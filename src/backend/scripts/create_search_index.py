"""
Create Azure AI Search Index for CareNav Florida
==================================================
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source

Run after provisioning Azure AI Search:
    python scripts/create_search_index.py

Then seed with documents using the export endpoint:
    curl http://localhost:8000/api/knowledge/export/azure-search/ | \
    python scripts/seed_search_index.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# TODO: Rick — Uncomment after installing azure-search-documents
#
# from azure.search.documents.indexes import SearchIndexClient
# from azure.search.documents.indexes.models import (
#     SearchIndex,
#     SearchField,
#     SearchFieldDataType,
#     SimpleField,
#     SearchableField,
#     VectorSearch,
#     HnswAlgorithmConfiguration,
#     VectorSearchProfile,
#     SemanticConfiguration,
#     SemanticSearch,
#     SemanticPrioritizedFields,
#     SemanticField,
# )
# from azure.core.credentials import AzureKeyCredential
#
#
# def create_index():
#     client = SearchIndexClient(
#         endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
#         credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY")),
#     )
#
#     fields = [
#         SimpleField(name="id", type=SearchFieldDataType.String, key=True),
#         SimpleField(name="patient_id", type=SearchFieldDataType.String, filterable=True),
#         SearchableField(name="title", type=SearchFieldDataType.String),
#         SearchableField(name="content", type=SearchFieldDataType.String),
#         SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
#         SimpleField(name="document_date", type=SearchFieldDataType.String, sortable=True),
#         SearchField(
#             name="content_vector",
#             type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
#             searchable=True,
#             vector_search_dimensions=3072,  # text-embedding-3-large
#             vector_search_profile_name="carenav-vector-profile",
#         ),
#     ]
#
#     vector_search = VectorSearch(
#         algorithms=[HnswAlgorithmConfiguration(name="carenav-hnsw")],
#         profiles=[VectorSearchProfile(
#             name="carenav-vector-profile",
#             algorithm_configuration_name="carenav-hnsw",
#         )],
#     )
#
#     semantic_config = SemanticConfiguration(
#         name="carenav-semantic",
#         prioritized_fields=SemanticPrioritizedFields(
#             title_field=SemanticField(field_name="title"),
#             content_fields=[SemanticField(field_name="content")],
#         ),
#     )
#
#     semantic_search = SemanticSearch(configurations=[semantic_config])
#
#     index = SearchIndex(
#         name=os.getenv("AZURE_SEARCH_INDEX", "carenav-documents"),
#         fields=fields,
#         vector_search=vector_search,
#         semantic_search=semantic_search,
#     )
#
#     result = client.create_or_update_index(index)
#     print(f"Created index: {result.name}")
#
#
# if __name__ == "__main__":
#     create_index()

print("TODO: Uncomment after installing azure-search-documents")
print("pip install azure-search-documents azure-core")
