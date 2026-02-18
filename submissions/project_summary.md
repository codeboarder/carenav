# CareNav Florida — Project Summary

CareNav Florida is a multi-agent AI elder care navigation system built with the GitHub Copilot SDK. It helps family caretakers navigate the overwhelming complexity of transitioning elderly loved ones from skilled nursing to assisted living — including Medicaid eligibility, VA benefits, facility selection, legal requirements, and financial planning.

Six specialized AI agents (orchestrator, eligibility, facility, legal, validator, summarizer) coordinate through the Copilot SDK's agentic loop, with four MCP servers exposing Florida-specific rules, VA regulations, facility data, and patient documents via RAG.

The platform is enterprise-ready and reusable — swap Florida rules for any state's regulations. Built for health systems where discharge planners and case managers handle thousands of these transitions annually.

Azure integration: Azure OpenAI (BYOK), Azure AI Search, Azure AI Foundry.
