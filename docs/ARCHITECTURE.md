# CareNav Florida - System Architecture

## Overview

CareNav Florida is a multi-agent AI system that helps families navigate elder care decisions in Florida. The system uses specialized AI agents coordinated by an orchestrator to provide comprehensive guidance on Medicaid eligibility, VA benefits, facility selection, and legal considerations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Executive  │  │   Intake    │  │    Chat     │  │     Documents       │ │
│  │   Summary   │  │   Wizard    │  │    Panel    │  │        Tab          │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ REST API
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           API Routers                                    ││
│  │  /patients  /chat  /eligibility  /facilities  /documents  /tasks        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         LLM Service Layer                                ││
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐  ││
│  │  │ LLMProvider     │    │AzureOpenAI      │    │CopilotSDK           │  ││
│  │  │ (Abstract)      │◄───│Provider         │    │Provider (Placeholder)│  ││
│  │  └─────────────────┘    └─────────────────┘    └─────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                          Agent System                                    ││
│  │                     ┌─────────────────┐                                  ││
│  │                     │   Orchestrator  │                                  ││
│  │                     │     Agent       │                                  ││
│  │                     └────────┬────────┘                                  ││
│  │         ┌───────────┬───────┼───────┬───────────┐                       ││
│  │         ▼           ▼       ▼       ▼           ▼                       ││
│  │  ┌───────────┐ ┌─────────┐ ┌─────┐ ┌─────────┐ ┌──────────┐            ││
│  │  │Eligibility│ │Facility │ │Legal│ │Validator│ │Summarizer│            ││
│  │  │  Agent    │ │ Agent   │ │Agent│ │  Agent  │ │  Agent   │            ││
│  │  └───────────┘ └─────────┘ └─────┘ └─────────┘ └──────────┘            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                          Data Layer                                      ││
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐  ││
│  │  │  Azure SQL DB   │    │ Azure AI Search │    │  Demo Documents     │  ││
│  │  │   (Patients,    │    │   (Vector +     │    │    Service          │  ││
│  │  │    Tasks, Docs) │    │    Semantic)    │    │                     │  ││
│  │  └─────────────────┘    └─────────────────┘    └─────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ MCP Protocol
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP Servers (Future)                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Medicaid   │  │ VA Benefits │  │  Facility   │  │    Document RAG     │ │
│  │   Server    │  │   Server    │  │   Server    │  │       Server        │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (React + TypeScript)

The frontend is a single-page application built with React 18 and TypeScript. Key components:

| Component | Purpose |
|-----------|---------|
| `ExecutiveSummary` | Dashboard showing patient status, tasks, and key metrics |
| `IntakeWizard` | 10-step wizard for patient intake with validation |
| `ChatPanel` | AI chat interface with rich formatted responses |
| `DocumentsTab` | Document viewer with category filtering and full content modal |

**Technology Stack:**
- React 18 with hooks
- TypeScript for type safety
- Tailwind CSS for styling (Vision UI dark theme)
- Vite for build tooling
- shadcn/ui for UI components

### Backend (FastAPI + Python)

The backend is a REST API built with FastAPI. Key modules:

| Module | Purpose |
|--------|---------|
| `routers/` | API endpoints for patients, chat, eligibility, facilities, documents, tasks |
| `agents/` | 6 specialized AI agents (orchestrator, eligibility, facility, legal, validator, summarizer) |
| `services/` | LLM abstraction layer, Azure OpenAI, knowledge base, demo documents |
| `models/` | SQLAlchemy models for database entities |

**Technology Stack:**
- Python 3.11
- FastAPI for REST API
- SQLAlchemy for ORM
- Azure SQL Database (target) / SQLite (local dev)
- Azure AI Search (target) / ChromaDB (local dev)
- Poetry for dependency management

### LLM Service Abstraction Layer

The `llm_service.py` module provides a clean abstraction for LLM interactions:

```python
# Abstract base class
class LLMProvider(ABC):
    async def chat_completion(messages, temperature, max_tokens, response_format) -> dict
    async def chat_completion_json(messages, temperature, max_tokens) -> dict
    async def get_embedding(text) -> list[float]
    async def chat_completion_stream(messages, temperature) -> AsyncIterator[str]

# Implementations
class AzureOpenAIProvider(LLMProvider)  # Current implementation
class CopilotSDKProvider(LLMProvider)   # Placeholder for SDK integration

# Factory function
def get_llm_provider() -> LLMProvider:
    provider_type = "azure"  # Change to "copilot_sdk" for SDK integration
    ...
```

**To switch providers:** Change `provider_type = "copilot_sdk"` in `get_llm_provider()`.

### Agent System

The agent system follows a coordinator pattern where the Orchestrator routes queries to specialist agents:

```
User Query
    │
    ▼
┌─────────────────┐
│   Orchestrator  │ ─── Analyzes query, determines routing
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┬────────┐
    ▼         ▼        ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌─────┐ ┌────────┐ ┌──────────┐
│Eligib. │ │Facility│ │Legal│ │Validat.│ │Summarizer│
└────────┘ └────────┘ └─────┘ └────────┘ └──────────┘
    │         │        │        │        │
    └─────────┴────────┴────────┴────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Orchestrator  │ ─── Synthesizes responses
              └────────┬────────┘
                       │
                       ▼
                 Final Response
```

**Agent Responsibilities:**

