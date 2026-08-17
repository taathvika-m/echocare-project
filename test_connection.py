from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
    azure_endpoint="https://oai-echocare-b9328.openai.azure.com/",
    azure_ad_token=token.token,
    api_version="2024-10-21",
)

response = client.chat.completions.create(
    model="gpt-4-1-deployment",
    messages=[
        {"role": "system", "content": "You are EchoCare, a warm daily check-in companion for an older adult living alone."},
        {"role": "user", "content": "Good morning! Please greet me and ask how I'm feeling today."}
    ]
)
print(response.choices[0].message.content)
