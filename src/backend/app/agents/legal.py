"""
Legal Agent for CareNav Florida - Spend-down strategies and mistake prevention.
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from typing import Optional
from app.agents.base import BaseAgent


class LegalAgent(BaseAgent):
    """Agent specializing in Florida elder law for Medicaid planning."""
    
    def __init__(self):
        super().__init__(
            name="legal",
            description="Elder law guidance and mistake prevention"
        )
    
    def get_system_prompt(self) -> str:
        return """You are the CareNav Legal Agent specializing in Florida elder law for Medicaid planning.

CRITICAL RULES - ALWAYS ENFORCE:

NEVER DO (will create Medicaid penalties):
1. Pay debts of the DECEASED spouse - creditors cannot pursue surviving spouse for deceased's individual debts in Florida
2. Give gifts to family members during look-back period
3. Sell assets below fair market value
4. Add children's names to deeds or accounts
5. Pay for grandchildren's expenses (unless documented education tuition)
6. Make large charitable donations
7. Transfer home to children before Medicaid application
8. Cash out life insurance and give away proceeds

LEGAL SPEND-DOWN STRATEGIES (with citations):
1. Irrevocable Prepaid Funeral - FL Stat. 497.458; 42 CFR 435.725
   - Must be irrevocable, Florida-licensed funeral home
   - Up to $15,000 typical, unlimited if reasonable
   
2. Pay Applicant's Own Debts - 42 CFR 435.725
   - Credit cards, medical bills, mortgage IN APPLICANT'S NAME
   - Keep receipts for Medicaid application
   
3. Home Repairs/Modifications - 42 CFR 435.726
   - Roof, HVAC, accessibility modifications
   - Increases exempt asset value
   - Up to $25,000 typical
   
4. Medical/Dental/Vision/Hearing - 42 CFR 435.725
   - Items not covered by Medicaid later
   - Dentures, hearing aids, glasses, dental work
   - Up to $15,000 typical
   
5. Vehicle Purchase/Upgrade - 42 CFR 435.726
   - One vehicle exempt at ANY value
   - Trade up to reliable vehicle
   
6. Burial Plot & Headstone - 42 CFR 435.725(c)
   - For applicant and immediate family members
   - Up to $5,000 typical
   
7. Household Goods & Furniture - Exempt category
   - Furniture, clothing, appliances for applicant
   
8. Caregiver Agreement - FL Medicaid Manual Ch. 1640
   - MUST be written BEFORE care provided
   - Fair market rate (check local rates)
   - REQUIRES attorney review - MEDIUM RISK

SPECIAL SITUATIONS:

Deceased Spouse's Debts:
- Florida is NOT a community property state
- Surviving spouse NOT responsible for deceased's individual debts
- Joint debts remain the survivor's responsibility
- DO NOT pay deceased's credit cards, medical bills, personal loans
- Creditors may TRY to collect - refer to elder law attorney

Gift Penalty Mitigation:
- Education tuition paid directly to institution may be exempt
- Document everything: invoices, cancelled checks, school records
- Get attorney letter explaining exemption
- Penalty only applies when otherwise eligible AND in facility

OUTPUT FORMAT (respond in JSON):
{
  "guidance": "string - plain English explanation",
  "legal_basis": ["citation1", "citation2"],
  "risk_level": "low|medium|high",
  "requires_attorney": boolean,
  "warnings": ["string"],
  "action_items": [{
    "action": "string",
    "priority": "urgent|high|medium|low",
    "phone": "string" | null
  }]
}"""

    @staticmethod
    def evaluate_debt_payment(
        debt_type: str,
        debt_holder: str,
        joint_account: bool = False
    ) -> dict:
        """Evaluate whether a debt should be paid."""
        if debt_holder == "deceased_spouse" and not joint_account:
            return {
                "guidance": "DO_NOT_PAY",
                "explanation": (
                    "Florida is NOT a community property state. The surviving spouse "
                    "is NOT responsible for the deceased spouse's individual debts. "
                    "Do not pay this debt - it wastes assets needed for care."
                ),
                "legal_basis": ["Florida common law property rules"],
                "risk_level": "high",
                "warnings": [
                    "Creditors may call and pressure you - do not pay",
                    "Paying this debt reduces assets available for legal spend-down",
                    "Consult elder law attorney if creditors are aggressive"
                ]
            }
        elif debt_holder == "deceased_spouse" and joint_account:
            return {
                "guidance": "MUST_PAY",
                "explanation": (
                    "This is a joint debt. The surviving spouse remains responsible "
                    "for joint debts even after the other spouse passes."
                ),
                "legal_basis": ["Joint debt liability"],
                "risk_level": "low",
                "warnings": []
            }
        elif debt_holder == "applicant":
            return {
                "guidance": "OK_TO_PAY",
                "explanation": (
                    "Paying the applicant's own debts is a legal spend-down strategy. "
                    "Keep all receipts for the Medicaid application."
                ),
                "legal_basis": ["42 CFR 435.725"],
                "risk_level": "low",
                "warnings": []
            }
        
        return {
            "guidance": "CONSULT_ATTORNEY",
            "explanation": "Unclear debt situation - consult elder law attorney.",
            "legal_basis": [],
            "risk_level": "medium",
            "warnings": ["Get professional advice before paying"]
        }

    @staticmethod
    def get_spend_down_options(amount_to_spend: float) -> list[dict]:
        """Get recommended spend-down options for a given amount."""
        options = []
        remaining = amount_to_spend
        
        # Priority order of spend-down strategies
        strategies = [
            {
                "name": "Irrevocable Prepaid Funeral",
                "max_amount": 15000,
                "citation": "FL Stat. 497.458; 42 CFR 435.725",
                "risk": "low",
                "requires_attorney": False,
                "description": "Prepay funeral expenses at Florida-licensed funeral home. Must be irrevocable."
            },
            {
                "name": "Pay Applicant's Own Debts",
                "max_amount": remaining,  # No limit
                "citation": "42 CFR 435.725",
                "risk": "low",
                "requires_attorney": False,
                "description": "Pay credit cards, medical bills, mortgage in applicant's name. Keep receipts."
            },
            {
                "name": "Home Repairs/Modifications",
                "max_amount": 25000,
                "citation": "42 CFR 435.726",
                "risk": "low",
                "requires_attorney": False,
                "description": "Roof, HVAC, accessibility modifications. Increases exempt asset value."
            },
            {
                "name": "Medical/Dental/Vision/Hearing",
                "max_amount": 15000,
                "citation": "42 CFR 435.725",
                "risk": "low",
                "requires_attorney": False,
                "description": "Dentures, hearing aids, glasses. Items not covered by Medicaid later."
            },
            {
                "name": "Vehicle Purchase/Upgrade",
                "max_amount": 50000,
                "citation": "42 CFR 435.726",
                "risk": "low",
                "requires_attorney": False,
                "description": "One vehicle exempt at any value. Trade up to reliable vehicle."
            },
            {
                "name": "Burial Plots & Headstones",
                "max_amount": 5000,
                "citation": "42 CFR 435.725(c)",
                "risk": "low",
                "requires_attorney": False,
                "description": "For applicant and immediate family members."
            },
        ]
        
        for strategy in strategies:
            if remaining <= 0:
                break
            
            use_amount = min(remaining, strategy["max_amount"])
            options.append({
                "strategy": strategy["name"],
                "amount": use_amount,
                "citation": strategy["citation"],
                "risk": strategy["risk"],
                "requires_attorney": strategy["requires_attorney"],
                "description": strategy["description"]
            })
            remaining -= use_amount
        
        return options
