# Built by Gregory Katz and Rick Weyenberg
# Code is as-is, open source

"""
Facility Search MCP Server for CareNav Florida.

This server provides tools for searching and comparing Florida care facilities
including assisted living, memory care, and skilled nursing facilities.

Tools:
- search_facilities: Search for facilities matching criteria
- compare_facilities: Compare multiple facilities side-by-side
- check_admission_requirements: Check if patient meets admission requirements
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import math


# Sample Florida facility data (in production, this would come from AHCA database)
SAMPLE_FACILITIES = [
    {
        "id": "FL-ALF-001",
        "name": "Sunrise Senior Living of Palm Beach",
        "type": "AL",
        "address": "2500 N Ocean Blvd, Palm Beach, FL 33480",
        "zip_code": "33480",
        "phone": "(561) 555-0101",
        "rating": 4.5,
        "medicaid_accepted": True,
        "medicaid_beds_available": 5,
        "private_pay_rate": 5500,
        "medicaid_rate": 3200,
        "capacity": 120,
        "current_occupancy": 95,
        "specialized_care": ["dementia", "diabetes"],
        "amenities": ["24/7 nursing", "physical therapy", "activities program", "transportation"],
        "last_inspection": "2025-08-15",
        "inspection_rating": "A",
        "lat": 26.7056,
        "lon": -80.0364,
    },
    {
        "id": "FL-MC-001",
        "name": "Palm Beach Memory Care Center",
        "type": "MC",
        "address": "1800 S Dixie Hwy, West Palm Beach, FL 33401",
        "zip_code": "33401",
        "phone": "(561) 555-0102",
        "rating": 4.8,
        "medicaid_accepted": True,
        "medicaid_beds_available": 3,
        "private_pay_rate": 7500,
        "medicaid_rate": 4500,
        "capacity": 60,
        "current_occupancy": 55,
        "specialized_care": ["alzheimers", "dementia", "wandering prevention"],
        "amenities": ["secured unit", "memory programs", "family support groups", "respite care"],
        "last_inspection": "2025-09-20",
        "inspection_rating": "A",
        "lat": 26.6851,
        "lon": -80.0534,
    },
    {
        "id": "FL-SNF-001",
        "name": "Wellington Skilled Nursing & Rehabilitation",
        "type": "SNF",
        "address": "3000 State Road 7, Wellington, FL 33449",
        "zip_code": "33449",
        "phone": "(561) 555-0103",
        "rating": 4.2,
        "medicaid_accepted": True,
        "medicaid_beds_available": 10,
        "private_pay_rate": 9500,
        "medicaid_rate": 6000,
        "capacity": 150,
        "current_occupancy": 130,
        "specialized_care": ["rehabilitation", "wound care", "IV therapy", "ventilator"],
        "amenities": ["24/7 skilled nursing", "physical therapy", "occupational therapy", "speech therapy"],
        "last_inspection": "2025-07-10",
        "inspection_rating": "B",
        "lat": 26.6618,
        "lon": -80.2684,
    },
    {
        "id": "FL-ALF-002",
        "name": "Brookdale Boynton Beach",
        "type": "AL",
        "address": "4800 N Congress Ave, Boynton Beach, FL 33426",
        "zip_code": "33426",
        "phone": "(561) 555-0104",
        "rating": 4.0,
        "medicaid_accepted": False,
        "medicaid_beds_available": 0,
        "private_pay_rate": 4800,
        "medicaid_rate": None,
        "capacity": 100,
        "current_occupancy": 85,
        "specialized_care": ["diabetes", "heart conditions"],
        "amenities": ["restaurant-style dining", "fitness center", "salon", "library"],
        "last_inspection": "2025-06-05",
        "inspection_rating": "A",
        "lat": 26.5317,
        "lon": -80.0834,
    },
    {
        "id": "FL-MC-002",
        "name": "Arden Courts Memory Care - Delray Beach",
        "type": "MC",
        "address": "6700 W Atlantic Ave, Delray Beach, FL 33446",
        "zip_code": "33446",
        "phone": "(561) 555-0105",
        "rating": 4.6,
        "medicaid_accepted": True,
        "medicaid_beds_available": 2,
        "private_pay_rate": 8200,
        "medicaid_rate": 5000,
        "capacity": 48,
        "current_occupancy": 45,
        "specialized_care": ["alzheimers", "dementia", "behavioral support"],
        "amenities": ["secured outdoor areas", "life skills stations", "music therapy", "pet therapy"],
        "last_inspection": "2025-10-01",
        "inspection_rating": "A",
        "lat": 26.4615,
        "lon": -80.1284,
    },
]

# Care level descriptions
CARE_LEVELS = {
    "AL": {
        "name": "Assisted Living",
        "description": "Help with activities of daily living (ADLs), medication management, meals",
        "typical_services": ["Medication management", "Meal preparation", "Housekeeping", "Personal care assistance"],
        "typical_cost_range": "$3,500 - $7,000/month",
    },
    "MC": {
        "name": "Memory Care",
        "description": "Specialized care for dementia and Alzheimer's patients in a secured environment",
        "typical_services": ["24/7 supervision", "Secured environment", "Memory programs", "Behavioral support"],
        "typical_cost_range": "$5,000 - $10,000/month",
    },
    "SNF": {
        "name": "Skilled Nursing Facility",
        "description": "24/7 medical care, rehabilitation services, complex medical needs",
        "typical_services": ["24/7 nursing care", "Physical therapy", "IV therapy", "Wound care"],
        "typical_cost_range": "$7,000 - $12,000/month",
    },
}


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in miles using Haversine formula."""
    R = 3959  # Earth's radius in miles
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


