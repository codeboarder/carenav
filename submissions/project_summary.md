# CareNav Florida — Project Summary

CareNav Florida is a multi-agent AI elder care navigation system built with the GitHub Copilot SDK. It helps family caretakers navigate the overwhelming complexity of transitioning elderly loved ones from skilled nursing to assisted living — including Medicaid eligibility, VA benefits, facility selection, legal requirements, and financial planning.

Six specialized AI agents (orchestrator, eligibility, facility, legal, validator, summarizer) coordinate through the Copilot SDK's agentic loop, with four MCP servers exposing Florida-specific rules, VA regulations, facility data, and patient documents via RAG.

The platform is enterprise-ready and reusable — swap Florida rules for any state's regulations. Built for health systems where discharge planners and case managers handle thousands of these transitions annually.

Azure integration: Azure OpenAI (BYOK), Azure AI Search, Azure AI Foundry.

---
-OR-

CareNav Florida is an open-source, multi-agent elder care navigation platform designed to help families make urgent, high-stakes care decisions in Florida. The system combines a React/TypeScript dashboard with a FastAPI backend and six coordinated AI agents: Orchestrator, Eligibility, Facility, Legal, Validator, and Summarizer. Together, they calculate Medicaid/VA/Medicare eligibility, recommend legal spend-down options, compare care facilities, validate guidance, and turn complex rules into practical action plans. The product includes guided intake, document management, task tracking, and an AI chat experience tailored to real family workflows during hospital-to-facility transitions. Architecturally, it uses an LLM abstraction layer (currently Azure OpenAI, with Copilot SDK path), modular API routers, and a knowledge base supporting local development and enterprise search migration. CareNav’s core value is reducing costly mistakes, time pressure, and confusion by unifying policy knowledge, patient context, and next-step recommendations in one actionable system. It is built from lived caregiver experience and validated through scenarios.
