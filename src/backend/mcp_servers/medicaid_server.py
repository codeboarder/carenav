# Built by Gregory Katz and Rick Weyenberg
# Code is as-is, open source

"""
Medicaid MCP Server for CareNav Florida.

This server provides tools for Florida Medicaid ICP eligibility calculations,
spend-down strategies, and look-back period analysis.

Tools:
- check_medicaid_eligibility: Check eligibility based on assets and income
- get_medicaid_rules: Get current Florida Medicaid rules and limits
- calculate_spend_down: Calculate spend-down amount and strategies
- check_look_back_violations: Check for potential look-back violations
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List, Dict, Any


# 2024/2025 Florida Medicaid ICP Limits
MEDICAID_LIMITS = {
    2024: {
        "asset_limit_single": 2000,
        "asset_limit_married_community_spouse": 154140,  # CSRA max
        "asset_limit_married_minimum": 30828,  # CSRA min
        "income_limit_sil": 2829,  # Special Income Level (300% of SSI)
        "personal_needs_allowance": 160,
        "home_equity_limit": 713000,
        "look_back_period_months": 60,
    },
    2025: {
        "asset_limit_single": 2000,
        "asset_limit_married_community_spouse": 157920,  # CSRA max (estimated)
        "asset_limit_married_minimum": 31584,  # CSRA min (estimated)
        "income_limit_sil": 2901,  # Special Income Level (estimated)
        "personal_needs_allowance": 165,
        "home_equity_limit": 730000,
        "look_back_period_months": 60,
    },
}

# Exempt assets that don't count toward the limit
EXEMPT_ASSETS = [
    "Primary residence (up to equity limit)",
    "One vehicle (any value)",
    "Household goods and personal effects",
    "Burial plots for immediate family",
    "Irrevocable burial trust (up to $2,500)",
    "Term life insurance (no cash value)",
    "Whole life insurance (face value up to $2,500)",
]

# Legal spend-down strategies
SPEND_DOWN_STRATEGIES = [
    {
        "name": "Prepaid Funeral/Burial",
        "description": "Purchase irrevocable prepaid funeral and burial plans",
        "max_amount": 15000,
        "priority": 1,
    },
    {
        "name": "Home Modifications",
        "description": "Accessibility modifications (ramps, grab bars, stair lifts)",
        "max_amount": 25000,
        "priority": 2,
    },
    {
        "name": "Vehicle Purchase/Upgrade",
        "description": "Purchase or upgrade to one exempt vehicle",
        "max_amount": 50000,
        "priority": 3,
    },
    {
        "name": "Debt Payoff",
        "description": "Pay off mortgage, credit cards, medical bills",
        "max_amount": None,
        "priority": 4,
    },
    {
        "name": "Home Repairs",
        "description": "Necessary repairs to primary residence",
        "max_amount": 30000,
        "priority": 5,
    },
    {
        "name": "Medical Equipment",
        "description": "Wheelchair, hospital bed, medical supplies",
        "max_amount": 10000,
        "priority": 6,
    },
    {
        "name": "Caregiver Agreement",
        "description": "Documented payment to family caregiver for past care",
        "max_amount": None,
        "priority": 7,
        "note": "Must be documented with written agreement and fair market value",
    },
]


@dataclass
class EligibilityResult:
    """Result of a Medicaid eligibility check."""
    eligible: bool
    spend_down_needed: float
    asset_limit: float
    current_assets: float
    income_eligible: bool
    income_limit: float
    current_income: float
    notes: List[str]


@dataclass
class SpendDownPlan:
    """A spend-down plan with prioritized strategies."""
    total_to_spend: float
    strategies: List[Dict[str, Any]]
    estimated_timeline_days: int
    warnings: List[str]


class MedicaidServer:
    """
    MCP Server for Florida Medicaid ICP tools.
    
    This class provides the implementation for Medicaid-related tools
    that will be registered with the GitHub Copilot SDK.
    """
    
    def __init__(self):
        self.current_year = datetime.now().year
        if self.current_year not in MEDICAID_LIMITS:
            self.current_year = max(MEDICAID_LIMITS.keys())
    
    def check_medicaid_eligibility(
        self,
        assets: float,
        income: float,
        marital_status: str = "single",
        spouse_assets: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Check Florida Medicaid ICP eligibility based on assets and income.
        
        Args:
            assets: Total countable assets in dollars
            income: Monthly gross income in dollars
            marital_status: "single", "married", or "widowed"
            spouse_assets: Spouse's countable assets (for CSRA calculation)
        
        Returns:
            Dict with eligibility status, spend-down amount, and notes
        """
        limits = MEDICAID_LIMITS[self.current_year]
        notes = []
        
        # Determine asset limit based on marital status
        if marital_status == "married" and spouse_assets is not None:
            # Calculate Community Spouse Resource Allowance (CSRA)
            total_assets = assets + spouse_assets
            csra = min(
                max(total_assets / 2, limits["asset_limit_married_minimum"]),
                limits["asset_limit_married_community_spouse"]
            )
            asset_limit = limits["asset_limit_single"]  # Applicant's limit
            notes.append(f"Community Spouse Resource Allowance (CSRA): ${csra:,.2f}")
            notes.append(f"Spouse can keep up to ${csra:,.2f} in assets")
        else:
            asset_limit = limits["asset_limit_single"]
        
        # Check asset eligibility
        asset_eligible = assets <= asset_limit
        spend_down_needed = max(0, assets - asset_limit)
        
        # Check income eligibility
        income_limit = limits["income_limit_sil"]
        income_eligible = income <= income_limit
        
        if not income_eligible:
            notes.append(
                f"Income exceeds Special Income Level (${income_limit:,.2f}/month). "
                "A Qualified Income Trust (Miller Trust) may be required."
            )
        
        # Overall eligibility
        eligible = asset_eligible and income_eligible
        
        if spend_down_needed > 0:
            notes.append(
                f"Spend-down of ${spend_down_needed:,.2f} required to meet asset limit."
            )
        
        return {
            "eligible": eligible,
            "spend_down_needed": spend_down_needed,
            "asset_limit": asset_limit,
            "current_assets": assets,
            "asset_eligible": asset_eligible,
            "income_eligible": income_eligible,
            "income_limit": income_limit,
            "current_income": income,
            "notes": notes,
            "year": self.current_year,
        }
    
    def get_medicaid_rules(
        self,
        year: Optional[int] = None,
        rule_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get current Florida Medicaid ICP rules and limits.
        
        Args:
            year: Year for rules (defaults to current year)
            rule_type: Type of rule to retrieve (asset_limits, income_limits, 
                      look_back, exempt_assets, csra)
        
        Returns:
            Dict with requested rules and limits
        """
        year = year or self.current_year
        if year not in MEDICAID_LIMITS:
            year = max(MEDICAID_LIMITS.keys())
        
        limits = MEDICAID_LIMITS[year]
        
        rules = {
            "year": year,
            "asset_limits": {
                "single": limits["asset_limit_single"],
                "married_csra_max": limits["asset_limit_married_community_spouse"],
                "married_csra_min": limits["asset_limit_married_minimum"],
            },
            "income_limits": {
                "special_income_level": limits["income_limit_sil"],
                "personal_needs_allowance": limits["personal_needs_allowance"],
            },
            "look_back": {
                "period_months": limits["look_back_period_months"],
                "period_years": limits["look_back_period_months"] / 12,
            },
            "exempt_assets": EXEMPT_ASSETS,
            "home_equity_limit": limits["home_equity_limit"],
        }
        
        if rule_type:
            return {rule_type: rules.get(rule_type, "Unknown rule type")}
        
        return rules
    
    def calculate_spend_down(
        self,
        current_assets: float,
        target_limit: Optional[float] = None,
        patient_needs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate spend-down amount and suggest legal strategies.
        
        Args:
            current_assets: Current countable assets in dollars
            target_limit: Target asset limit (defaults to $2,000)
            patient_needs: List of patient needs that could justify spend-down
        
        Returns:
            Dict with spend-down plan and prioritized strategies
        """
        limits = MEDICAID_LIMITS[self.current_year]
        target_limit = target_limit or limits["asset_limit_single"]
        
        spend_down_amount = max(0, current_assets - target_limit)
        
        if spend_down_amount == 0:
            return {
                "spend_down_needed": False,
                "current_assets": current_assets,
                "target_limit": target_limit,
                "message": "No spend-down required. Assets are within Medicaid limits.",
            }
        
        # Build prioritized strategy list
        strategies = []
        remaining = spend_down_amount
        
        for strategy in sorted(SPEND_DOWN_STRATEGIES, key=lambda x: x["priority"]):
            if remaining <= 0:
                break
            
            max_amount = strategy.get("max_amount") or remaining
            amount = min(remaining, max_amount)
            
            strategies.append({
                "name": strategy["name"],
                "description": strategy["description"],
                "suggested_amount": amount,
                "priority": strategy["priority"],
                "note": strategy.get("note"),
            })
            
            remaining -= amount
        
        warnings = []
        if remaining > 0:
            warnings.append(
                f"${remaining:,.2f} remaining after all strategies. "
                "Consider consulting an elder law attorney for additional options."
            )
        
        # Estimate timeline (rough estimate: 30-90 days)
        estimated_days = min(90, max(30, int(spend_down_amount / 1000)))
        
        return {
            "spend_down_needed": True,
            "total_to_spend": spend_down_amount,
            "current_assets": current_assets,
            "target_limit": target_limit,
            "strategies": strategies,
            "estimated_timeline_days": estimated_days,
            "warnings": warnings,
        }
    
    def check_look_back_violations(
        self,
        transfers: List[Dict[str, Any]],
        application_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check for potential Medicaid look-back period violations.
        
        Args:
            transfers: List of asset transfers with amount, date, recipient, purpose
            application_date: Planned Medicaid application date (ISO format)
        
        Returns:
            Dict with violation analysis and penalty period calculation
        """
        limits = MEDICAID_LIMITS[self.current_year]
        look_back_months = limits["look_back_period_months"]
        
        if application_date:
            app_date = datetime.fromisoformat(application_date).date()
        else:
            app_date = date.today()
        
        # Calculate look-back start date
        look_back_start = date(
            app_date.year - (look_back_months // 12),
            app_date.month,
            app_date.day
        )
        
        violations = []
        total_penalty = 0
        
        # Average monthly cost of nursing home care in Florida (for penalty calculation)
        avg_monthly_cost = 10000  # Approximate
        
        for transfer in transfers:
            transfer_date = datetime.fromisoformat(transfer["date"]).date()
            
            if transfer_date >= look_back_start:
                # This transfer is within the look-back period
                amount = transfer["amount"]
                
                # Check if it's an exempt transfer
                exempt = False
                purpose = transfer.get("purpose", "").lower()
                recipient = transfer.get("recipient", "").lower()
                
                # Exempt transfers
                if "spouse" in recipient:
                    exempt = True
                    reason = "Transfer to spouse is exempt"
                elif "disabled child" in recipient:
                    exempt = True
                    reason = "Transfer to disabled child is exempt"
                elif "caretaker child" in recipient and "lived in home" in purpose:
                    exempt = True
                    reason = "Transfer to caretaker child who lived in home may be exempt"
                elif amount < 100:
                    exempt = True
                    reason = "De minimis transfer"
                
                if not exempt:
                    # Calculate penalty period
                    penalty_months = amount / avg_monthly_cost
                    total_penalty += penalty_months
                    
                    violations.append({
                        "date": transfer["date"],
                        "amount": amount,
                        "recipient": transfer.get("recipient"),
                        "purpose": transfer.get("purpose"),
                        "penalty_months": round(penalty_months, 1),
                        "exempt": False,
                    })
                else:
                    violations.append({
                        "date": transfer["date"],
                        "amount": amount,
                        "recipient": transfer.get("recipient"),
                        "purpose": transfer.get("purpose"),
                        "exempt": True,
                        "exempt_reason": reason,
                    })
        
        has_violations = any(not v.get("exempt", False) for v in violations)
        
        return {
            "has_violations": has_violations,
            "look_back_start_date": look_back_start.isoformat(),
            "application_date": app_date.isoformat(),
            "look_back_period_months": look_back_months,
            "transfers_analyzed": len(transfers),
            "violations": violations,
            "total_penalty_months": round(total_penalty, 1),
            "penalty_end_date": (
                date(
                    app_date.year,
                    app_date.month + int(total_penalty) % 12,
                    app_date.day
                ).isoformat()
                if has_violations else None
            ),
            "recommendations": [
                "Consult with an elder law attorney to review transfer details",
                "Gather documentation for any transfers that may qualify for exemption",
                "Consider delaying application if penalty period is significant",
            ] if has_violations else [
                "No look-back violations detected",
                "Proceed with Medicaid application",
            ],
        }


# For running as MCP server
if __name__ == "__main__":
    import json
    import sys
    
    server = MedicaidServer()
    
    # Simple JSON-RPC style interface for MCP
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "check_medicaid_eligibility":
                result = server.check_medicaid_eligibility(**params)
            elif method == "get_medicaid_rules":
                result = server.get_medicaid_rules(**params)
            elif method == "calculate_spend_down":
                result = server.calculate_spend_down(**params)
            elif method == "check_look_back_violations":
                result = server.check_look_back_violations(**params)
            else:
                result = {"error": f"Unknown method: {method}"}
            
            print(json.dumps({"id": request.get("id"), "result": result}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
