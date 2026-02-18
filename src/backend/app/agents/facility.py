"""Facility Agent for CareNav Florida - Facility search and scoring."""
from typing import Optional
from app.agents.base import BaseAgent


class FacilityAgent(BaseAgent):
    """Agent specializing in Florida assisted living and nursing facility search."""
    
    def __init__(self):
        super().__init__(
            name="facility",
            description="Facility search, scoring, and comparison"
        )
    
    def get_system_prompt(self) -> str:
        return """You are the CareNav Facility Agent specializing in Florida assisted living and skilled nursing facilities.

YOUR DATA SOURCES:
- Florida AHCA License Database (official)
- Medicare Nursing Home Compare
- Facility information provided in context

SEARCH PARAMETERS:
When user provides location (ZIP or address):
1. Search facilities within specified radius (default 20 miles)
2. Filter by care level needed (AL, MC, SNF)
3. Filter by Medicaid acceptance
4. Sort by match score

MATCH SCORING ALGORITHM (100 points max):
- Medicaid Day 1 acceptance: +25 points
- Medicaid acceptance (with wait): +15 points
- Within budget (income covers rate): +20 points
- Care level match: +15 points
- Distance under 10 miles: +10 points
- Rating 4.0+: +10 points
- Beds available: +5 points

REQUIRED DATA PER FACILITY:
{
  "name": "string",
  "address": "string",
  "phone": "string",
  "distance_miles": number,
  "license_number": "string",
  "license_type": "ALF|SNF|AFC",
  "capacity": number,
  "beds_available": number | "call",
  "rate_low": number,
  "rate_high": number,
  "medicaid": {
    "accepts": boolean,
    "day_one": boolean,
    "private_pay_months": number | null
  },
  "care_levels": ["AL", "MC", "SNF"],
  "memory_care": boolean,
  "rating": number,
  "review_count": number,
  "last_inspection": "date",
  "violations_12mo": number,
  "amenities": ["string"],
  "match_score": number,
  "affordability": {
    "monthly_rate": number,
    "patient_income": number,
    "gap_or_surplus": number,
    "with_va": number | null
  }
}

AFFORDABILITY CALCULATION:
1. Get patient's total income (including pending VA if eligible)
2. Compare to facility base rate
3. Calculate gap or surplus
4. Flag if gap > $500/month (may need asset draw)

OUTPUT FORMAT (respond in JSON):
{
  "facilities": [facility objects],
  "search_criteria": {
    "zip_code": "string",
    "radius_miles": number,
    "care_level": "string",
    "medicaid_required": boolean
  },
  "recommendations": "string",
  "confidence": 0-100
}"""

    @staticmethod
    def calculate_match_score(
        facility: dict,
        patient_income: float,
        care_level: str,
        medicaid_required: bool = True,
        va_benefit: float = 0,
    ) -> int:
        """Calculate match score for a facility."""
        score = 0
        
        # Medicaid acceptance (25 or 15 points)
        if facility.get("medicaid_day_one"):
            score += 25
        elif facility.get("accepts_medicaid"):
            score += 15
        elif medicaid_required:
            return 0  # Disqualify if Medicaid required but not accepted
        
        # Budget match (20 points)
        rate = facility.get("rate_low", 0) or 0
        total_income = patient_income + va_benefit
        if total_income >= rate:
            score += 20
        elif total_income >= rate * 0.8:
            score += 10
        
        # Care level match (15 points)
        facility_type = facility.get("license_type", "")
        if care_level == "SNF" and facility_type == "SNF":
            score += 15
        elif care_level == "MC" and facility.get("memory_care"):
            score += 15
        elif care_level == "AL" and facility_type in ["ALF", "AFC"]:
            score += 15
        
        # Distance (10 points)
        distance = facility.get("distance_miles", 100)
        if distance <= 10:
            score += 10
        elif distance <= 20:
            score += 5
        
        # Rating (10 points)
        rating = facility.get("rating", 0) or 0
        if rating >= 4.0:
            score += 10
        elif rating >= 3.5:
            score += 5
        
        # Availability (5 points)
        if facility.get("beds_available"):
            score += 5
        
        return score

    @staticmethod
    def calculate_affordability(
        facility_rate: float,
        patient_income: float,
        va_benefit: float = 0,
    ) -> dict:
        """Calculate affordability for a facility."""
        total_income = patient_income + va_benefit
        gap = facility_rate - total_income
        
        return {
            "monthly_rate": facility_rate,
            "patient_income": patient_income,
            "va_benefit": va_benefit,
            "total_income": total_income,
            "gap_or_surplus": -gap,  # Positive = surplus, negative = gap
            "affordable": gap <= 0,
            "needs_asset_draw": gap > 500,
            "monthly_shortfall": max(0, gap),
        }

    @staticmethod
    def get_sample_facilities(zip_code: str, care_level: str) -> list[dict]:
        """Get sample Florida facilities for demo purposes."""
        # Sample facilities based on the Ted Estate research
        facilities = [
            {
                "name": "Moore Care ALF",
                "address": "123 Palm Beach Blvd, Riviera Beach, FL 33404",
                "phone": "561-555-0101",
                "license_number": "ALF-12345",
                "license_type": "ALF",
                "capacity": 6,
                "beds_available": 2,
                "rate_low": 3550,
                "rate_high": 4550,
                "accepts_medicaid": True,
                "medicaid_day_one": True,
                "private_pay_months": 0,
                "memory_care": True,
                "rating": 4.5,
                "review_count": 28,
                "violations_12_months": 0,
                "distance_miles": 3.2,
            },
            {
                "name": "Victoria Gardens ALF",
                "address": "456 Ocean Ave, West Palm Beach, FL 33401",
                "phone": "561-555-0102",
                "license_number": "ALF-12346",
                "license_type": "ALF",
                "capacity": 18,
                "beds_available": 4,
                "rate_low": 3200,
                "rate_high": 4000,
                "accepts_medicaid": True,
                "medicaid_day_one": False,
                "private_pay_months": 6,
                "memory_care": False,
                "rating": 4.2,
                "review_count": 45,
                "violations_12_months": 1,
                "distance_miles": 5.8,
            },
            {
                "name": "A Second Home ALF",
                "address": "789 Sunrise Blvd, Lake Park, FL 33403",
                "phone": "561-555-0103",
                "license_number": "ALF-12347",
                "license_type": "ALF",
                "capacity": 4,
                "beds_available": 1,
                "rate_low": 3800,
                "rate_high": 4200,
                "accepts_medicaid": True,
                "medicaid_day_one": True,
                "private_pay_months": 0,
                "memory_care": True,
                "rating": 4.8,
                "review_count": 12,
                "violations_12_months": 0,
                "distance_miles": 4.1,
            },
            {
                "name": "Discovery Village at Palm Beach Gardens",
                "address": "3000 Discovery Way, Palm Beach Gardens, FL 33410",
                "phone": "561-555-0104",
                "license_number": "ALF-12348",
                "license_type": "ALF",
                "capacity": 150,
                "beds_available": 8,
                "rate_low": 3730,
                "rate_high": 6895,
                "accepts_medicaid": False,
                "medicaid_day_one": False,
                "private_pay_months": None,
                "memory_care": True,
                "rating": 4.3,
                "review_count": 156,
                "violations_12_months": 2,
                "distance_miles": 8.5,
            },
            {
                "name": "HarborChase of Palm Beach Gardens",
                "address": "3145 Harbor Blvd, Palm Beach Gardens, FL 33410",
                "phone": "561-555-0105",
                "license_number": "ALF-12349",
                "license_type": "ALF",
                "capacity": 120,
                "beds_available": 5,
                "rate_low": 5500,
                "rate_high": 7000,
                "accepts_medicaid": False,
                "medicaid_day_one": False,
                "private_pay_months": None,
                "memory_care": True,
                "rating": 4.6,
                "review_count": 89,
                "violations_12_months": 0,
                "distance_miles": 9.2,
            },
            {
                "name": "Palm Beach SNF & Rehab",
                "address": "500 Medical Center Dr, West Palm Beach, FL 33401",
                "phone": "561-555-0106",
                "license_number": "SNF-54321",
                "license_type": "SNF",
                "capacity": 120,
                "beds_available": 12,
                "rate_low": 8500,
                "rate_high": 12000,
                "accepts_medicaid": True,
                "medicaid_day_one": True,
                "private_pay_months": 0,
                "memory_care": True,
                "skilled_nursing": True,
                "rating": 3.8,
                "review_count": 67,
                "violations_12_months": 3,
                "distance_miles": 6.0,
            },
        ]
        
        # Filter by care level
        if care_level == "SNF":
            facilities = [f for f in facilities if f.get("license_type") == "SNF"]
        elif care_level == "MC":
            facilities = [f for f in facilities if f.get("memory_care")]
        elif care_level == "AL":
            facilities = [f for f in facilities if f.get("license_type") in ["ALF", "AFC"]]
        
        return facilities
