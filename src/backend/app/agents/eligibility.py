"""
Eligibility Agent for CareNav Florida - Medicaid, VA, Medicare calculations.
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from typing import Optional
from app.agents.base import BaseAgent


class EligibilityAgent(BaseAgent):
    """Agent specializing in Florida elder care benefits eligibility."""
    
    def __init__(self):
        super().__init__(
            name="eligibility",
            description="Benefits eligibility determination for Medicaid, VA, Medicare"
        )
    
    def get_system_prompt(self) -> str:
        return """You are the CareNav Eligibility Agent specializing in Florida elder care benefits.

YOUR KNOWLEDGE (cite these when answering):
- Florida Medicaid ICP: $2,000 asset limit, $2,829 income limit (2026)
- Florida look-back: 60 months for gifts/transfers
- Penalty divisor: $10,809/month (2026)
- Home equity limit: $713,000 (exempt if intending to return)
- One vehicle: Fully exempt at any value
- Prepaid funeral: Exempt if irrevocable
- VA A&A Surviving Spouse: $1,432/month (2026)
- VA A&A Veteran Single: $2,229/month (2026)
- VA A&A Veteran w/Spouse: $2,724/month (2026)
- VA Net Worth Limit: $150,538 (2026)
- VA Look-back: 36 months
- Medicare SNF: Days 1-20 $0 copay, Days 21-100 $200/day (2026)
- QMB Income Limit: $1,255/month individual (2026)

CALCULATION RULES:
1. Countable Assets = Bank + Investments + Life Insurance Cash (if face > $2,500) + 2nd vehicle
2. Exempt Assets = Home (if returning) + 1 vehicle + household goods + burial plots + prepaid funeral
3. Medicaid Eligible = Countable <= $2,000 AND Income <= $2,829
4. Gift Penalty Months = Gift Amount / $10,809 (rounded up)
5. VA Net Worth = Countable Assets + (Annual Income - Annual Medical Expenses)

