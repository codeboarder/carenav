"""
Summarizer Agent for CareNav Florida - Plain English output generation.
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from typing import Optional
from app.agents.base import BaseAgent


class SummarizerAgent(BaseAgent):
    """Agent that converts technical outputs to plain English for families."""
    
    def __init__(self):
        super().__init__(
            name="summarizer",
            description="Plain English summary generation for families"
        )
    
    def get_system_prompt(self) -> str:
        return """You are the CareNav Summarizer Agent. Your role is to convert technical legal and financial information into clear, compassionate plain English for families navigating elder care.

COMMUNICATION PRINCIPLES:

1. EMPATHY FIRST
   - Acknowledge this is a difficult time
   - Use "your mom" or "your dad" not "the patient"
   - Avoid jargon - explain terms when necessary

2. CLARITY
   - Lead with the most important information
   - Use short sentences
   - Break complex topics into steps
   - Use bullet points for action items

3. ACCURACY
   - Never oversimplify to the point of being wrong
   - Include dollar amounts and dates
   - Cite sources when relevant
   - Flag uncertainty clearly

4. ACTIONABLE
   - Every summary should end with clear next steps
   - Include phone numbers and deadlines
   - Prioritize actions (urgent, this week, this month)

FORMATTING RULES:

For eligibility summaries:
- Start with "Based on what you've told me..."
- State eligibility clearly (yes/no/maybe)
- Explain the key numbers
- List what needs to happen next

For facility recommendations:
- Lead with the top 2-3 options
- Explain why each is a good fit
- Include monthly costs and what's covered
- Provide contact info and visiting hours

For legal guidance:
- Start with what NOT to do (if relevant)
- Explain the safe options
- Be clear about what needs an attorney
- Never give legal advice - give legal information

OUTPUT FORMAT (respond in JSON):
{
  "summary": "string - plain English summary",
  "key_points": ["string"],
  "action_items": [{
    "action": "string",
    "priority": "urgent|this_week|this_month",
    "phone": "string" | null,
    "deadline": "string" | null
  }],
  "warnings": ["string"],
  "questions_to_ask": ["string"],
  "emotional_support": "string - brief supportive message"
}"""

    @staticmethod
    def format_eligibility_summary(
        medicaid_result: dict,
        va_result: dict,
        patient_name: str = "your parent",
    ) -> str:
        """Format eligibility results into plain English."""
        lines = []
        
        # Medicaid section
        if medicaid_result.get("eligible"):
            lines.append(f"Good news: {patient_name} appears to qualify for Florida Medicaid right now.")
        else:
            over_by = medicaid_result.get("over_by", 0)
            if over_by > 0:
                lines.append(
                    f"Right now, {patient_name} has ${over_by:,.0f} more in countable assets "
                    f"than Medicaid allows (the limit is $2,000). But don't worry - there are "
                    f"legal ways to spend down these assets."
                )
            else:
                lines.append(f"{patient_name} may qualify for Medicaid, but we need to verify some details.")
        
        # VA section
        if va_result.get("eligible"):
            benefit = va_result.get("monthly_benefit", 0)
            va_type = va_result.get("type", "")
            if va_type == "surviving_spouse":
                lines.append(
                    f"\nAs a surviving spouse of a wartime veteran, {patient_name} may qualify "
                    f"for ${benefit:,.0f}/month in VA Aid & Attendance benefits. This money "
                    f"comes directly to you and can help pay for care."
                )
            elif va_type == "veteran":
                lines.append(
                    f"\nAs a wartime veteran, {patient_name} may qualify for ${benefit:,.0f}/month "
                    f"in VA Aid & Attendance benefits."
                )
        
        return "\n".join(lines)

    @staticmethod
    def format_facility_summary(
        facilities: list[dict],
        patient_income: float,
        va_benefit: float = 0,
    ) -> str:
        """Format facility recommendations into plain English."""
        if not facilities:
            return "I couldn't find any facilities matching your criteria. Let's adjust the search."
        
        lines = [f"I found {len(facilities)} facilities that could work. Here are the top options:\n"]
        
        total_income = patient_income + va_benefit
        
        for i, facility in enumerate(facilities[:3], 1):
            name = facility.get("name", "Unknown")
            rate = facility.get("rate_low", 0)
            medicaid = "Yes" if facility.get("accepts_medicaid") else "No"
            day_one = " (Day 1)" if facility.get("medicaid_day_one") else ""
            distance = facility.get("distance_miles", 0)
            
            gap = rate - total_income
            affordability = (
                f"Within budget" if gap <= 0 
                else f"${gap:,.0f}/month gap"
            )
            
            lines.append(f"{i}. **{name}**")
            lines.append(f"   - ${rate:,.0f}/month ({affordability})")
            lines.append(f"   - Medicaid: {medicaid}{day_one}")
            lines.append(f"   - {distance:.1f} miles away")
            lines.append(f"   - Phone: {facility.get('phone', 'Call for info')}")
            lines.append("")
        
        return "\n".join(lines)

    @staticmethod
    def format_spend_down_summary(
        options: list[dict],
        amount_needed: float,
    ) -> str:
        """Format spend-down options into plain English."""
        lines = [
            f"To qualify for Medicaid, we need to reduce countable assets by ${amount_needed:,.0f}. "
            f"Here are legal ways to do this:\n"
        ]
        
        for option in options:
            name = option.get("strategy", "")
            amount = option.get("amount", 0)
            risk = option.get("risk", "low")
            attorney = option.get("requires_attorney", False)
            
            risk_note = " (consult attorney)" if attorney else ""
            lines.append(f"- **{name}**: up to ${amount:,.0f}{risk_note}")
            lines.append(f"  {option.get('description', '')}")
            lines.append("")
        
        lines.append(
            "\nIMPORTANT: Do NOT give money to family members or pay a deceased spouse's debts. "
            "These actions create Medicaid penalties."
        )
        
        return "\n".join(lines)

    @staticmethod
    def format_deceased_debt_warning() -> str:
        """Format the deceased spouse debt warning."""
        return """
**IMPORTANT: Do Not Pay Your Late Spouse's Individual Debts**

Florida is NOT a community property state. This means you are NOT responsible for debts that were only in your spouse's name, including:
- Credit cards in their name only
- Medical bills in their name only
- Personal loans in their name only

Creditors may call and pressure you to pay. You can tell them:
"The account holder is deceased. Please send a written request to the estate. Do not call this number again."

Paying these debts would waste money that could be used for your care. If creditors are aggressive, consult an elder law attorney.

**Exception**: You ARE responsible for joint debts (accounts with both names).
"""
