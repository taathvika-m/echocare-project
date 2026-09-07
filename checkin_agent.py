import json
from datetime import datetime
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from rag_utils import CarePlanIndex

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
    azure_endpoint="https://oai-echocare-b9328.openai.azure.com/",
    azure_ad_token=token.token,
    api_version="2024-10-21",
)

PERSON_NAME = "Margaret"
MAX_CONCERN_RETRIES = 3

print("Loading care plan index...")
care_plan_index = CarePlanIndex(client)
print("Ready.\n")

tools = [
    {
        "type": "function",
        "function": {
            "name": "save_checkin",
            "description": "Save the completed check-in ONLY once you have clearly established the person's "
                            "mood and whether they took their medication. If medication status is unclear or "
                            "they seem unsure, ask a follow-up question instead of calling this function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mood_summary": {"type": "string"},
                    "took_medication": {"type": "boolean"},
                    "date_orientation_correct": {"type": "boolean"},
                    "notable_quotes": {"type": "array", "items": {"type": "string"}},
                    "immediate_concern": {"type": "boolean"},
                    "immediate_concern_detail": {"type": "string"}
                },
                "required": ["mood_summary", "took_medication", "date_orientation_correct"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_care_plan",
            "description": "Look up information from the person's actual care plan and medication schedule "
                            "when they ask a question about their medications, dosages, timing, or emergency "
                            "guidance. ALWAYS use this instead of answering from general knowledge.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The specific question to look up"}
                },
                "required": ["question"]
            }
        }
    }
]

def save_checkin(mood_summary, took_medication, date_orientation_correct, notable_quotes=None,
                  immediate_concern=False, immediate_concern_detail=None):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "person_name": PERSON_NAME,
        "mood_summary": mood_summary,
        "took_medication": took_medication,
        "date_orientation_correct": date_orientation_correct,
        "notable_quotes": notable_quotes or [],
        "immediate_concern": immediate_concern,
        "immediate_concern_detail": immediate_concern_detail
    }
    with open("checkins.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
    if immediate_concern:
        print(f"\n IMMEDIATE CONCERN FLAGGED: {immediate_concern_detail}")
    return {"status": "saved"}

def lookup_care_plan(question):
    context = care_plan_index.retrieve(question)
    return {"retrieved_context": context}

def concern_detail_is_adequate(detail, transcript_so_far):
    judge_response = client.chat.completions.create(
        model="gpt-4-1-deployment",
        messages=[
            {"role": "system", "content": "You judge whether enough is known about a reported health symptom. "
                                            "Answer with ONLY 'yes' or 'no'. Say yes only if severity AND "
                                            "whether it's new/unusual are both reasonably clear."},
            {"role": "user", "content": f"Conversation so far:\n{transcript_so_far}\n\n"
                                          f"Concern detail captured: '{detail}'\n\nIs this adequate? yes or no."}
        ]
    )
    return judge_response.choices[0].message.content.strip().lower().startswith("yes")

system_prompt = f"""You are EchoCare, a warm daily check-in companion for {PERSON_NAME}, an older adult living alone.

1. Greet them warmly and ask how they're feeling today
2. Ask if they've taken their medication today. If unclear, ask a follow-up. Do not guess.
3. Ask what day of the week it is. If they don't know, that's OK, don't press.
4. If they mention a new symptom or acute confusion, ask about severity and whether it's new before moving on.
5. If they ask ANY question about their medications, dosages, or what to do in a situation, use lookup_care_plan
   to answer accurately from their real records - never answer from general knowledge.
6. Once ready, call save_checkin."""

conversation = [{"role": "system", "content": system_prompt}]
concern_retry_count = 0

print("=== EchoCare Check-In (type 'quit' to end) ===\n")

while True:
    response = client.chat.completions.create(
        model="gpt-4-1-deployment",
        messages=conversation,
        tools=tools,
        tool_choice="auto"
    )
    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        fn_name = tool_call.function.name

        if fn_name == "lookup_care_plan":
            result = lookup_care_plan(**args)
            conversation.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
            continue

        if fn_name == "save_checkin":
            if args.get("immediate_concern") and concern_retry_count < MAX_CONCERN_RETRIES:
                transcript_so_far = "\n".join(
                    f"{m['role']}: {m['content']}" for m in conversation if m.get("content")
                )
                if not concern_detail_is_adequate(args.get("immediate_concern_detail", ""), transcript_so_far):
                    concern_retry_count += 1
                    print(f"\n[System: concern detail inadequate (attempt {concern_retry_count}/{MAX_CONCERN_RETRIES}), forcing follow-up]")
                    conversation.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": "REJECTED: not enough detail on severity or whether this is new. Ask again."
                    })
                    continue

            result = save_checkin(**args)
            print(f"\n[Check-in saved: {result}]")
            break

    print(f"EchoCare: {message.content}")
    conversation.append({"role": "assistant", "content": message.content})

    user_input = input(f"\n{PERSON_NAME}: ")
    if user_input.lower() == "quit":
        print("Ending check-in early.")
        break

    conversation.append({"role": "user", "content": user_input})
