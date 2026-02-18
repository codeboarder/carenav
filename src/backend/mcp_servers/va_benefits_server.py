"""
VA Benefits MCP Server for CareNav Florida.

This server provides tools for VA Aid & Attendance eligibility calculations,
benefit amount estimation, and required documentation guidance.

Tools:
- check_va_eligibility: Check VA A&A eligibility for veteran or surviving spouse
- calculate_va_benefit: Calculate maximum benefit amount
- get_required_documents: Get list of required documents for application
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List, Dict, Any


# 2024/2025 VA Aid & Attendance Limits and Benefits
VA_LIMITS = {
    2024: {
        "net_worth_limit": 150538,
        "look_back_period_months": 36,
        "max_benefit_veteran_single": 2431,
        "max_benefit_veteran_married": 2879,
        "max_benefit_surviving_spouse": 1318,
        "max_benefit_veteran_with_dependent": 2879,
    },
    2025: {
        "net_worth_limit": 155000,  # Estimated
        "look_back_period_months": 36,
        "max_benefit_veteran_single": 2500,  # Estimated
        "max_benefit_veteran_married": 2960,  # Estimated
        "max_benefit_surviving_spouse": 1355,  # Estimated
        "max_benefit_veteran_with_dependent": 2960,  # Estimated
    },
}

# Wartime periods for VA benefits eligibility
WARTIME_PERIODS = [
    {"name": "World War II", "start": "1941-12-07", "end": "1946-12-31"},
    {"name": "Korean War", "start": "1950-06-27", "end": "1955-01-31"},
    {"name": "Vietnam War", "start": "1961-02-28", "end": "1975-05-07"},  # Extended for in-country
    {"name": "Gulf War", "start": "1990-08-02", "end": None},  # Ongoing
]

# Required documents by beneficiary type
REQUIRED_DOCUMENTS = {
    "veteran": [
        {
            "name": "DD-214",
            "description": "Certificate of Release or Discharge from Active Duty",
            "required": True,
            "alternatives": ["Military service records from National Archives"],
        },
        {
            "name": "VA Form 21-2680",
            "description": "Examination for Housebound Status or Permanent Need for Regular Aid and Attendance",
            "required": True,
            "note": "Must be completed by a licensed physician",
        },
        {
            "name": "VA Form 21-534EZ",
            "description": "Application for DIC, Death Pension, and/or Accrued Benefits",
            "required": True,
        },
        {
            "name": "Medical Records",
            "description": "Documentation of medical conditions requiring assistance",
            "required": True,
        },
        {
            "name": "Financial Information",
            "description": "Bank statements, income documentation, asset statements",
            "required": True,
        },
        {
            "name": "Care Facility Invoice",
            "description": "Monthly invoice from assisted living or care facility",
            "required": False,
            "note": "Required if claiming unreimbursed medical expenses",
        },
    ],
    "surviving_spouse": [
        {
            "name": "DD-214",
            "description": "Veteran's Certificate of Release or Discharge",
            "required": True,
            "alternatives": ["Military service records from National Archives"],
        },
        {
            "name": "Marriage Certificate",
            "description": "Proof of marriage to the veteran",
            "required": True,
        },
        {
            "name": "Death Certificate",
            "description": "Veteran's death certificate",
            "required": True,
        },
        {
            "name": "VA Form 21-2680",
            "description": "Examination for Housebound Status or Permanent Need for Regular Aid and Attendance",
            "required": True,
            "note": "Must be completed by a licensed physician",
        },
        {
            "name": "VA Form 21-534EZ",
            "description": "Application for DIC, Death Pension, and/or Accrued Benefits",
            "required": True,
        },
        {
            "name": "Financial Information",
            "description": "Bank statements, income documentation, asset statements",
            "required": True,
        },
    ],
}


@dataclass
class VAEligibilityResult:
    """Result of a VA eligibility check."""
    eligible: bool
    beneficiary_type: str
    max_monthly_benefit: float
    net_worth_eligible: bool
    wartime_service_verified: bool
    notes: List[str]


class VABenefitsServer:
    """
    MCP Server for VA Aid & Attendance tools.
    
    This class provides the implementation for VA benefits-related tools
    that will be registered with the GitHub Copilot SDK.
    """
    
    def __init__(self):
        self.current_year = datetime.now().year
        if self.current_year not in VA_LIMITS:
            self.current_year = max(VA_LIMITS.keys())
    
    def check_va_eligibility(
        self,
        is_veteran: bool = False,
        is_spouse_of_veteran: bool = False,
        wartime_service: bool = False,
        veteran_deceased: bool = False,
        service_connected_disability: bool = False,
        net_worth: Optional[float] = None,
        service_dates: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Check VA Aid & Attendance eligibility.
        
        Args:
            is_veteran: Is the applicant a veteran?
            is_spouse_of_veteran: Is the applicant a spouse of a veteran?
            wartime_service: Did the veteran serve during a wartime period?
            veteran_deceased: Is the veteran deceased?
            service_connected_disability: Does the veteran have a service-connected disability?
            net_worth: Total net worth in dollars
            service_dates: Dict with "start" and "end" dates of service
        
        Returns:
            Dict with eligibility status and benefit information
        """
        limits = VA_LIMITS[self.current_year]
        notes = []
        
        # Determine beneficiary type
        if is_veteran and not veteran_deceased:
            beneficiary_type = "veteran"
        elif is_spouse_of_veteran and veteran_deceased:
            beneficiary_type = "surviving_spouse"
        elif is_spouse_of_veteran and not veteran_deceased:
            beneficiary_type = "veteran_spouse"
            notes.append("Spouse of living veteran - veteran must apply")
        else:
            return {
                "eligible": False,
                "beneficiary_type": "unknown",
                "reason": "Must be a veteran or surviving spouse of a veteran",
                "notes": ["Neither veteran nor surviving spouse status confirmed"],
            }
        
        # Check wartime service requirement
        wartime_verified = False
        wartime_period_name = None
        
        if wartime_service:
            wartime_verified = True
            notes.append("Wartime service confirmed by user")
        elif service_dates:
            # Verify against wartime periods
            start = datetime.fromisoformat(service_dates.get("start", "")).date()
            end = datetime.fromisoformat(service_dates.get("end", "")).date()
            
            for period in WARTIME_PERIODS:
                period_start = datetime.fromisoformat(period["start"]).date()
                period_end = (
                    datetime.fromisoformat(period["end"]).date()
                    if period["end"]
                    else date.today()
                )
                
                # Check if service overlaps with wartime period
                if start <= period_end and end >= period_start:
                    wartime_verified = True
                    wartime_period_name = period["name"]
                    notes.append(f"Service during {period['name']} verified")
                    break
        
        if not wartime_verified:
            notes.append(
                "Wartime service not verified. Veteran must have served during a "
                "recognized wartime period (WWII, Korea, Vietnam, or Gulf War)."
            )
        
        # Check net worth limit
        net_worth_eligible = True
        if net_worth is not None:
            net_worth_limit = limits["net_worth_limit"]
            net_worth_eligible = net_worth <= net_worth_limit
            
            if not net_worth_eligible:
                excess = net_worth - net_worth_limit
                notes.append(
                    f"Net worth (${net_worth:,.2f}) exceeds limit (${net_worth_limit:,.2f}) "
                    f"by ${excess:,.2f}. Spend-down may be required."
                )
        
        # Determine maximum benefit
        if beneficiary_type == "veteran":
            max_benefit = limits["max_benefit_veteran_single"]
        elif beneficiary_type == "surviving_spouse":
            max_benefit = limits["max_benefit_surviving_spouse"]
        else:
            max_benefit = 0
        
        # Overall eligibility
        eligible = wartime_verified and net_worth_eligible and beneficiary_type in ["veteran", "surviving_spouse"]
        
        if service_connected_disability:
            notes.append(
                "Service-connected disability may qualify for additional VA benefits. "
                "Consider applying for VA disability compensation as well."
            )
        
        return {
            "eligible": eligible,
            "beneficiary_type": beneficiary_type,
            "max_monthly_benefit": max_benefit,
            "wartime_service_verified": wartime_verified,
            "wartime_period": wartime_period_name,
            "net_worth_eligible": net_worth_eligible,
            "net_worth_limit": limits["net_worth_limit"],
            "look_back_period_months": limits["look_back_period_months"],
            "notes": notes,
            "year": self.current_year,
        }
    
    def calculate_va_benefit(
        self,
        beneficiary_type: str,
        care_costs: Optional[float] = None,
        current_income: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculate the VA Aid & Attendance benefit amount.
        
        Args:
            beneficiary_type: "veteran_single", "veteran_married", or "surviving_spouse"
            care_costs: Monthly unreimbursed care costs
            current_income: Current monthly income
        
        Returns:
            Dict with benefit calculation details
        """
        limits = VA_LIMITS[self.current_year]
        
        # Get maximum benefit based on type
        benefit_map = {
            "veteran_single": limits["max_benefit_veteran_single"],
            "veteran_married": limits["max_benefit_veteran_married"],
            "surviving_spouse": limits["max_benefit_surviving_spouse"],
            "veteran_with_dependent": limits["max_benefit_veteran_with_dependent"],
        }
        
        max_benefit = benefit_map.get(beneficiary_type, 0)
        
        if max_benefit == 0:
            return {
                "error": f"Unknown beneficiary type: {beneficiary_type}",
                "valid_types": list(benefit_map.keys()),
            }
        
        # Calculate estimated benefit
        # VA A&A is calculated as: Max Benefit - (Income - Unreimbursed Medical Expenses)
        estimated_benefit = max_benefit
        calculation_notes = []
        
        if current_income is not None and care_costs is not None:
            # Unreimbursed medical expenses reduce countable income
            adjusted_income = max(0, current_income - care_costs)
            estimated_benefit = max(0, max_benefit - adjusted_income)
            
            calculation_notes.append(f"Gross income: ${current_income:,.2f}/month")
            calculation_notes.append(f"Unreimbursed care costs: ${care_costs:,.2f}/month")
            calculation_notes.append(f"Adjusted income: ${adjusted_income:,.2f}/month")
            calculation_notes.append(f"Maximum benefit: ${max_benefit:,.2f}/month")
            calculation_notes.append(f"Estimated benefit: ${estimated_benefit:,.2f}/month")
        else:
            calculation_notes.append(
                "Provide income and care costs for accurate benefit calculation"
            )
        
        return {
            "beneficiary_type": beneficiary_type,
            "max_monthly_benefit": max_benefit,
            "estimated_monthly_benefit": estimated_benefit,
            "annual_benefit": estimated_benefit * 12,
            "calculation_notes": calculation_notes,
            "year": self.current_year,
            "disclaimer": (
                "This is an estimate only. Actual benefit amount is determined by the VA "
                "based on your complete application and supporting documentation."
            ),
        }
    
    def get_required_documents(
        self,
        beneficiary_type: str,
        has_dd214: bool = False,
    ) -> Dict[str, Any]:
        """
        Get list of required documents for VA A&A application.
        
        Args:
            beneficiary_type: "veteran" or "surviving_spouse"
            has_dd214: Does the applicant already have the DD-214?
        
        Returns:
            Dict with required documents and guidance
        """
        if beneficiary_type not in REQUIRED_DOCUMENTS:
            return {
                "error": f"Unknown beneficiary type: {beneficiary_type}",
                "valid_types": list(REQUIRED_DOCUMENTS.keys()),
            }
        
        documents = REQUIRED_DOCUMENTS[beneficiary_type]
        
        # Mark DD-214 status
        doc_list = []
        for doc in documents:
            doc_info = doc.copy()
            if doc["name"] == "DD-214":
                doc_info["status"] = "obtained" if has_dd214 else "needed"
                if not has_dd214:
                    doc_info["how_to_obtain"] = (
                        "Request from National Archives at www.archives.gov/veterans "
                        "or call 1-866-272-6272. Processing time: 2-4 weeks."
                    )
            else:
                doc_info["status"] = "needed"
            doc_list.append(doc_info)
        
        # Add guidance
        guidance = [
            "Gather all documents before starting the application",
            "VA Form 21-2680 must be completed by a licensed physician within 6 months",
            "Include 12 months of bank statements for financial verification",
            "Keep copies of all submitted documents",
        ]
        
        if beneficiary_type == "surviving_spouse":
            guidance.append("Marriage must have lasted at least 1 year OR resulted in children")
        
        return {
            "beneficiary_type": beneficiary_type,
            "documents": doc_list,
            "total_required": len([d for d in doc_list if d.get("required", False)]),
            "guidance": guidance,
            "application_methods": [
                {
                    "method": "Online",
                    "url": "https://www.va.gov/pension/aid-attendance-housebound/",
                    "note": "Fastest method, requires VA.gov account",
                },
                {
                    "method": "Mail",
                    "address": "Department of Veterans Affairs, Pension Intake Center, PO Box 5365, Janesville, WI 53547-5365",
                    "note": "Processing time: 3-6 months",
                },
                {
                    "method": "In Person",
                    "location": "Local VA Regional Office",
                    "note": "Find your nearest office at va.gov/find-locations",
                },
            ],
        }


# For running as MCP server
if __name__ == "__main__":
    import json
    import sys
    
    server = VABenefitsServer()
    
    # Simple JSON-RPC style interface for MCP
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "check_va_eligibility":
                result = server.check_va_eligibility(**params)
            elif method == "calculate_va_benefit":
                result = server.calculate_va_benefit(**params)
            elif method == "get_required_documents":
                result = server.get_required_documents(**params)
            else:
                result = {"error": f"Unknown method: {method}"}
            
            print(json.dumps({"id": request.get("id"), "result": result}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
