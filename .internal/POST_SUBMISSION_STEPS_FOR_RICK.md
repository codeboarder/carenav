# CareNav Florida - Post-Submission Steps

**Attention: Rick Weyenberg**

This document outlines all the steps needed after the GitHub Copilot SDK Enterprise Challenge submission to get CareNav Florida running locally and integrated with the GitHub Copilot SDK.

## Step 1: Download the Repository

```bash
# Clone the repository
git clone https://github.com/gregnatkatz/carenav.git
cd carenav

# Switch to the main branch
git checkout MAIN1
```

## Step 2: Backend Setup

### 2.1 Install Python Dependencies

```bash
cd src/backend

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

### 2.2 Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Azure OpenAI credentials
# Required variables:
#   AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
#   AZURE_OPENAI_API_KEY=your-api-key
#   AZURE_OPENAI_API_VERSION=2024-12-01-preview
#   AZURE_OPENAI_DEPLOYMENT=gpt-5.2
```

### 2.3 Start the Backend Server

```bash
# From src/backend directory
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# The API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Step 3: Frontend Setup

### 3.1 Install Node Dependencies

```bash
cd src/frontend

# Install dependencies
npm install
```

### 3.2 Configure Frontend Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env to point to your backend
# VITE_API_URL=http://localhost:8000
```

### 3.3 Start the Frontend Server

```bash
# From src/frontend directory
npm run dev

# The app will be available at http://localhost:5173
```

## Step 4: Load Demo Data

Once both servers are running:

1. Open http://localhost:5173 in your browser
2. Click "Load Demo Patient" or select "Margaret Thompson" from the patient list
3. The system will automatically create demo data including:
   - 51 documents (bank statements, medical records, legal docs, VA records)
   - Medical info with 10 diagnoses and 9 medications
   - 3 insurance policies (Medicaid pending, Medicare, Humana)
   - Selected facility (Palm Beach Memory Care Center)
   - 5 recent wins/accomplishments
   - 22 tasks with priorities and due dates
   - Bills, income phases, benefit applications, contacts, assets

**New UI Tabs:**
- **Executive** - Recent Wins, Hot List, Care Journey Roadmap, Application Status Tracker
- **Medical** - Diagnoses, Medications, Vitals, Care Level
- **Insurance** - Medicaid, Medicare, Supplemental policies
- **Facility** - Selected facility with costs, contacts, key dates
- **Contacts** - Family, medical, legal, facility contacts
- **Money** - Bills, income phases, benefit pipeline, assets

## Step 5: GitHub Copilot SDK Integration

### 5.1 Understanding the LLM Abstraction Layer

The codebase has an LLM abstraction layer at `src/backend/app/services/llm_service.py` that makes it easy to swap between Azure OpenAI and GitHub Copilot SDK.

Current implementation uses Azure OpenAI directly. To integrate GitHub Copilot SDK:

### 5.2 Install GitHub Copilot SDK

```bash
cd src/backend

# Add the GitHub Copilot SDK to dependencies
poetry add github-copilot-sdk  # (or whatever the actual package name is)
```

### 5.3 Update the LLM Service

Edit `src/backend/app/services/llm_service.py`:

```python
# Add import for GitHub Copilot SDK
from github_copilot_sdk import CopilotClient  # Adjust based on actual SDK

class LLMService:
    def __init__(self):
        # Option 1: Use GitHub Copilot SDK
        self.client = CopilotClient(
            api_key=os.getenv("GITHUB_COPILOT_API_KEY")
        )
        
        # Option 2: Keep Azure OpenAI as fallback
        # self.client = AzureOpenAI(...)
    
    async def chat_completion(self, messages, model=None):
        # Update to use Copilot SDK methods
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model or "gpt-4"
        )
        return response
```

### 5.4 Environment Variables for Copilot SDK

Add to your `.env` file:

```
GITHUB_COPILOT_API_KEY=your-copilot-api-key
USE_COPILOT_SDK=true  # Toggle between Azure and Copilot
```

## Step 6: Running Tests

### 6.1 Run the Full Test Suite

```bash
cd src/backend

# Run all 39 end-to-end tests
poetry run pytest tests/test_39_scenarios.py -v

# Expected result: 39/39 tests passing (100%)
```

### 6.2 Test Categories

The test suite covers:
- Health checks
- Patient CRUD operations
- Document storage and retrieval
- Medicaid eligibility calculations
- VA benefits eligibility
- Facility search and matching
- AI chat with all 6 agents
- Task management

## Step 7: Production Deployment

### 7.1 Backend Deployment (Fly.io)

```bash
cd src/backend

# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly
flyctl auth login

# Deploy
flyctl deploy

# Set secrets
flyctl secrets set AZURE_OPENAI_ENDPOINT=your-endpoint
flyctl secrets set AZURE_OPENAI_API_KEY=your-key
```

### 7.2 Frontend Deployment (Vercel/Netlify)

