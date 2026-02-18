# CareNav Florida - Responsible AI Notes

This document outlines the responsible AI considerations, potential risks, and mitigation strategies for the CareNav Florida multi-agent elder care navigation system.

## Overview

CareNav Florida uses AI to help families navigate complex elder care decisions involving Medicaid eligibility, VA benefits, and facility selection. Given the sensitive nature of this domain (healthcare, finances, vulnerable populations), responsible AI practices are critical.

## Key Responsible AI Principles

### 1. Transparency

**What we do:**
- Clearly identify that users are interacting with an AI system
- Explain how recommendations are generated
- Provide sources for eligibility rules and calculations
- Show confidence levels when appropriate

**Implementation:**
- System prompts include "You are CareNav Florida, an AI assistant..."
- Responses cite specific regulations (e.g., "Per Florida Medicaid ICP rules...")
- Calculations show step-by-step reasoning

### 2. Accuracy

**What we do:**
- Use current year figures for all limits and thresholds
- Cross-validate recommendations with the Validator agent
- Flag uncertain or edge-case scenarios
- Provide disclaimers for complex situations

**Implementation:**
- Eligibility calculations use 2024/2025 figures with annual updates
- Validator agent checks all recommendations before delivery
- System prompts instruct agents to say "I'm not certain" when appropriate

### 3. Privacy

**What we do:**
- Minimize data collection to what's necessary
- Do not store conversation history beyond the session
- Do not transmit patient data to third parties (except LLM provider)
- Instruct LLM not to learn from or store patient data

**Implementation:**
- SQLite database stores only essential patient information
- LLM system prompts include: "Do not store or learn from this patient's data"
- No analytics or tracking beyond basic usage metrics

### 4. Fairness

**What we do:**
- Provide consistent recommendations regardless of patient demographics
- Avoid bias in facility recommendations
- Ensure accessibility for users with disabilities

**Implementation:**
- Facility search uses objective criteria (distance, rating, Medicaid acceptance)
- No demographic factors in recommendation algorithms
- Frontend uses accessible fonts, colors, and ARIA labels

### 5. Human Oversight

**What we do:**
- Recommend professional consultation for complex decisions
- Provide information to support human decision-making, not replace it
- Include clear disclaimers about the limitations of AI advice

**Implementation:**
- All responses include: "This is not legal or financial advice"
- Complex scenarios recommend: "Consult with an elder law attorney"
- Users make final decisions; AI provides information only

## Potential Risks and Mitigations

### Risk 1: Incorrect Eligibility Calculations

**Risk:** AI provides incorrect Medicaid or VA eligibility information, leading families to make poor decisions.

**Mitigation:**
- Use rule-based calculations for eligibility (not LLM inference)
- Validator agent cross-checks all calculations
- Include disclaimer: "Verify with your local Medicaid office"
- Annual review of eligibility limits and rules

### Risk 2: Biased Facility Recommendations

**Risk:** AI recommends certain facilities over others based on factors unrelated to patient needs.

**Mitigation:**
- Use objective, transparent ranking criteria
- Show all matching facilities, not just "top picks"
- Allow users to adjust search criteria
- No paid placements or advertising influence

### Risk 3: Privacy Breach

**Risk:** Sensitive patient health and financial information is exposed or misused.

**Mitigation:**
- Encrypt data at rest and in transit
- Minimize data retention
- No sharing with third parties (except LLM provider)
- Regular security audits

### Risk 4: Over-Reliance on AI

**Risk:** Families rely solely on AI advice without consulting professionals.

**Mitigation:**
- Prominent disclaimers on every response
- Recommend professional consultation for complex cases
- Provide contact information for relevant professionals
- Educate users about AI limitations

### Risk 5: Outdated Information

**Risk:** AI provides outdated eligibility limits or rules.

**Mitigation:**
- Annual review and update of all limits
- Date-stamp all regulatory information
- System prompts include current year
- Validator checks for outdated figures

## Disclaimers

The following disclaimers are included in CareNav Florida responses:

### Standard Disclaimer
> This information is provided for educational purposes only and does not constitute legal, financial, or medical advice. Eligibility determinations are made by the relevant government agencies, not by this system. Please consult with qualified professionals before making important decisions about elder care.

### Medicaid Disclaimer
> Medicaid eligibility rules vary by state and change annually. The information provided is based on current Florida Medicaid ICP rules but should be verified with your local Department of Children and Families (DCF) office or a qualified Medicaid planning attorney.

### VA Benefits Disclaimer
> VA benefits eligibility is determined by the Department of Veterans Affairs. The information provided is based on current VA Aid & Attendance rules but should be verified with your local VA office or an accredited VA claims agent.

### Facility Disclaimer
> Facility information is provided for reference only. Availability, pricing, and services may change. Please contact facilities directly to verify current information and schedule tours before making decisions.

## Data Handling

### Data Collected
- Patient demographics (name, DOB, SSN)
- Financial information (assets, income)
- Health information (diagnoses, care needs)
- Veteran status
- Family/caregiver information

### Data Storage
- SQLite database on backend server
- ChromaDB for document embeddings (optional)
- No cloud storage of patient data

### Data Retention
- Demo data: Retained for demonstration purposes
- User data: Retained until user requests deletion
- Conversation history: Not retained beyond session

### Data Sharing
- LLM Provider (Azure OpenAI): Conversation context sent for processing
- No other third-party sharing
- No selling or monetization of patient data

## Accessibility

### Current Implementation
- High contrast dark theme (Vision UI)
- Large fonts (22px base)
- Keyboard navigation support
- Screen reader compatible (ARIA labels)

### Future Improvements
- WCAG 2.1 AA compliance audit
- Voice input/output support
- Multi-language support
- Simplified language option

## Monitoring and Feedback

### Current Monitoring
- Error logging for failed API calls
- Basic usage metrics (queries per day)

### Future Monitoring
- User satisfaction surveys
- Accuracy tracking (compare recommendations to outcomes)
- Bias detection in facility recommendations
- Regular audits by domain experts

### Feedback Channels
- In-app feedback button
- GitHub issues for technical problems
- Email support for user concerns

## Incident Response

### If Incorrect Information is Discovered
1. Immediately update the affected rules/calculations
2. Notify users who may have received incorrect information
3. Document the incident and root cause
4. Implement safeguards to prevent recurrence

### If Privacy Breach Occurs
1. Contain the breach immediately
2. Notify affected users within 72 hours
3. Report to relevant authorities as required
4. Conduct post-incident review

## Governance

### Review Schedule
- **Monthly:** Review user feedback and error logs
- **Quarterly:** Update eligibility limits and rules
- **Annually:** Full responsible AI audit

### Responsible Parties
- **Product Owner:** Overall responsibility for RAI compliance
- **Development Team:** Implementation of RAI features
- **Domain Experts:** Review of eligibility rules and recommendations
- **Legal/Compliance:** Review of disclaimers and data handling

## Conclusion

CareNav Florida is designed with responsible AI principles at its core. We recognize that AI systems assisting with elder care decisions must be accurate, transparent, fair, and respectful of privacy. We are committed to continuous improvement of our RAI practices based on user feedback, domain expert review, and evolving best practices in AI ethics.

For questions or concerns about our responsible AI practices, please contact the development team.
