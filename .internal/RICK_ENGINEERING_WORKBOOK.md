# CareNav Azure Cloud Migration Guide

**ChromaDB -> Azure AI Search | SQLite -> Microsoft Fabric | React -> Azure Web App**

**Version 1.0 | Gregory Katz | Microsoft Corporation**

Built by Gregory Katz and Rick Weyenberg. Code is as-is, open source.

---

## 0. Migration Overview

This document provides complete step-by-step instructions to migrate CareNav from its local development stack to a production-ready Azure architecture. The migration covers three major infrastructure changes: replacing ChromaDB with Azure AI Search (fully loaded indexes), replacing SQLite with Microsoft Fabric (Lakehouse + SQL Analytics), and deploying the React frontend as an Azure Static Web App with the FastAPI backend on Azure App Service.

### 0.1 Prerequisites

- Azure subscription with Owner or Contributor role on target Resource Group
- Microsoft Fabric capacity (F4 minimum recommended; F2 for dev/test)
- Azure OpenAI resource with embedding model deployed
- GitHub repo: gregnatkatz/carenav with MAIN1 branch
- Azure CLI installed and authenticated (az login)
- Node.js 18+ and Python 3.11+ on your local machine
- Git configured with access to the repo

### 0.2 Estimated Timeline

| Phase | Estimated Time |
|-------|----------------|
| Phase 1: Azure AI Search setup + index migration | 2-3 hours |
| Phase 2: Microsoft Fabric + data migration | 2-3 hours |
| Phase 3: Backend deployment to App Service | 1-2 hours |
| Phase 4: Frontend deployment to Static Web Apps | 1 hour |
| Phase 5: Configuration, secrets, smoke testing | 1-2 hours |
| **Total** | **7-11 hours (first time); ~2 hours subsequent deploys** |

### 0.3 Architecture Summary

| Component | Change |
|-----------|--------|
| Vector Store | ChromaDB (local) -> Azure AI Search (fully loaded indexes) |
| Relational DB | SQLite (local file) -> Microsoft Fabric SQL Analytics Endpoint |
| Frontend Hosting | Local dev server -> Azure Static Web Apps |
| Backend Hosting | Local uvicorn -> Azure App Service (Python) |
| Secrets / Config | Local .env -> Azure Key Vault + App Settings |
| Embeddings | Local model or OpenAI -> Azure OpenAI (text-embedding-ada-002 or text-embedding-3-large) |
| CI/CD | None -> GitHub Actions (auto-deploy on push to MAIN1) |

---

## 1. Create Core Azure Resources

All CareNav resources should live in a single Resource Group for easy management and cost tracking.

### 1.1 Set Up Resource Group and Variables

```bash
export RG="rg-carenav-prod"
export LOCATION="eastus2"
export SEARCH_SVC="carenav-search"
export APP_SVC_PLAN="carenav-plan"
export BACKEND_APP="carenav-api"
export STATIC_APP="carenav-web"
export KV_NAME="carenav-kv"

az group create --name $RG --location $LOCATION
```

### 1.2 Create Azure Key Vault

```bash
az keyvault create --name $KV_NAME --resource-group $RG --location $LOCATION --enable-rbac-authorization true
```

---

## 2. Azure AI Search - Replacing ChromaDB

### 2.1 Create the Azure AI Search Service

```bash
az search service create --name $SEARCH_SVC --resource-group $RG --location $LOCATION --sku Standard --partition-count 1 --replica-count 1

az search admin-key show --service-name $SEARCH_SVC --resource-group $RG
```

NOTE: Standard SKU supports vector search. Basic SKU does NOT support vector fields.

### 2.2 Understand Your ChromaDB Schema

```python
import chromadb
client = chromadb.PersistentClient(path='./chroma_db')
for col in client.list_collections():
    print(f'Collection: {col.name}, Count: {col.count()}')
```

### 2.3 Create the Azure AI Search Index

```python
# File: scripts/create_search_index.py
import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    SimpleField, SearchableField, VectorSearch,
    HnswAlgorithmConfiguration, VectorSearchProfile
)
from azure.core.credentials import AzureKeyCredential

SEARCH_ENDPOINT = os.environ['AZURE_SEARCH_ENDPOINT']
SEARCH_KEY = os.environ['AZURE_SEARCH_KEY']
INDEX_NAME = 'carenav-docs'
EMBEDDING_DIM = 1536

client = SearchIndexClient(SEARCH_ENDPOINT, AzureKeyCredential(SEARCH_KEY))

fields = [
    SimpleField(name='id', type=SearchFieldDataType.String, key=True),
    SearchableField(name='content', type=SearchFieldDataType.String),
    SimpleField(name='source', type=SearchFieldDataType.String, filterable=True),
    SimpleField(name='category', type=SearchFieldDataType.String, filterable=True),
    SearchField(name='content_vector', type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=EMBEDDING_DIM, vector_search_profile_name='hnsw-profile')
]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name='hnsw-algo')],
    profiles=[VectorSearchProfile(name='hnsw-profile', algorithm_configuration_name='hnsw-algo')]
)

index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
result = client.create_or_update_index(index)
print(f'Index created: {result.name}')
```