| Agent | Responsibility |
|-------|----------------|
| Orchestrator | Routes queries, synthesizes responses, maintains conversation context |
| Eligibility | Medicaid ICP, VA A&A, Medicare eligibility calculations |
| Facility | Care facility search, comparison, admission requirements |
| Legal | Spend-down strategies, asset protection, deceased spouse debt |
| Validator | Cross-validates recommendations for accuracy and compliance |
| Summarizer | Creates plain-English summaries and action plans |

### Data Layer

**SQLite Database Schema:**

```sql
-- Patients table
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    ssn TEXT,
    assets REAL,
    monthly_income REAL,
    marital_status TEXT,
    veteran_status TEXT,
    care_level_needed TEXT,
    created_at TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    title TEXT,
    category TEXT,
    content TEXT,
    document_date DATE,
    created_at TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    title TEXT,
    description TEXT,
    status TEXT,
    priority TEXT,
    due_date DATE,
    completed_at TIMESTAMP
);
```

**Azure AI Search (Target) / ChromaDB (Local Dev):**

Used for semantic search over patient documents. Embeddings are generated using Azure OpenAI's text-embedding-3-large model. For enterprise deployment, Azure AI Search provides hybrid vector + semantic search with Foundry IQ for agentic retrieval.

### MCP Servers (Future)

Four MCP servers are defined in `mcp.json` for GitHub Copilot SDK integration:

| Server | Tools |
|--------|-------|
| `medicaid` | check_medicaid_eligibility, get_medicaid_rules, calculate_spend_down, check_look_back_violations |
| `va_benefits` | check_va_eligibility, calculate_va_benefit, get_required_documents |
| `facility_search` | search_facilities, compare_facilities, check_admission_requirements |
| `document_rag` | search_documents, get_document, list_documents, summarize_documents |

## Data Flow

### Chat Request Flow

```
1. User sends message via ChatPanel
2. Frontend POSTs to /api/chat
3. Chat router receives request
4. Orchestrator agent analyzes query
5. Orchestrator routes to relevant specialist(s)
6. Specialist agent(s) process with LLM
7. Validator checks recommendations
8. Summarizer formats response
9. Orchestrator returns final response
10. Frontend renders rich formatted response
```

### Patient Intake Flow

```
1. User completes IntakeWizard steps
2. Frontend POSTs to /api/patients
3. Patient router creates patient record
4. Demo documents service generates documents
5. Knowledge base indexes documents (if ChromaDB enabled)
6. Frontend redirects to ExecutiveSummary
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
┌─────────────────────────────┐  ┌─────────────────────────────────┐
│    Static Web Hosting       │  │         Fly.io                   │
│  (Vercel/Netlify/Azure)     │  │    (Backend Hosting)             │
│                             │  │                                  │
│  [Your frontend URL]        │  │  [Your backend URL]              │
│                             │  │                                  │
│                             │  │  ┌─────────────────────────────┐│
│  ┌─────────────────────┐    │  │  │     FastAPI Application     ││
│  │   React SPA         │    │  │  │                             ││
│  │   (Vite Build)      │────┼──┼─▶│  - REST API                 ││
│  └─────────────────────┘    │  │  │  - Agent System             ││
│                             │  │  │  - SQLite Database          ││
└─────────────────────────────┘  │  └─────────────────────────────┘│
                                 │                                  │
                                 │  ┌─────────────────────────────┐│
                                 │  │   Azure OpenAI              ││
                                 │  │   (LLM Provider)            ││
                                 │  │                             ││
                                 │  │   ahfy26-resource.          ││
                                 │  │   cognitiveservices.        ││
                                 │  │   azure.com                 ││
                                 │  └─────────────────────────────┘│
                                 └─────────────────────────────────┘
```

## Security Considerations

1. **API Security**: CORS configured for specific origins
2. **Data Privacy**: Patient data stored locally, not transmitted to third parties except LLM
3. **LLM Privacy**: System prompts instruct LLM not to store or learn from patient data
4. **Authentication**: Currently demo mode; production would add OAuth/JWT

## Scalability Considerations

1. **Database**: SQLite for local dev; Azure SQL Database for enterprise
2. **Vector Search**: ChromaDB for local dev; Azure AI Search + Foundry IQ for enterprise
3. **LLM**: Azure OpenAI scales automatically; rate limiting may be needed
4. **Caching**: Add Redis for frequently accessed data in production

## Azure AI Foundry Integration

CareNav Florida is designed to leverage Azure AI Foundry for advanced AI capabilities:

**Current Integration Points:**
- Model deployment and versioning through Foundry projects
- Centralized model management across development and production
- Usage analytics and cost tracking
- Model evaluation and testing pipelines

**Configuration:**
```bash
AZURE_AI_FOUNDRY_ENDPOINT=https://your-foundry.services.ai.azure.com/api/projects/your-project
AZURE_AI_FOUNDRY_API_KEY=your-foundry-key-here
```

Azure AI Foundry provides the enterprise governance layer for managing AI models at scale, enabling health systems to maintain compliance and auditability requirements.

## Future Enhancements

1. **GitHub Copilot SDK Integration**: Replace Azure OpenAI with Copilot SDK
2. **MCP Server Implementation**: Implement the 4 MCP servers defined in mcp.json
3. **Real Facility Data**: Integrate with AHCA facility database
4. **Document OCR**: Add OCR for uploaded documents
5. **Multi-tenant**: Add organization/user management