OUTPUT FORMAT (respond in JSON):
{
  "medicaid": {
    "eligible": boolean,
    "countable": number,
    "over_by": number,
    "months_to_eligible": number,
    "explanation": "string"
  },
  "va_aa": {
    "eligible": boolean,
    "type": "surviving_spouse|veteran|veteran_spouse|none",
    "monthly_benefit": number,
    "explanation": "string"
  },
  "gift_penalty": {
    "has_penalty": boolean,
    "amount": number,
    "months": number,
    "mitigation": "string"
  },
  "confidence": 0-100,
  "citations": ["FL Stat. ...", "42 CFR ..."]
}"""

    @staticmethod
    def calculate_countable_assets(financials: dict) -> float:
        """Calculate countable assets for Medicaid eligibility."""
        countable = 0.0
        
        # Bank accounts
        countable += float(financials.get("checking", 0) or 0)
        countable += float(financials.get("savings", 0) or 0)
        countable += float(financials.get("cds", 0) or 0)
        countable += float(financials.get("money_market", 0) or 0)
        
        # Investments
        countable += float(financials.get("ira", 0) or 0)
        countable += float(financials.get("four01k", 0) or 0)
        countable += float(financials.get("brokerage", 0) or 0)
        countable += float(financials.get("annuities", 0) or 0)
        countable += float(financials.get("stocks", 0) or 0)
        countable += float(financials.get("bonds", 0) or 0)
        
        # Life insurance - only if face value > $2,500
        life_face = float(financials.get("life_insurance_face", 0) or 0)
        life_cash = float(financials.get("life_insurance_cash", 0) or 0)
        if life_face > 2500:
            countable += life_cash
        
        # Second vehicle
        countable += float(financials.get("vehicle_2_value", 0) or 0)
        
        return countable
    
    @staticmethod
    def calculate_exempt_assets(financials: dict) -> float:
        """Calculate exempt assets."""
        exempt = 0.0
        
        # Home (if owned)
        if financials.get("owns_home"):
            home_value = float(financials.get("home_value", 0) or 0)
            mortgage = float(financials.get("home_mortgage", 0) or 0)
            equity = home_value - mortgage
            if equity <= 713000:
                exempt += equity
        
        # First vehicle (unlimited)
        exempt += float(financials.get("vehicle_1_value", 0) or 0)
        
        # Household goods
        exempt += float(financials.get("household_goods", 0) or 0)
        
        return exempt
    
    @staticmethod
    def calculate_total_income(financials: dict) -> float:
        """Calculate total monthly income."""
        return (
            float(financials.get("social_security", 0) or 0) +
            float(financials.get("pension", 0) or 0) +
            float(financials.get("va_pension", 0) or 0) +
            float(financials.get("other_income", 0) or 0)
        )
    
    @staticmethod
    def check_medicaid_eligibility(financials: dict) -> dict:
        """Check Medicaid eligibility based on financials."""
        countable = EligibilityAgent.calculate_countable_assets(financials)
        total_income = EligibilityAgent.calculate_total_income(financials)
        
        asset_limit = 2000
        income_limit = 2829
        
        asset_eligible = countable <= asset_limit
        income_eligible = total_income <= income_limit
        
        over_by = max(0, countable - asset_limit)
        
        return {
            "eligible": asset_eligible and income_eligible,
            "countable": countable,
            "over_by": over_by,
            "asset_eligible": asset_eligible,
            "income_eligible": income_eligible,
            "total_income": total_income,
            "explanation": (
                f"Countable assets: ${countable:,.2f} (limit: $2,000). "
                f"Monthly income: ${total_income:,.2f} (limit: $2,829). "
                + ("Eligible for Medicaid." if asset_eligible and income_eligible 
                   else f"Over asset limit by ${over_by:,.2f}." if not asset_eligible
                   else "Income exceeds limit - may need Qualified Income Trust.")
            )
        }
    
    @staticmethod
    def check_va_eligibility(veteran_status: dict, financials: dict) -> dict:
        """Check VA Aid & Attendance eligibility."""
        is_veteran = veteran_status.get("is_veteran", False)
        is_spouse = veteran_status.get("is_spouse_of_veteran", False)
        veteran_deceased = veteran_status.get("veteran_deceased", False)
        wartime = veteran_status.get("wartime_service", False)
        
        if not wartime:
            return {
                "eligible": False,
                "type": "none",
                "monthly_benefit": 0,
                "explanation": "VA A&A requires wartime service. No wartime service indicated."
            }
        
        countable = EligibilityAgent.calculate_countable_assets(financials)
        net_worth_limit = 150538
        
        if countable > net_worth_limit:
            return {
                "eligible": False,
                "type": "none",
                "monthly_benefit": 0,
                "explanation": f"Net worth ${countable:,.2f} exceeds VA limit of $150,538."
            }
        
        if is_veteran:
            return {
                "eligible": True,
                "type": "veteran",
                "monthly_benefit": 2229,
                "explanation": "Veteran with wartime service qualifies for $2,229/month A&A."
            }
        elif is_spouse and veteran_deceased:
            return {
                "eligible": True,
                "type": "surviving_spouse",
                "monthly_benefit": 1432,
                "explanation": "Surviving spouse of wartime veteran qualifies for $1,432/month A&A."
            }
        elif is_spouse and not veteran_deceased:
            return {
                "eligible": True,
                "type": "veteran_spouse",
                "monthly_benefit": 2724,
                "explanation": "Spouse of living wartime veteran may qualify for $2,724/month A&A."
            }
        
        return {
            "eligible": False,
            "type": "none",
            "monthly_benefit": 0,
            "explanation": "Not a veteran or spouse of veteran with wartime service."
        }
    
    @staticmethod
    def calculate_gift_penalty(gifts: list) -> dict:
        """Calculate Medicaid gift penalty from gift history."""
        from datetime import date, timedelta
        
        penalty_divisor = 10809
        lookback_months = 60
        lookback_date = date.today() - timedelta(days=lookback_months * 30)
        
        total_penalty_amount = 0
        for gift in gifts:
            gift_date = gift.get("gift_date")
            if gift_date and gift_date >= lookback_date:
                if not gift.get("potentially_exempt", False):
                    total_penalty_amount += float(gift.get("amount", 0) or 0)
        
        if total_penalty_amount > 0:
            penalty_months = -(-int(total_penalty_amount) // penalty_divisor)  # Ceiling division
            return {
                "has_penalty": True,
                "amount": total_penalty_amount,
                "months": penalty_months,
                "mitigation": (
                    "Penalty period begins when otherwise eligible and in facility. "
                    "Consult elder law attorney for potential mitigation strategies."
                )
            }
        
        return {
            "has_penalty": False,
            "amount": 0,
            "months": 0,
            "mitigation": "No gift penalty detected."
        }
