# CareNav Florida — Gregory's Checklist

**For: Gregory Katz**
**Submission Deadline: March 7, 2026 at 10 PM PST**

Built by Gregory Katz and Rick Weyenberg. Code is as-is, open source.

---

## Overview

Rick handles all code and engineering — data layer migration, SDK integration, repo cleanup, screenshots, challenge files, testing. Everything.

You handle three things: presentation deck, demo video, and final submission.

**Do not start until Rick confirms everything is working and tests pass.**

---

## STEP 1: Presentation Deck (1-2 Slides)

Create `/presentations/CareNavFlorida.pptx`

### Slide 1: The Problem & Solution

**Title:** CareNav Florida — AI-Powered Elder Care Navigation

**Left side — The Problem:**
- 10,000 Americans turn 65 every day
- Family caretakers make $500K+ decisions with zero training
- Florida Medicaid alone has 200+ pages of rules
- Medicare covers skilled nursing for only 100 days
- Most families don't know about VA survivor benefits ($1,432/month)

**Right side — The Solution:**
- 6 specialized AI agents via GitHub Copilot SDK
- 4 MCP servers (Medicaid rules, VA benefits, facility search, document RAG)
- Azure OpenAI (BYOK) + Azure AI Search + Azure SQL + Azure AI Foundry
- 55 documents, 39 tests, 100% pass rate
- Reusable pattern — swap Florida rules for any state

**Bottom:** Dashboard screenshot + GitHub repo link

### Slide 2: Architecture & Enterprise Value

**Left side — Architecture diagram:**
- Show the flow: React → FastAPI → Copilot SDK → CLI → MCP Servers + Azure OpenAI
- Call out each Azure integration point

**Right side — Enterprise Value:**
- Built for health systems managing care transitions at scale
- State-agnostic: swap Medicaid MCP server for any state
- Validated against real-world elder care scenarios

**Bottom:** Scoring callouts
- Enterprise applicability: ✅ (35 pts)
- Azure integration: ✅ Azure OpenAI + AI Search + SQL + Foundry (25 pts)
- Operational readiness: ✅ CI/CD, .env config, deployment docs (15 pts)
- RAI: ✅ Synthetic data, human-in-loop, disclaimers (15 pts)
- Foundry IQ: ✅ (15 bonus pts)
- Customer validation: ✅ Contoso Health context (10 bonus pts)
- Product feedback: ✅ (10 bonus pts)

Include repo link: `https://github.com/gregorykatz/carenav-florida`

---

## STEP 2: Product Feedback (10 Bonus Points)

1. Go to the SDK team channel (internal Microsoft Teams)
2. Post genuine feedback about the Copilot SDK based on the integration Rick did
3. Mention what worked, what was confusing, what you'd improve
4. Take a screenshot of your post
5. Give screenshot to Rick to save as `/submissions/product_feedback_screenshot.png`

---

## STEP 3: Demo Video (3 Minutes Max)

### Setup Before Recording
- Rick runs the app locally with Margaret Thompson demo loaded
- Azure SQL + Azure AI Search connected (not local fallbacks)
- Chat panel ready
- Clean browser window at 1440x900
- Close all other tabs and notifications

### Recording Tool
- OBS Studio, Loom, or Windows Game Bar (Win+G)
- Screen + microphone
- Export as MP4, under 100MB

### Script

**0:00–0:30 — The Problem (voiceover over dashboard)**
> "When a family member suddenly needs long-term care, families are thrown into an overwhelming maze of Medicaid applications, VA benefits, and facility decisions — making half-million-dollar decisions with zero training. CareNav Florida is an AI-powered navigator that helps families through this crisis. Let me show you Margaret Thompson's case."

Show: Executive dashboard — Recent Wins (5 accomplishments), Hot List (22 tasks), Care Journey Roadmap, Application Status Tracker.

**0:30–1:00 — The AI Chat (live)**
> "Margaret is 83, a widow of a Vietnam veteran, currently in skilled nursing. Her family wants to know if she's ready for assisted living."

Type: "Is Margaret ready for assisted living? What does she still need?"

Show: Multi-agent response — Medicaid (blue), VA benefits (green), admission gap analysis, action items (orange).

**1:00–1:30 — Documents & Financial Analysis**
> "CareNav tracks 51 documents — 3 years of medical records, 2 years of bank statements, legal documents, veteran records."

Click: Docs tab → open bank statement → switch to Money tab → show bills, income phases, benefit pipeline.

> "Margaret is $1,000 over the Medicaid limit. The system identifies three legal spend-down options. The Income Phases card shows her income growing from $2,425 to $4,557/month as benefits come online."

**1:30–2:15 — Tasks & Facility Search**
> "Everything turns into actionable tasks with deadlines and phone numbers."

Show: To-Do tab → check off a task → Places tab → facility scoring → Facility tab → selected facility details with costs.

**2:15–3:00 — Architecture & Enterprise Value**
> "Under the hood, six AI agents coordinate through the GitHub Copilot SDK. Four MCP servers expose Florida Medicaid rules, VA regulations, facility data, and patient documents through Azure AI Search hybrid vector and semantic search. Data lives in Azure SQL. Models run through Azure OpenAI via BYOK."

Show: Architecture diagram.

> "This is state-agnostic — swap the Medicaid MCP server and it works for any state. Every health system in America needs this."

---

## STEP 4: Final Submission

### Before Submitting — Confirm with Rick
- [ ] All tests pass (39+ tests, 100%)
- [ ] Copilot SDK integration works end-to-end
- [ ] README renders on GitHub with all screenshots
- [ ] AGENTS.md and mcp.json in repo root
- [ ] Presentation deck in `/presentations/`
- [ ] Product feedback screenshot in `/submissions/`
- [ ] Customer validation in `/customer/`
- [ ] 150-word project summary in `/submissions/project_summary.md`
- [ ] All source files have attribution header
- [ ] No stale references anywhere in repo
- [ ] GitHub Actions CI is green

### Submit

1. Go to submission form: **Aka.ms/FY26SDKChallenge**
2. Fill in:
   - Project summary (copy from `/submissions/project_summary.md`)
   - GitHub repo URL
   - Demo video (upload or link)
   - Presentation deck (upload)
   - Product feedback screenshot (upload)
   - Customer validation reference
3. **Submit before March 7, 2026 at 10 PM PST**

### After Submission
- Screening: March 9–20
- If finalist: Present to leadership March 23–27
- Winners announced in April community calls

---

## Timeline

| When | What | Who |
|------|------|-----|
| Now → Mar 3 | All engineering, migration, SDK, testing, screenshots, challenge files | Rick |
| Mar 3 → Mar 5 | Presentation deck, product feedback post | Gregory |
| Mar 5 → Mar 6 | Demo video recording | Gregory (Rick runs the app) |
| Mar 6 | Final review, dry run | Both |
| **Mar 7 by 10 PM PST** | **SUBMIT** | **Gregory** |

---

**Built by Gregory Katz and Rick Weyenberg**
**CareNav Florida — GitHub Copilot SDK Enterprise Challenge**
