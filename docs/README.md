# CareNav Florida Documentation

This folder contains comprehensive documentation for the CareNav Florida multi-agent elder care navigation system.

## Contents

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture, agent design, and data flow |
| [RAI_NOTES.md](RAI_NOTES.md) | Responsible AI considerations and guidelines |
| [SETUP.md](SETUP.md) | Development environment setup and deployment |

## Quick Links

- **Live Demo**: [Deploy your own instance]
- **Backend API**: [Deploy your own instance]
- **GitHub Repository**: https://github.com/gregorykatz/carenav-florida

## System Overview

CareNav Florida is a multi-agent AI system designed to help families navigate the complex process of finding and funding elder care in Florida. The system provides guidance on:

1. **Medicaid Eligibility** - Florida Medicaid Institutional Care Program (ICP) eligibility assessment, spend-down calculations, and look-back period analysis

2. **VA Benefits** - Aid & Attendance eligibility for veterans and surviving spouses, benefit calculations, and required documentation

3. **Facility Search** - Assisted living, memory care, and skilled nursing facility search with Medicaid acceptance filtering

4. **Legal Guidance** - Spend-down strategies, asset protection within legal limits, and deceased spouse debt guidance

## Agent Architecture

The system uses 6 specialized AI agents coordinated by an orchestrator:

```
User Query → Orchestrator → [Eligibility, Facility, Legal, Validator, Summarizer] → Response
```

Each agent has domain-specific knowledge and tools. See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLite, ChromaDB (optional)
- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **AI**: Azure OpenAI (GPT-5.2) with abstraction layer for GitHub Copilot SDK
- **Deployment**: Fly.io (backend), Static hosting (frontend)

## Getting Started

See [SETUP.md](SETUP.md) for detailed setup instructions.

### Quick Start

```bash
# Backend
cd src/backend
poetry install
poetry run uvicorn app.main:app --reload

# Frontend
cd src/frontend
npm install
npm run dev
```

## GitHub Copilot SDK Integration

This codebase is prepared for GitHub Copilot SDK integration. Key files:

- `src/backend/app/services/llm_service.py` - LLM abstraction layer (change one line to switch providers)
- `mcp.json` - MCP server configuration for Copilot SDK
- `AGENTS.md` - Agent definitions and custom instructions

To integrate the Copilot SDK:

1. Implement `CopilotSDKProvider` class in `llm_service.py`
2. Change `provider_type = "copilot_sdk"` in `get_llm_provider()`
3. Register MCP servers as tools with the Copilot session

## Enterprise Applicability & Reusability (35 pts)

CareNav's architecture is state-agnostic by design. The MCP servers encapsulate state-specific rules (Florida Medicaid ICP, VA regulations) as swappable modules. To deploy for another state:

1. Replace `medicaid_server.py` rules with the target state's Medicaid program
2. Update facility search parameters for the target region
3. All other components (agents, UI, document management) work unchanged

This pattern applies to any health system managing care transitions — any organization with discharge planning workflows.

## Azure & Microsoft Integration (25 pts)

- **Azure OpenAI**: Primary LLM via BYOK mode through Copilot SDK
- **Azure AI Search**: Facility database indexing and hybrid search
- **Azure AI Foundry**: Model deployment and management
- **GitHub Copilot SDK**: Agentic orchestration with MCP tool servers

## Security, Governance & Responsible AI (15 pts)

See [RAI_NOTES.md](./RAI_NOTES.md) for full details.

- Synthetic demo data only — no real PII
- SSN masking in all display surfaces
- AI recommendations include disclaimer: "Guidance only, not legal/medical advice"
- Human-in-the-loop: all actions require caretaker confirmation
- Florida statutes cited for all eligibility calculations
- Facility scoring algorithm fully documented and auditable

## Operational Readiness (15 pts)

- GitHub Actions CI pipeline for lint, test, build
- `.env.example` files for quick setup
- Docker support for backend deployment
- SQLite for zero-config local development
- Fly.io deployment config included

## Support

For questions or issues, contact the development team or open a GitHub issue.
