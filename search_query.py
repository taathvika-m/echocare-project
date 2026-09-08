import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from rag_utils import get_embedding

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

def hybrid_search(question, top_k=2):
    query_vector = get_embedding(client, question)
    vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=top_k, fields="content_vector")

    results = search_client.search(
        search_text=question,
        vector_queries=[vector_query],
        top=top_k
    )
    return [r["content"] for r in results]

if __name__ == "__main__":
    question = "what should I do if I fall?"
    results = hybrid_search(question)
    print(f"=== HYBRID SEARCH RESULTS for '{question}' ===")
    for r in results:
        print(r)
        print("---")
