import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchField, SearchFieldDataType,
    VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration
)

load_dotenv()

index_client = SearchIndexClient(
    endpoint=os.environ["SEARCH_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["SEARCH_KEY"])
)

index_name = "echocare-care-plan"

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="default-profile"
    )
]

vector_search = VectorSearch(
    profiles=[VectorSearchProfile(name="default-profile", algorithm_configuration_name="default-algo")],
    algorithms=[HnswAlgorithmConfiguration(name="default-algo")]
)

index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
index_client.create_or_update_index(index)
print(f"Index '{index_name}' created successfully")