### 2.4 Migrate ChromaDB Data to Azure AI Search

```python
# File: scripts/migrate_chromadb_to_search.py
import os, chromadb
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

SEARCH_ENDPOINT = os.environ['AZURE_SEARCH_ENDPOINT']
SEARCH_KEY = os.environ['AZURE_SEARCH_KEY']
INDEX_NAME = 'carenav-docs'

search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))
chroma_client = chromadb.PersistentClient(path='./chroma_db')

for collection in chroma_client.list_collections():
    col = chroma_client.get_collection(collection.name)
    batch = col.get(include=['embeddings', 'documents', 'metadatas'])
    docs = [{'id': batch['ids'][i], 'content': batch['documents'][i], 'content_vector': batch['embeddings'][i]} for i in range(len(batch['ids']))]
    search_client.upload_documents(documents=docs)
```

### 2.5 Update Python Backend - Search Client

```python
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

search_client = SearchClient(endpoint=os.environ['AZURE_SEARCH_ENDPOINT'], index_name='carenav-docs', credential=AzureKeyCredential(os.environ['AZURE_SEARCH_KEY']))

vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=50, fields='content_vector')
results = search_client.search(search_text=user_query, vector_queries=[vector_query], top=5)
```

### 2.6 Update requirements.txt

```
azure-search-documents>=11.4.0
azure-identity>=1.15.0
azure-keyvault-secrets>=4.7.0
```

---

## 3. Microsoft Fabric - Replacing SQLite

### 3.1 Set Up Microsoft Fabric Workspace

1. Sign in to app.fabric.microsoft.com
2. Click Workspaces -> New workspace. Name it CareNav-Prod.
3. Under Advanced settings, assign a Fabric capacity (F4+).

### 3.2 Create a Lakehouse

1. Inside CareNav-Prod workspace, click + New -> Lakehouse.
2. Name it carenav_lakehouse.
3. Note the SQL Analytics Endpoint connection string.

### 3.3 Export SQLite Data

```python
import sqlite3, csv, os
DB_PATH = './carenav.db'
EXPORT_DIR = './sqlite_export'
os.makedirs(EXPORT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    with open(f'{EXPORT_DIR}/{table}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        writer.writerows(rows)
conn.close()
```

### 3.4 Upload CSVs to Fabric Lakehouse

1. In Fabric Lakehouse, click Files.
2. Create folder uploads/sqlite_export.
3. Drag and drop all CSV files.

### 3.5 Create Delta Tables from CSVs

```python
# Fabric Notebook
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

files = mssparkutils.fs.ls('Files/uploads/sqlite_export/')
for f in files:
    if f.name.endswith('.csv'):
        table_name = f.name.replace('.csv', '')
        df = spark.read.csv(f.path, header=True, inferSchema=True)
        df.write.format('delta').mode('overwrite').saveAsTable(table_name)
```

### 3.6 Update Python Backend - Database Connection

```python
import pyodbc, os

FABRIC_SERVER = os.environ['FABRIC_SQL_SERVER']
FABRIC_DATABASE = os.environ['FABRIC_SQL_DATABASE']
FABRIC_USERNAME = os.environ['FABRIC_SQL_USERNAME']
FABRIC_PASSWORD = os.environ['FABRIC_SQL_PASSWORD']

conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={FABRIC_SERVER};DATABASE={FABRIC_DATABASE};UID={FABRIC_USERNAME};PWD={FABRIC_PASSWORD};Encrypt=yes;'

def get_db():
    return pyodbc.connect(conn_str)
```

### 3.7 Create Service Principal for Fabric Access

```bash
az ad sp create-for-rbac --name carenav-fabric-sp --output json
az keyvault secret set --vault-name $KV_NAME --name fabric-sql-username --value '<appId>@<tenant>'
az keyvault secret set --vault-name $KV_NAME --name fabric-sql-password --value '<password>'
```

---

## 4. Azure App Service - FastAPI Backend

### 4.1 Create App Service Plan and Web App

