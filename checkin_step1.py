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

tools = [
    {
        "type": "function",
        "function": {
            "name": "save_checkin",
            "description": "Save today's check-in conversation transcript for this person.",
            "parameters": {
                "type": "object",
                "properties": {
                    "person_name": {"type": "string", "description": "Name of the person checking in"},
                    "mood_summary": {"type": "string", "description": "Brief summary of how they said they're feeling"},
                    "took_medication": {"type": "boolean", "description": "Whether they confirmed taking their medication"},
                    "full_transcript": {"type": "string", "description": "The full text of what they said"}
                },
                "required": ["person_name", "mood_summary", "took_medication", "full_transcript"]
            }
        }
    }
]

def save_checkin(person_name, mood_summary, took_medication, full_transcript):
    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "person_name": person_name,
        "mood_summary": mood_summary,
        "took_medication": took_medication,
        "full_transcript": full_transcript
    }
    with open("checkins_step1_test.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
    return {"status": "saved", "date": record["date"]}

person_response = "Hi, this is Margaret. I'm feeling pretty good today, a little tired. Yes, I took my morning pills already."

messages = [
    {"role": "system", "content": "You are EchoCare, a warm daily check-in companion for an older adult living alone. "
                                    "After hearing their response, call save_checkin to record it."},
    {"role": "user", "content": person_response}
]

response = client.chat.completions.create(
    model="gpt-4-1-deployment",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message

if message.tool_calls:
    for tool_call in message.tool_calls:
        print(f"Model wants to call: {tool_call.function.name}")
        args = json.loads(tool_call.function.arguments)
        print(f"With arguments: {args}")
        if tool_call.function.name == "save_checkin":
            result = save_checkin(**args)
            print(f"Function result: {result}")
else:
    print("Model responded with text instead of calling a tool:")
    print(message.content)
