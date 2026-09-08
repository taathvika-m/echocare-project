import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from rag_utils import chunk_document, get_embedding

load_dotenv()

search_client = SearchClient(
    endpoint=os.environ["SEARCH_ENDPOINT"],
    index_name="echocare-care-plan",
    credential=AzureKeyCredential(os.environ["SEARCH_KEY"])
)

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")
client = AzureOpenAI(
    azure_endpoint="https://oai-echocare-b9328.openai.azure.com/",
    azure_ad_token=token.token,
    api_version="2024-10-21",
)

with open("care_plan.txt") as f:
    text = f.read()

chunks = chunk_document(text)
documents = []
for i, chunk in enumerate(chunks):
    embedding = get_embedding(client, chunk)
    documents.append({
        "id": str(i),
        "content": chunk,
        "source": "care_plan.txt",
        "content_vector": embedding
    })

result = search_client.upload_documents(documents)
print(f"Uploaded {len(documents)} chunks to Azure AI Search")
