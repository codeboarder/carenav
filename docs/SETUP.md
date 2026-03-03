# CareNav Florida - Setup Guide

This guide covers development environment setup, local running, and deployment for CareNav Florida.

## Prerequisites

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend build tools
- **Poetry** - Python dependency management
- **npm** - Node.js package manager
- **Git** - Version control

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/gregorykatz/carenav-florida.git
cd carenav-florida
```

### 2. Backend Setup

```bash
cd src/backend

# Install dependencies
poetry install

# Create .env file
cat > .env << EOF
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
MODEL_GPT_5_2=gpt-5.2
MODEL_GPT_5_NANO=gpt-5-nano
MODEL_EMBEDDING=text-embedding-ada-002
DATABASE_URL=sqlite+aiosqlite:///./carenav.db
EOF

# Run database migrations (creates tables)
poetry run python -c "from app.config import get_settings; from app.models.database import init_db; import asyncio; asyncio.run(init_db(get_settings().resolve_database_url()))"

# Create demo patient (Margaret Thompson)
poetry run python scripts/create_demo.py

# Start the backend server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at http://localhost:8000

### 3. Frontend Setup

```bash
cd src/frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000
EOF

# Start the development server
npm run dev
```

The frontend will be available at http://localhost:5173

## Environment Variables

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | `https://your-resource.cognitiveservices.azure.com/` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-02-15-preview` |
| `MODEL_GPT_5_2` | Primary model deployment name | `gpt-5.2` |
| `MODEL_GPT_5_NANO` | Fast model deployment name | `gpt-5-nano` |
| `MODEL_EMBEDDING` | Embedding model deployment name | `text-embedding-ada-002` |
| `DATABASE_URL` | SQLAlchemy async DB URL (SQLite or Azure SQL) | `sqlite+aiosqlite:///./carenav.db` |
| `AZURE_SQL_SERVER` | Azure SQL server (optional if `DATABASE_URL` set) | `your-server.database.windows.net` |
| `AZURE_SQL_DATABASE` | Azure SQL database name | `carenav-db` |
| `AZURE_SQL_USERNAME` | Azure SQL username | `carenavadmin` |
| `AZURE_SQL_PASSWORD` | Azure SQL password | `***` |
| `AZURE_SQL_ODBC_DRIVER` | ODBC driver for Azure SQL | `ODBC Driver 18 for SQL Server` |
| `CHROMA_ENABLED` | Enable ChromaDB (optional) | `false` |

### Frontend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## Running Tests

### Backend Tests

```bash
cd src/backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_scenarios.py -v

# Run end-to-end tests
poetry run pytest tests/test_e2e_comprehensive.py -v
```

### Frontend Tests

```bash
cd src/frontend

# Run linting
npm run lint

# Type checking
npm run typecheck

# Build (checks for errors)
npm run build
```

## Deployment

### Backend Deployment (Fly.io)

```bash
cd src/backend

# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly
fly auth login

# Create app (first time only)
fly apps create carenav-backend

# Set secrets
fly secrets set AZURE_OPENAI_API_KEY=your_key
fly secrets set AZURE_OPENAI_ENDPOINT=your_endpoint

# Deploy
fly deploy
```

### Frontend Deployment (Static Hosting)

```bash
cd src/frontend

# Build for production
npm run build

# The dist/ folder can be deployed to any static hosting:
# - Vercel
# - Netlify
# - AWS S3 + CloudFront
# - Azure Static Web Apps
```

## GitHub Copilot SDK Integration

To integrate with GitHub Copilot SDK (Gregory's task):

### 1. Implement CopilotSDKProvider

Edit `src/backend/app/services/llm_service.py`:

```python
class CopilotSDKProvider(LLMProvider):
    def __init__(self):
        # Initialize Copilot SDK connection
        # Option 1: Use Copilot CLI in server mode
        # Option 2: Use Node.js sidecar process
        pass
    
    async def chat_completion(self, messages, temperature=0.7, max_tokens=4096, response_format=None):
        # Implement using Copilot SDK
        pass
    
    async def chat_completion_json(self, messages, temperature=0.3, max_tokens=4096):
        # Implement using Copilot SDK with JSON mode
        pass
    
    async def get_embedding(self, text):
        # Implement using Copilot SDK or Azure AI Search
        pass
```

### 2. Switch Provider

In `src/backend/app/services/llm_service.py`, change:

```python
def get_llm_provider() -> LLMProvider:
    provider_type = "copilot_sdk"  # Changed from "azure"
    ...
```

### 3. Register MCP Servers

The MCP servers are defined in `mcp.json`. Implement the server files:

```bash
src/backend/mcp_servers/
├── medicaid_server.py
├── va_benefits_server.py
├── facility_search_server.py
└── document_rag_server.py
```

### 4. Test Integration

```bash
# Run tests to verify SDK integration
poetry run pytest tests/test_sdk_integration.py -v
```

## Troubleshooting

### Common Issues

**1. Azure OpenAI 401 Unauthorized**
- Check that `AZURE_OPENAI_API_KEY` is correct
- Verify the endpoint URL matches your Azure resource

**2. Database not found**
- Run the database initialization command
- Check that `DATABASE_URL` path is correct

**3. Frontend can't connect to backend**
- Verify backend is running on port 8000
- Check `VITE_API_URL` in frontend .env
- Check CORS settings in backend

**4. ChromaDB memory issues**
- Set `CHROMA_ENABLED=false` in backend .env
- ChromaDB requires significant memory for ONNX model

### Getting Help

- Check the [GitHub Issues](https://github.com/gregorykatz/carenav-florida/issues)
- Review the [Architecture Documentation](ARCHITECTURE.md)
- Contact the development team

## Project Structure

```
carenav-florida/
├── AGENTS.md                    # Agent definitions
├── mcp.json                     # MCP server configuration
├── README.md                    # Project overview
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── agents/          # 6 AI agents
│   │   │   ├── models/          # Database models
│   │   │   ├── routers/         # API endpoints
│   │   │   ├── schemas/         # Pydantic schemas
│   │   │   ├── services/        # LLM service, knowledge base
│   │   │   ├── config.py        # Configuration
│   │   │   └── main.py          # FastAPI app
│   │   ├── mcp_servers/         # MCP server implementations
│   │   ├── scripts/             # Utility scripts
│   │   ├── tests/               # Backend tests
│   │   ├── pyproject.toml       # Python dependencies
│   │   └── poetry.lock
│   └── frontend/
│       ├── src/
│       │   ├── components/      # React components
│       │   ├── lib/             # API client, utilities
│       │   ├── App.tsx          # Main app component
│       │   └── main.tsx         # Entry point
│       ├── package.json         # Node dependencies
│       └── vite.config.ts       # Vite configuration
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md
│   ├── RAI_NOTES.md
│   ├── README.md
│   └── SETUP.md
├── demo/                        # Demo scripts
├── presentations/               # Presentation materials
└── tests/                       # Integration tests
```
