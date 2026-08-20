import json
from datetime import datetime
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
    azure_endpoint="https://oai-echocare-b9328.openai.azure.com/",
    azure_ad_token=token.token,
    api_version="2024-10-21",
)

PERSON_NAME = "Margaret"

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
                    "date_orientation_correct": {
                        "type": "boolean",
                        "description": "Whether the person correctly stated today's day/date when asked"
                    },
                    "notable_quotes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Any specific phrases worth remembering verbatim, e.g. repeated concerns"
                    },
                    "immediate_concern": {
                        "type": "boolean",
                        "description": "True if the person mentioned a new physical symptom (pain, dizziness, headache, falls) or expressed acute confusion/disorientation beyond just not knowing the date"
                    },
                    "immediate_concern_detail": {
                        "type": "string",
                        "description": "If immediate_concern is true, describe exactly what they said, in their words"
                    }
                },
                "required": ["mood_summary", "took_medication", "date_orientation_correct"]
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
        print(f"\n⚠️  IMMEDIATE CONCERN FLAGGED: {immediate_concern_detail}")
    return {"status": "saved"}

system_prompt = f"""You are EchoCare, a warm daily check-in companion for {PERSON_NAME}, an older adult living alone.

Your job this conversation:
1. Greet them warmly and ask how they're feeling today
2. Ask if they've taken their medication today — if their answer is unclear or uncertain, gently ask a clarifying follow-up. Do not guess.
3. Ask what day of the week it is today, naturally. If they genuinely don't know, that's OK — don't press repeatedly, just note it.
4. IMPORTANT: if they mention any new physical symptom (headache, dizziness, pain, a fall) or express acute confusion ("I don't remember what's happening"), gently ask one follow-up to understand it better before ending the call — this matters more than finishing the routine questions.
5. Once you have what you need, call save_checkin, setting immediate_concern to true if step 4 applied. If immediate_concern applies, do NOT call save_checkin until the person has actually answered your follow-up question about the symptom - a one-word non-answer like "yes" does not count as an answer. Ask again more specifically if needed.

Keep your responses short and warm, like a caring friend on the phone — not clinical or robotic."""

conversation = [{"role": "system", "content": system_prompt}]

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
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
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