# ZIP code to coordinates (sample data for Palm Beach County)
ZIP_COORDINATES = {
    "33480": (26.7056, -80.0364),  # Palm Beach
    "33401": (26.7153, -80.0534),  # West Palm Beach
    "33449": (26.6618, -80.2684),  # Wellington
    "33426": (26.5317, -80.0834),  # Boynton Beach
    "33446": (26.4615, -80.1284),  # Delray Beach
    "33458": (26.9342, -80.0942),  # Jupiter
    "33467": (26.6276, -80.1456),  # Lake Worth
}


class FacilitySearchServer:
    """
    MCP Server for facility search tools.
    
    This class provides the implementation for facility search-related tools
    that will be registered with the GitHub Copilot SDK.
    """
    
    def __init__(self):
        self.facilities = SAMPLE_FACILITIES
    
    def search_facilities(
        self,
        zip_code: str,
        care_level: str,
        medicaid_required: bool = False,
        max_distance_miles: float = 25.0,
        min_rating: float = 0.0,
        specialized_care: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search for care facilities matching specified criteria.
        
        Args:
            zip_code: Center ZIP code for search
            care_level: Care level (AL, MC, SNF)
            medicaid_required: Must facility accept Medicaid?
            max_distance_miles: Maximum distance from ZIP code
            min_rating: Minimum star rating (1-5)
            specialized_care: Required specialized care types
        
        Returns:
            Dict with matching facilities and search metadata
        """
        # Get coordinates for ZIP code
        if zip_code not in ZIP_COORDINATES:
            # Default to West Palm Beach if ZIP not found
            center_coords = ZIP_COORDINATES.get("33401", (26.7153, -80.0534))
        else:
            center_coords = ZIP_COORDINATES[zip_code]
        
        # Filter facilities
        matching = []
        for facility in self.facilities:
            # Check care level
            if facility["type"] != care_level:
                continue
            
            # Check Medicaid requirement
            if medicaid_required and not facility["medicaid_accepted"]:
                continue
            
            if medicaid_required and facility["medicaid_beds_available"] == 0:
                continue
            
            # Check rating
            if facility["rating"] < min_rating:
                continue
            
            # Check specialized care
            if specialized_care:
                facility_care = set(facility.get("specialized_care", []))
                required_care = set(specialized_care)
                if not required_care.issubset(facility_care):
                    continue
            
            # Calculate distance
            distance = calculate_distance(
                center_coords[0], center_coords[1],
                facility["lat"], facility["lon"]
            )
            
            if distance > max_distance_miles:
                continue
            
            # Add to results with distance
            result = facility.copy()
            result["distance_miles"] = round(distance, 1)
            matching.append(result)
        
        # Sort by distance
        matching.sort(key=lambda x: x["distance_miles"])
        
        # Get care level info
        care_info = CARE_LEVELS.get(care_level, {})
        
        return {
            "search_criteria": {
                "zip_code": zip_code,
                "care_level": care_level,
                "care_level_name": care_info.get("name", care_level),
                "medicaid_required": medicaid_required,
                "max_distance_miles": max_distance_miles,
                "min_rating": min_rating,
                "specialized_care": specialized_care,
            },
            "results_count": len(matching),
            "facilities": matching,
            "care_level_info": care_info,
            "search_center": {
                "zip_code": zip_code,
                "coordinates": center_coords,
            },
        }
    
    def compare_facilities(
        self,
        facility_ids: List[str],
        comparison_factors: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare multiple facilities side-by-side.
        
        Args:
            facility_ids: List of facility IDs to compare
            comparison_factors: Factors to compare (cost, rating, staff_ratio, amenities)
        
        Returns:
            Dict with side-by-side comparison
        """
        if not comparison_factors:
            comparison_factors = ["cost", "rating", "medicaid", "capacity", "amenities"]
        
        # Find facilities
        facilities = []
        not_found = []
        
        for fid in facility_ids:
            facility = next((f for f in self.facilities if f["id"] == fid), None)
            if facility:
                facilities.append(facility)
            else:
                not_found.append(fid)
        
        if not facilities:
            return {
                "error": "No facilities found",
                "not_found": not_found,
            }
        
        # Build comparison
        comparison = {
            "facilities_compared": len(facilities),
            "not_found": not_found,
            "comparison": {},
        }
        
        for factor in comparison_factors:
            if factor == "cost":
                comparison["comparison"]["monthly_cost"] = {
                    f["name"]: {
                        "private_pay": f.get("private_pay_rate"),
                        "medicaid": f.get("medicaid_rate"),
                    }
                    for f in facilities
                }
            elif factor == "rating":
                comparison["comparison"]["rating"] = {
                    f["name"]: {
                        "overall": f.get("rating"),
                        "inspection": f.get("inspection_rating"),
                    }
                    for f in facilities
                }
            elif factor == "medicaid":
                comparison["comparison"]["medicaid"] = {
                    f["name"]: {
                        "accepted": f.get("medicaid_accepted"),
                        "beds_available": f.get("medicaid_beds_available"),
                    }
                    for f in facilities
                }
            elif factor == "capacity":
                comparison["comparison"]["capacity"] = {
                    f["name"]: {
                        "total": f.get("capacity"),
                        "current_occupancy": f.get("current_occupancy"),
                        "availability": f.get("capacity", 0) - f.get("current_occupancy", 0),
                    }
                    for f in facilities
                }
            elif factor == "amenities":
                comparison["comparison"]["amenities"] = {
                    f["name"]: f.get("amenities", [])
                    for f in facilities
                }
            elif factor == "specialized_care":
                comparison["comparison"]["specialized_care"] = {
                    f["name"]: f.get("specialized_care", [])
                    for f in facilities
                }
        
        # Add recommendation
        if facilities:
            # Simple scoring: rating * 2 + (medicaid_beds > 0) * 1 - (cost / 1000)
            def score(f):
                s = f.get("rating", 0) * 2
                if f.get("medicaid_beds_available", 0) > 0:
                    s += 1
                s -= (f.get("private_pay_rate", 5000) / 1000)
                return s
            
            best = max(facilities, key=score)
            comparison["recommendation"] = {
                "facility": best["name"],
                "reason": f"Highest combined score based on rating ({best['rating']}) and value",
            }
        
        return comparison
    
    def check_admission_requirements(
        self,
        facility_id: str,
        patient_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Check if a patient meets a facility's admission requirements.
        
        Args:
            facility_id: Facility ID
            patient_profile: Patient's care profile
        
        Returns:
            Dict with admission eligibility and any issues
        """
        facility = next((f for f in self.facilities if f["id"] == facility_id), None)
        
        if not facility:
            return {
                "error": f"Facility not found: {facility_id}",
            }
        
        issues = []
        warnings = []
        
        # Check care level match
        care_level_needed = patient_profile.get("care_level_needed", "").upper()
        if care_level_needed and care_level_needed != facility["type"]:
            issues.append(
                f"Care level mismatch: Patient needs {care_level_needed}, "
                f"facility provides {facility['type']}"
            )
        
        # Check payment type
        payment_type = patient_profile.get("payment_type", "").lower()
        if payment_type == "medicaid":
            if not facility["medicaid_accepted"]:
                issues.append("Facility does not accept Medicaid")
            elif facility["medicaid_beds_available"] == 0:
                warnings.append("Facility accepts Medicaid but no beds currently available")
        
        # Check specialized care needs
        diagnoses = patient_profile.get("diagnoses", [])
        facility_care = set(facility.get("specialized_care", []))
        
        # Map common diagnoses to care types
        diagnosis_care_map = {
            "alzheimers": ["alzheimers", "dementia", "memory"],
            "dementia": ["dementia", "alzheimers", "memory"],
            "diabetes": ["diabetes"],
            "copd": ["respiratory"],
            "heart_failure": ["cardiac", "heart conditions"],
        }
        
        for diagnosis in diagnoses:
            diagnosis_lower = diagnosis.lower()
            required_care = diagnosis_care_map.get(diagnosis_lower, [])
            if required_care and not any(c in facility_care for c in required_care):
                warnings.append(
                    f"Facility may not specialize in {diagnosis} care. "
                    "Verify with facility directly."
                )
        
        # Check mobility requirements
        mobility = patient_profile.get("mobility", "").lower()
        if mobility == "wheelchair" and facility["type"] == "AL":
            warnings.append(
                "Wheelchair-bound patients may need higher level of care. "
                "Verify facility can accommodate."
            )
        
        # Check availability
        availability = facility["capacity"] - facility["current_occupancy"]
        if availability <= 0:
            issues.append("Facility is currently at full capacity")
        elif availability <= 3:
            warnings.append(f"Limited availability: only {availability} beds open")
        
        # Determine eligibility
        eligible = len(issues) == 0
        
        return {
            "facility_id": facility_id,
            "facility_name": facility["name"],
            "eligible": eligible,
            "issues": issues,
            "warnings": warnings,
            "facility_details": {
                "type": facility["type"],
                "medicaid_accepted": facility["medicaid_accepted"],
                "medicaid_beds_available": facility["medicaid_beds_available"],
                "specialized_care": facility["specialized_care"],
                "current_availability": availability,
            },
            "next_steps": [
                "Schedule a tour of the facility",
                "Request a detailed cost breakdown",
                "Ask about waitlist if applicable",
                "Verify insurance/Medicaid acceptance",
            ] if eligible else [
                "Address the issues listed above",
                "Consider alternative facilities",
                "Consult with a care advisor",
            ],
        }


# For running as MCP server
if __name__ == "__main__":
    import json
    import sys
    
    server = FacilitySearchServer()
    
    # Simple JSON-RPC style interface for MCP
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "search_facilities":
                result = server.search_facilities(**params)
            elif method == "compare_facilities":
                result = server.compare_facilities(**params)
            elif method == "check_admission_requirements":
                result = server.check_admission_requirements(**params)
            else:
                result = {"error": f"Unknown method: {method}"}
            
            print(json.dumps({"id": request.get("id"), "result": result}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
