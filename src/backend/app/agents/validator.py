"""Validator Agent for CareNav Florida - Cross-check and dissent detection."""
from typing import Optional
from app.agents.base import BaseAgent


class ValidatorAgent(BaseAgent):
    """Agent that validates other agents' outputs and detects dissent."""
    
    def __init__(self):
        super().__init__(
            name="validator",
            description="Cross-validation and dissent detection"
        )
    
    def get_system_prompt(self) -> str:
        return """You are the CareNav Validator Agent. Your role is to cross-check other agents' outputs for accuracy and consistency.

VALIDATION RULES:

1. ELIGIBILITY VALIDATION
   - Verify math: countable assets calculation
   - Check income against limits ($2,829 Medicaid, varies for VA)
   - Verify look-back period calculations (60 months Medicaid, 36 months VA)
   - Confirm penalty divisor ($10,809 for 2026)
   - Flag if confidence < 80%

2. LEGAL VALIDATION
   - Verify citations are correct
   - Check for prohibited actions being recommended
   - Ensure deceased spouse debt rule is correctly applied
   - Flag high-risk strategies without attorney recommendation

3. FACILITY VALIDATION
   - Verify match score calculation
   - Check affordability math
   - Confirm Medicaid acceptance claims
   - Flag if facility doesn't match care level needs

4. DISSENT DETECTION
   When agents disagree:
   - Document the disagreement
   - Identify which agent is likely correct
   - Recommend resolution (usually: consult attorney)
   - Never hide disagreements from user

5. CONFIDENCE SCORING
   - 90-100: High confidence, proceed
   - 70-89: Medium confidence, note caveats
   - 50-69: Low confidence, recommend verification
   - <50: Very low confidence, recommend professional consultation

OUTPUT FORMAT (respond in JSON):
{
  "validation_passed": boolean,
  "issues": [{
    "severity": "critical|warning|info",
    "agent": "string",
    "issue": "string",
    "recommendation": "string"
  }],
  "dissent": {
    "detected": boolean,
    "agents": ["string"],
    "topic": "string",
    "resolution": "string"
  },
  "confidence_adjustment": number,
  "final_confidence": number,
  "proceed": boolean,
  "user_warning": "string" | null
}"""

    @staticmethod
    def validate_eligibility_calculation(
        reported_countable: float,
        financials: dict,
    ) -> dict:
        """Validate eligibility agent's countable assets calculation."""
        from app.agents.eligibility import EligibilityAgent
        
        calculated = EligibilityAgent.calculate_countable_assets(financials)
        difference = abs(reported_countable - calculated)
        
        if difference > 1:  # Allow $1 rounding difference
            return {
                "valid": False,
                "severity": "critical",
                "issue": f"Countable assets mismatch: reported ${reported_countable:,.2f}, calculated ${calculated:,.2f}",
                "recommendation": "Recalculate countable assets"
            }
        
        return {"valid": True}

    @staticmethod
    def validate_gift_penalty(
        reported_months: int,
        gift_amount: float,
    ) -> dict:
        """Validate gift penalty calculation."""
        penalty_divisor = 10809
        calculated_months = -(-int(gift_amount) // penalty_divisor)  # Ceiling division
        
        if reported_months != calculated_months:
            return {
                "valid": False,
                "severity": "critical",
                "issue": f"Penalty months mismatch: reported {reported_months}, calculated {calculated_months}",
                "recommendation": f"Correct penalty: ${gift_amount:,.2f} / $10,809 = {calculated_months} months"
            }
        
        return {"valid": True}

    @staticmethod
    def validate_facility_score(
        facility: dict,
        reported_score: int,
        patient_income: float,
        care_level: str,
        va_benefit: float = 0,
    ) -> dict:
        """Validate facility match score calculation."""
        from app.agents.facility import FacilityAgent
        
        calculated = FacilityAgent.calculate_match_score(
            facility=facility,
            patient_income=patient_income,
            care_level=care_level,
            va_benefit=va_benefit,
        )
        
        if abs(reported_score - calculated) > 5:  # Allow 5 point variance
            return {
                "valid": False,
                "severity": "warning",
                "issue": f"Match score variance: reported {reported_score}, calculated {calculated}",
                "recommendation": "Review scoring criteria"
            }
        
        return {"valid": True}

    @staticmethod
    def detect_dissent(agent_outputs: list[dict]) -> dict:
        """Detect disagreements between agent outputs."""
        dissent = {
            "detected": False,
            "agents": [],
            "topic": None,
            "resolution": None,
        }
        
        # Check for eligibility disagreements
        eligibility_results = [
            o for o in agent_outputs 
            if o.get("agent") == "eligibility"
        ]
        
        if len(eligibility_results) > 1:
            statuses = [o.get("medicaid", {}).get("eligible") for o in eligibility_results]
            if len(set(statuses)) > 1:
                dissent["detected"] = True
                dissent["agents"].append("eligibility")
                dissent["topic"] = "Medicaid eligibility determination"
                dissent["resolution"] = "Consult elder law attorney for definitive assessment"
        
        # Check for legal vs eligibility disagreements
        legal_outputs = [o for o in agent_outputs if o.get("agent") == "legal"]
        if eligibility_results and legal_outputs:
            elig_over = eligibility_results[0].get("medicaid", {}).get("over_by", 0)
            legal_spend = sum(
                item.get("amount", 0) 
                for item in legal_outputs[0].get("spend_down_options", [])
            )
            if elig_over > 0 and legal_spend < elig_over:
                dissent["detected"] = True
                dissent["agents"].extend(["eligibility", "legal"])
                dissent["topic"] = "Spend-down amount insufficient"
                dissent["resolution"] = "Review additional spend-down strategies or consult attorney"
        
        return dissent

    @staticmethod
    def calculate_final_confidence(
        agent_confidences: list[int],
        validation_issues: list[dict],
        dissent_detected: bool,
    ) -> int:
        """Calculate final confidence score after validation."""
        if not agent_confidences:
            return 50
        
        base_confidence = sum(agent_confidences) / len(agent_confidences)
        
        # Deduct for validation issues
        for issue in validation_issues:
            if issue.get("severity") == "critical":
                base_confidence -= 20
            elif issue.get("severity") == "warning":
                base_confidence -= 10
            elif issue.get("severity") == "info":
                base_confidence -= 5
        
        # Deduct for dissent
        if dissent_detected:
            base_confidence -= 15
        
        return max(0, min(100, int(base_confidence)))