```bash
cd src/frontend

# Build for production
npm run build

# The dist/ folder can be deployed to:
# - Vercel: vercel deploy
# - Netlify: netlify deploy
# - Azure Static Web Apps
```

### 7.3 Update Frontend API URL

Before deploying frontend, update `.env` to point to your deployed backend:

```
VITE_API_URL=https://your-backend.fly.dev
```

## Step 8: RAG Knowledge Base

The repository includes a comprehensive RAG knowledge base with 10 policy documents indexed in ChromaDB:

### 8.1 Knowledge Base Contents

| Document | Category | Description |
|----------|----------|-------------|
| Florida Medicaid ICP Rules | medicaid | Asset limits, income rules, look-back periods |
| VA Aid & Attendance | va | Eligibility, benefit amounts, required documents |
| Medicare/Medicaid Coordination | medicare | Dual eligible rules, QMB/SLMB programs |
| Assisted Living Regulations | facility | Florida ALF licensing, staffing, admission criteria |
| Estate Planning for Elder Care | legal | POA, trusts, Medicaid planning |
| Spend-Down Strategies | medicaid | Legal ways to reduce countable assets |
| Document Requirements | documents | Checklists for Medicaid, VA, facility applications |
| Care Transition Procedures | transition | SNF to ALF timeline, discharge planning |
| Deceased Spouse Debt Rules | legal | Florida common law property rules |
| Florida ALF Inspection Guide | facility | Quality indicators, deficiency patterns |

### 8.2 Knowledge Base API Endpoints

```bash
# Semantic search
curl -X POST http://localhost:8000/api/knowledge/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the Medicaid asset limits?", "n_results": 3}'

# Export for Azure AI Search migration
curl http://localhost:8000/api/knowledge/export/azure-search/

# List all categories
curl http://localhost:8000/api/knowledge/categories/

# Get knowledge base summary
curl http://localhost:8000/api/knowledge/summary/
```

### 8.3 Azure AI Search Migration

The knowledge base is structured for easy migration to Azure AI Search:
- Consistent metadata fields: `category`, `priority`, `topic`
- Export endpoint returns documents in Azure AI Search bulk upload format
- Vector embeddings compatible with Azure AI Search semantic search

---

## Step 9: MCP Server Integration (Optional)

The repository includes Model Context Protocol (MCP) servers for enhanced RAG capabilities:

### 9.1 Document RAG Server

Location: `src/backend/mcp_servers/document_rag_server.py`

This server provides:
- Document indexing with ChromaDB
- Semantic search across all patient documents
- Context retrieval for AI agents

### 8.2 Facility Search Server

Location: `src/backend/mcp_servers/facility_search_server.py`

This server provides:
- Facility database queries
- Distance calculations
- Matching algorithm based on patient needs

### 8.3 Running MCP Servers

```bash
# Start Document RAG server
python src/backend/mcp_servers/document_rag_server.py

# Start Facility Search server
python src/backend/mcp_servers/facility_search_server.py
```

## Step 9: Troubleshooting

### Common Issues

**Backend won't start:**
- Check that all environment variables are set
- Ensure port 8000 is not in use
- Verify Python 3.11+ is installed

**Frontend shows blank page:**
- Check browser console for errors
- Verify VITE_API_URL points to running backend
- Clear browser cache and reload

**AI responses are slow:**
- Azure OpenAI has rate limits
- Consider using gpt-5-nano for faster responses
- Check network connectivity to Azure

**Demo data not loading:**
- Ensure backend is running before loading demo
- Check backend logs for database errors
- Try refreshing the page

### Getting Help

- Check the main README.md for detailed documentation
- Review the API docs at http://localhost:8000/docs
- Contact Gregory Katz (gregory.katz@microsoft.com)

## Step 10: Submission Checklist

Before final submission, verify:

- [ ] All 39 tests pass (100% pass rate)
- [ ] Demo data loads correctly
- [ ] AI chat responds with formatted sections
- [ ] All 6 agents are working
- [ ] Documents display with realistic dates
- [ ] Executive Summary shows progress roadmap
- [ ] Intake Wizard completes all 10 steps
- [ ] No black text on dark backgrounds
- [ ] GitHub Copilot SDK integration documented
- [ ] README has all screenshots

## Files Reference

Key files for the challenge:

| File | Purpose |
|------|---------|
| `src/backend/app/services/llm_service.py` | LLM abstraction layer (SDK integration point) |
| `src/backend/app/agents/*.py` | 6 specialized AI agents |
| `src/frontend/src/App.tsx` | Main React application |
| `src/frontend/src/components/IntakeWizard.tsx` | 10-step patient intake |
| `src/frontend/src/index.css` | Vision UI dark theme |
| `README.md` | Main documentation |
| `docs/ARCHITECTURE.md` | Technical architecture |
| `presentations/PITCH_DECK.md` | Presentation materials |

---

**Document prepared for Rick Weyenberg**
**CareNav Florida - GitHub Copilot SDK Enterprise Challenge**
**Authors: Gregory Katz and Rick Weyenberg**
