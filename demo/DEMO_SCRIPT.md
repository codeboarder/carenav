# CareNav Florida - Demo Script
## GitHub Copilot SDK Enterprise Challenge

This script guides you through demonstrating CareNav Florida's multi-agent AI capabilities.

---

## Pre-Demo Setup

### 1. Open the Application
- **Frontend**: [Your deployed frontend URL]
- **Backend API**: [Your deployed backend URL]

### 2. Select Demo Patient
- Click the patient dropdown in the header
- Select "Margaret Thompson"
- The dashboard will load with her complete profile

---

## Demo Flow (10 minutes)

### Part 1: Executive Summary (2 minutes)

**What to Show:**
1. Open the "Executive" tab (default view)
2. Point out the key status cards:
   - **Medicaid Status**: "$1,000 Over Limit" - shows she needs to spend down
   - **VA Benefits**: "$1,432/month" - eligible as surviving spouse
   - **Tasks**: 10 action items with priorities

**Talking Points:**
> "Margaret is an 82-year-old widow whose husband Robert was a Vietnam veteran. She has Alzheimer's and needs Memory Care placement. CareNav has already analyzed her situation and identified that she's only $1,000 over the Medicaid asset limit, and she's eligible for $1,432/month in VA Aid & Attendance benefits as a surviving spouse."

### Part 2: Documents Tab (2 minutes)

**What to Show:**
1. Click the "Docs" tab
2. Scroll through the document categories:
   - AI Analysis Reports
   - Medical Records (3-year history)
   - Bank Statements (2 years)
   - VA Documents (DD-214, death certificate)
   - Legal Documents (POA, advance directive)
3. Click on a document to show the detail modal

**Talking Points:**
> "CareNav has ingested 51 documents for Margaret - everything from her husband's DD-214 to 2 years of bank statements. The AI has analyzed each document and extracted key information. Click on any document to see the full content and AI analysis."

### Part 3: AI Chat - Eligibility Question (2 minutes)

**What to Show:**
1. Click "AI Assistant" button in the header
2. Type: "Is Margaret eligible for Medicaid? What does she need to do?"
3. Wait for the response (10-15 seconds)
4. Point out the structured response with Medicaid status, spend-down options

**Talking Points:**
> "Let's ask the AI about Margaret's Medicaid eligibility. Notice how the response is structured with clear sections - the Orchestrator agent coordinated with the Eligibility agent and Legal agent to provide a comprehensive answer with specific spend-down strategies."

### Part 4: AI Chat - VA Benefits (2 minutes)

**What to Show:**
1. In the chat, type: "What VA benefits is Margaret eligible for?"
2. Wait for the response
3. Point out the benefit amount and required documents

**Talking Points:**
> "Now let's ask about VA benefits. The AI knows that Margaret's husband Robert served in Vietnam and passed away in 2020. As a surviving spouse, she's eligible for VA Aid & Attendance - that's $1,432 per month to help pay for her care."

### Part 5: Facility Search (2 minutes)

**What to Show:**
1. Click the "Places" tab
2. Show the facility list sorted by match score
3. Point out Medicaid acceptance and availability

**Talking Points:**
> "The Facility agent has searched for Memory Care facilities in Palm Beach County that accept Medicaid. Each facility is scored based on Margaret's specific needs - her Alzheimer's diagnosis, budget, and location preferences. The top match is Palm Beach Memory Care Center with 3 Medicaid beds available."

---

## Key Demo Questions & Answers

### Q: "How does the multi-agent system work?"
> "CareNav uses 6 specialized AI agents. The Orchestrator receives your question and routes it to the appropriate specialists - Eligibility for benefits questions, Facility for placement, Legal for asset protection. The Validator checks all recommendations, and the Summarizer creates the final response."

### Q: "How is this different from ChatGPT?"
> "Three key differences: First, CareNav has domain-specific knowledge - Florida Medicaid rules, VA regulations, facility databases. Second, it has access to the patient's actual documents through RAG. Third, the multi-agent architecture ensures accuracy through cross-validation."

### Q: "How does the Copilot SDK integration work?"
> "We've built an LLM Service Abstraction Layer that allows us to swap between Azure OpenAI and GitHub Copilot SDK with a single line change. The MCP servers expose our domain tools - Medicaid eligibility, VA benefits, facility search - that can be registered with a Copilot session."

### Q: "What about privacy and security?"
> "Patient data is stored in SQLite on the backend - no cloud storage. We don't retain conversation history beyond the session. All responses include appropriate disclaimers, and we recommend professional consultation for complex decisions."

---

## Troubleshooting

### If the app doesn't load:
- Check that you're using the correct URL
- Try refreshing the page
- Check browser console for errors

### If Margaret Thompson doesn't appear:
- The demo patient should auto-load
- If not, check the patient dropdown
- Backend may need a restart

### If AI responses are slow:
- Azure OpenAI can take 10-20 seconds for complex queries
- This is normal for multi-agent coordination
- The response will include multiple agent perspectives

---

## Post-Demo Resources

- **GitHub Repository**: https://github.com/gregorykatz/carenav-florida
- **Architecture Docs**: /docs/ARCHITECTURE.md
- **Agent Definitions**: /AGENTS.md
- **MCP Configuration**: /mcp.json
- **Setup Guide**: /docs/SETUP.md

---

## Recording the Demo

If recording a video demo:

1. **Screen Resolution**: 1920x1080 recommended
2. **Browser**: Chrome or Edge (best compatibility)
3. **Audio**: Prepare talking points in advance
4. **Duration**: Target 5-10 minutes
5. **Flow**: Follow the demo script above

### Suggested Recording Outline:
1. Introduction (30 sec) - Problem statement
2. Executive Summary (2 min) - Show Margaret's status
3. Documents (1 min) - Show document depth
4. AI Chat (3 min) - Eligibility and VA questions
5. Facilities (1 min) - Show matching
6. Technical (1 min) - Mention Copilot SDK integration
7. Conclusion (30 sec) - Call to action

---

## Contact

For questions about this demo:
- **Email**: gregory.katz@microsoft.com
- **GitHub**: @gregorykatz_microsoft