```bash
az appservice plan create --name $APP_SVC_PLAN --resource-group $RG --location $LOCATION --is-linux --sku B2
az webapp create --name $BACKEND_APP --resource-group $RG --plan $APP_SVC_PLAN --runtime "PYTHON:3.11"
az webapp identity assign --name $BACKEND_APP --resource-group $RG
```

### 4.2 Grant App Service Access to Key Vault

```bash
PRINCIPAL_ID=$(az webapp identity show --name $BACKEND_APP --resource-group $RG --query principalId -o tsv)
KV_ID=$(az keyvault show --name $KV_NAME --resource-group $RG --query id -o tsv)
az role assignment create --role 'Key Vault Secrets User' --assignee $PRINCIPAL_ID --scope $KV_ID
```

### 4.3 Store All Secrets in Key Vault

```bash
az keyvault secret set --vault-name $KV_NAME --name azure-search-endpoint --value 'https://<svc>.search.windows.net'
az keyvault secret set --vault-name $KV_NAME --name azure-search-key --value '<key>'
az keyvault secret set --vault-name $KV_NAME --name azure-openai-endpoint --value 'https://<aoi>.openai.azure.com/'
az keyvault secret set --vault-name $KV_NAME --name azure-openai-key --value '<key>'
```

### 4.4 Configure App Service Application Settings

```bash
KV_URI="https://${KV_NAME}.vault.azure.net"
az webapp config appsettings set --name $BACKEND_APP --resource-group $RG --settings AZURE_SEARCH_ENDPOINT="@Microsoft.KeyVault(SecretUri=${KV_URI}/secrets/azure-search-endpoint/)" WEBSITES_PORT=8000
```

### 4.5 Create startup.sh

```bash
#!/bin/bash
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120
```

### 4.6 Add GitHub Actions for Backend CI/CD

Create .github/workflows/deploy-backend.yml with azure/webapps-deploy@v3 action.

---

## 5. Azure Static Web Apps - React Frontend

### 5.1 Create the Static Web App

```bash
az staticwebapp create --name $STATIC_APP --resource-group $RG --location "eastus2" --source https://github.com/gregnatkatz/carenav --branch MAIN1 --app-location "/frontend" --output-location "dist" --login-with-github
```

### 5.2 Update React API Base URL

```bash
# frontend/.env.production
VITE_API_URL=https://carenav-api.azurewebsites.net
```

### 5.3 Configure CORS on FastAPI Backend

```python
from fastapi.middleware.cors import CORSMiddleware
origins = ['https://carenav-web.azurestaticapps.net', 'http://localhost:5173']
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
```

---

## 6. Final Configuration and Smoke Testing

### 6.1 Environment Variable Checklist

| Variable | Source | Required For |
|----------|--------|--------------|
| AZURE_SEARCH_ENDPOINT | Key Vault | Vector search |
| AZURE_SEARCH_KEY | Key Vault | Vector search |
| AZURE_OPENAI_ENDPOINT | Key Vault | Embeddings |
| AZURE_OPENAI_KEY | Key Vault | Embeddings |
| FABRIC_SQL_SERVER | Key Vault | Database |
| FABRIC_SQL_DATABASE | Key Vault | Database |

### 6.2 Smoke Tests

```bash
# Azure AI Search
curl -X POST 'https://<svc>.search.windows.net/indexes/carenav-docs/docs/search?api-version=2023-11-01' -H 'api-key: <key>' -d '{"search": "medication"}'

# Backend API
curl https://carenav-api.azurewebsites.net/health

# Frontend - Navigate to https://carenav-web.azurestaticapps.net
```

---

## 7. Common Issues and Troubleshooting

| Issue | Resolution |
|-------|------------|
| App Service shows 'Application Error' | Check logs: az webapp log tail --name carenav-api --resource-group rg-carenav-prod |
| Key Vault secret not resolving | Verify Managed Identity has Key Vault Secrets User role |
| CORS error from frontend | Add exact Static Web App URL to FastAPI CORS origins |
| Search returns no results | Run migration script again and verify document count |

---

## 8. Post-Migration Cleanup

```bash
echo 'chroma_db/' >> .gitignore
echo '*.db' >> .gitignore
git rm -r --cached chroma_db/ 2>/dev/null || true
git commit -m 'chore: remove local data artifacts post-migration'
```

### Cost Optimization

- Azure AI Search Standard: ~$245/month
- App Service B2: ~$73/month
- Static Web Apps: Free
- Fabric: Billed per capacity unit-hour

---

## Questions?

Reach Gregory at gregory.katz@microsoft.com or Teams.

---

**Built by Gregory Katz and Rick Weyenberg**
**CareNav Florida - GitHub Copilot SDK Enterprise Challenge**
**Submission Deadline: March 7, 2026 at 10 PM PST**

