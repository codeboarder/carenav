"""
CareNav Florida - 30 Scenario End-to-End Test Suite

This script tests all major functionality with Azure OpenAI endpoints:
- Medicaid eligibility scenarios
- VA benefits scenarios  
- Facility matching scenarios
- Spend-down strategies
- Deceased spouse debt scenarios
- Gift penalty scenarios
- Chat/conversation scenarios
- Document generation scenarios
"""

import asyncio
import httpx
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

BASE_URL = "http://localhost:8000"
DOCS_DIR = Path("/home/ubuntu/carenav-florida/test_documents")
RESULTS_FILE = Path("/home/ubuntu/carenav-florida/test_results.json")

DOCS_DIR.mkdir(parents=True, exist_ok=True)


class TestScenario:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.passed = False
        self.error = None
        self.results = {}
        self.documents = []


async def create_patient(client: httpx.AsyncClient, data: dict) -> dict:
    """Create a patient and return the response."""
    response = await client.post(f"{BASE_URL}/api/patients/", json=data)
    response.raise_for_status()
    return response.json()


async def check_eligibility(client: httpx.AsyncClient, data: dict) -> dict:
    """Check Medicaid/VA eligibility."""
    response = await client.post(f"{BASE_URL}/api/eligibility/check", json=data)
    response.raise_for_status()
    return response.json()


async def search_facilities(client: httpx.AsyncClient, data: dict) -> dict:
    """Search for facilities."""
    response = await client.post(f"{BASE_URL}/api/facilities/search", json=data)
    response.raise_for_status()
    return response.json()


async def send_chat(client: httpx.AsyncClient, message: str, patient_id: int = None) -> dict:
    """Send a chat message."""
    data = {"message": message, "patient_id": patient_id, "conversation_history": []}
    response = await client.post(f"{BASE_URL}/api/chat/", json=data)
    response.raise_for_status()
    return response.json()


async def create_task(client: httpx.AsyncClient, patient_id: int, data: dict) -> dict:
    """Create a task."""
    response = await client.post(f"{BASE_URL}/api/tasks/{patient_id}", json=data)
    response.raise_for_status()
    return response.json()


async def get_spend_down(client: httpx.AsyncClient, amount: float) -> dict:
    """Get spend-down options."""
    response = await client.get(f"{BASE_URL}/api/eligibility/spend-down/{amount}")
    response.raise_for_status()
    return response.json()


async def check_debt(client: httpx.AsyncClient, debt_type: str, debt_holder: str, joint: bool) -> dict:
    """Check deceased spouse debt guidance."""
    response = await client.post(
        f"{BASE_URL}/api/eligibility/debt-check",
        params={"debt_type": debt_type, "debt_holder": debt_holder, "joint_account": joint}
    )
    response.raise_for_status()
    return response.json()


def save_document(scenario_name: str, doc_type: str, content: dict) -> str:
    """Save a document to the test_documents directory."""
    filename = f"{scenario_name.replace(' ', '_')}_{doc_type}.json"
    filepath = DOCS_DIR / filename
    with open(filepath, "w") as f:
        json.dump(content, f, indent=2, default=str)
    return str(filepath)


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================

async def scenario_01_medicaid_eligible(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 1: Patient clearly eligible for Medicaid (under $2,000 assets)."""
    scenario = TestScenario(
        "01_Medicaid_Eligible",
        "Patient with $1,500 in assets - should be Medicaid eligible"
    )
    try:
        patient = await create_patient(client, {
            "first_name": "Mary",
            "last_name": "Johnson",
            "date_of_birth": "1940-03-15",
            "state": "FL",
            "zip_code": "33401",
            "county": "Palm Beach",
            "current_location": "home",
            "care_level_needed": "AL",
            "care_needs": {"bathing": True, "dressing": True, "medication_management": True},
            "veteran_status": {"is_veteran": False},
            "financials": {
                "social_security": 1800,
                "checking": 800,
                "savings": 700,
                "owns_home": True,
                "home_value": 250000,
                "intends_to_return": True
            }
        })
        scenario.results["patient"] = patient
        
        eligibility = await check_eligibility(client, {
            "financials": {
                "social_security": 1800,
                "checking": 800,
                "savings": 700,
                "owns_home": True,
                "home_value": 250000
            },
            "veteran_status": {"is_veteran": False}
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["medicaid"]["eligible"] is True, "Should be Medicaid eligible"
        
        doc_path = save_document(scenario.name, "eligibility_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_02_medicaid_over_limit(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 2: Patient over Medicaid asset limit."""
    scenario = TestScenario(
        "02_Medicaid_Over_Limit",
        "Patient with $50,000 in assets - needs spend-down"
    )
    try:
        patient = await create_patient(client, {
            "first_name": "Robert",
            "last_name": "Smith",
            "date_of_birth": "1938-07-22",
            "state": "FL",
            "zip_code": "33139",
            "county": "Miami-Dade",
            "current_location": "hospital",
            "care_level_needed": "SNF",
            "care_needs": {"skilled_nursing": True, "wound_care": True},
            "veteran_status": {"is_veteran": False},
            "financials": {
                "social_security": 2200,
                "pension": 800,
                "checking": 15000,
                "savings": 25000,
                "cds": 10000
            }
        })
        scenario.results["patient"] = patient
        
        eligibility = await check_eligibility(client, {
            "financials": {
                "social_security": 2200,
                "pension": 800,
                "checking": 15000,
                "savings": 25000,
                "cds": 10000
            },
            "veteran_status": {"is_veteran": False}
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["medicaid"]["eligible"] is False
        
        spend_down = await get_spend_down(client, eligibility["medicaid"]["over_by"])
        scenario.results["spend_down"] = spend_down
        
        doc_path = save_document(scenario.name, "spend_down_plan", {
            "eligibility": eligibility,
            "spend_down_options": spend_down
        })
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_03_va_veteran_eligible(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 3: Wartime veteran eligible for VA Aid & Attendance."""
    scenario = TestScenario(
        "03_VA_Veteran_Eligible",
        "Vietnam veteran eligible for VA A&A benefits"
    )
    try:
        patient = await create_patient(client, {
            "first_name": "James",
            "last_name": "Williams",
            "date_of_birth": "1945-11-08",
            "state": "FL",
            "zip_code": "32801",
            "county": "Orange",
            "current_location": "home",
            "care_level_needed": "AL",
            "care_needs": {"bathing": True, "dressing": True, "transferring": True},
            "veteran_status": {
                "is_veteran": True,
                "wartime_service": True,
                "dd214_available": True
            },
            "financials": {
                "social_security": 1600,
                "checking": 5000,
                "savings": 3000
            }
        })
        scenario.results["patient"] = patient
        
        eligibility = await check_eligibility(client, {
            "financials": {
                "social_security": 1600,
                "checking": 5000,
                "savings": 3000
            },
            "veteran_status": {
                "is_veteran": True,
                "wartime_service": True
            }
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["va_aa"]["eligible"] is True
        assert eligibility["va_aa"]["monthly_benefit"] == 2229
        
        doc_path = save_document(scenario.name, "va_benefits_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_04_va_surviving_spouse(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 4: Surviving spouse of wartime veteran."""
    scenario = TestScenario(
        "04_VA_Surviving_Spouse",
        "Widow of WWII veteran eligible for survivor benefits"
    )
    try:
        patient = await create_patient(client, {
            "first_name": "Eleanor",
            "last_name": "Davis",
            "date_of_birth": "1928-04-12",
            "state": "FL",
            "zip_code": "33701",
            "county": "Pinellas",
            "current_location": "home",
            "care_level_needed": "MC",
            "care_needs": {"dementia_diagnosis": True, "wandering_risk": True, "medication_management": True},
            "veteran_status": {
                "is_veteran": False,
                "is_spouse_of_veteran": True,
                "veteran_deceased": True,
                "wartime_service": True
            },
            "financials": {
                "social_security": 1400,
                "checking": 1200,
                "savings": 500
            }
        })
        scenario.results["patient"] = patient
        
        eligibility = await check_eligibility(client, {
            "financials": {
                "social_security": 1400,
                "checking": 1200,
                "savings": 500
            },
            "veteran_status": {
                "is_veteran": False,
                "is_spouse_of_veteran": True,
                "veteran_deceased": True,
                "wartime_service": True
            }
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["va_aa"]["eligible"] is True
        assert eligibility["va_aa"]["monthly_benefit"] == 1432
        
        doc_path = save_document(scenario.name, "va_survivor_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_05_gift_penalty(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 5: Patient with gift in look-back period."""
    scenario = TestScenario(
        "05_Gift_Penalty",
        "Patient gave $50,000 gift 2 years ago - penalty period applies"
    )
    try:
        gift_date = (date.today() - timedelta(days=730)).isoformat()
        
        patient = await create_patient(client, {
            "first_name": "Patricia",
            "last_name": "Brown",
            "date_of_birth": "1942-09-30",
            "state": "FL",
            "zip_code": "33060",
            "county": "Broward",
            "current_location": "rehab",
            "care_level_needed": "SNF",
            "care_needs": {"skilled_nursing": True, "physical_therapy": True},
            "veteran_status": {"is_veteran": False},
            "financials": {
                "social_security": 1900,
                "checking": 1500,
                "savings": 300
            },
            "gifts": [{
                "amount": 50000,
                "recipient": "Daughter",
                "gift_date": gift_date
            }]
        })
        scenario.results["patient"] = patient
        
        eligibility = await check_eligibility(client, {
            "financials": {
                "social_security": 1900,
                "checking": 1500,
                "savings": 300
            },
            "veteran_status": {"is_veteran": False},
            "gifts": [{
                "amount": 50000,
                "gift_date": gift_date,
                "recipient": "Daughter"
            }]
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["gift_penalty"]["has_penalty"] is True
        assert eligibility["gift_penalty"]["months"] > 0
        
        doc_path = save_document(scenario.name, "gift_penalty_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_06_deceased_spouse_debt(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 6: Deceased spouse debt - surviving spouse NOT responsible."""
    scenario = TestScenario(
        "06_Deceased_Spouse_Debt",
        "Widow being pressured to pay deceased husband's medical debt"
    )
    try:
        debt_check = await check_debt(client, "medical", "deceased_spouse", False)
        scenario.results["debt_check"] = debt_check
        
        doc_path = save_document(scenario.name, "debt_guidance", debt_check)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_07_facility_search_al(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 7: Search for Assisted Living facilities in Palm Beach."""
    scenario = TestScenario(
        "07_Facility_Search_AL",
        "Search for AL facilities accepting Medicaid in Palm Beach County"
    )
    try:
        facilities = await search_facilities(client, {
            "zip_code": "33401",
            "care_level": "AL",
            "medicaid_required": True,
            "radius_miles": 25,
            "patient_income": 1800,
            "va_benefit": 0
        })
        scenario.results["facilities"] = facilities
        
        doc_path = save_document(scenario.name, "facility_search_results", facilities)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_08_facility_search_mc(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 8: Search for Memory Care facilities."""
    scenario = TestScenario(
        "08_Facility_Search_MC",
        "Search for Memory Care facilities in Orange County"
    )
    try:
        facilities = await search_facilities(client, {
            "zip_code": "32801",
            "care_level": "MC",
            "medicaid_required": False,
            "radius_miles": 30,
            "patient_income": 2500,
            "va_benefit": 1432
        })
        scenario.results["facilities"] = facilities
        
        doc_path = save_document(scenario.name, "mc_facility_results", facilities)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_09_facility_search_snf(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 9: Search for Skilled Nursing facilities."""
    scenario = TestScenario(
        "09_Facility_Search_SNF",
        "Search for SNF facilities in Miami-Dade County"
    )
    try:
        facilities = await search_facilities(client, {
            "zip_code": "33139",
            "care_level": "SNF",
            "medicaid_required": True,
            "radius_miles": 20,
            "patient_income": 3000,
            "va_benefit": 0
        })
        scenario.results["facilities"] = facilities
        
        doc_path = save_document(scenario.name, "snf_facility_results", facilities)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_10_chat_medicaid_question(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 10: Chat about Medicaid eligibility."""
    scenario = TestScenario(
        "10_Chat_Medicaid",
        "User asks about Medicaid asset limits"
    )
    try:
        response = await send_chat(
            client,
            "What is the Medicaid asset limit in Florida and what assets are exempt?"
        )
        scenario.results["chat_response"] = response
        
        assert len(response["message"]) > 50
        
        doc_path = save_document(scenario.name, "chat_response", response)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_11_chat_va_benefits(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 11: Chat about VA benefits."""
    scenario = TestScenario(
        "11_Chat_VA_Benefits",
        "User asks about VA Aid & Attendance"
    )
    try:
        response = await send_chat(
            client,
            "My father is a Vietnam veteran. What VA benefits might he qualify for to help pay for assisted living?"
        )
        scenario.results["chat_response"] = response
        
        assert len(response["message"]) > 50
        
        doc_path = save_document(scenario.name, "va_chat_response", response)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_12_chat_spend_down(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 12: Chat about spend-down strategies."""
    scenario = TestScenario(
        "12_Chat_Spend_Down",
        "User asks about legal ways to spend down assets"
    )
    try:
        response = await send_chat(
            client,
            "My mother has $75,000 in savings. What are legal ways to spend down to qualify for Medicaid?"
        )
        scenario.results["chat_response"] = response
        
        assert len(response["message"]) > 50
        
        doc_path = save_document(scenario.name, "spend_down_chat", response)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_13_chat_look_back(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 13: Chat about look-back period."""
    scenario = TestScenario(
        "13_Chat_Look_Back",
        "User asks about Medicaid look-back period"
    )
    try:
        response = await send_chat(
            client,
            "What is the Medicaid look-back period and what happens if my parent gave money to family members?"
        )
        scenario.results["chat_response"] = response
        
        assert len(response["message"]) > 50
        
        doc_path = save_document(scenario.name, "look_back_chat", response)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_14_task_creation(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 14: Create tasks for a patient."""
    scenario = TestScenario(
        "14_Task_Creation",
        "Create multiple tasks for care planning"
    )
    try:
        patient = await create_patient(client, {
            "first_name": "Test",
            "last_name": "Patient14",
            "date_of_birth": "1940-01-01",
            "state": "FL",
            "zip_code": "33401",
            "county": "Palm Beach",
            "current_location": "home",
            "care_level_needed": "AL",
            "care_needs": {},
            "veteran_status": {"is_veteran": False},
            "financials": {"social_security": 1500}
        })
        
        tasks = []
        task_data = [
            {"title": "Gather bank statements", "priority": "urgent", "category": "document"},
            {"title": "Schedule facility tours", "priority": "high", "category": "facility"},
            {"title": "Contact elder law attorney", "priority": "high", "category": "legal"},
            {"title": "Apply for Medicaid", "priority": "medium", "category": "benefit"}
        ]
        
        for td in task_data:
            task = await create_task(client, patient["id"], td)
            tasks.append(task)
        
        scenario.results["patient"] = patient
        scenario.results["tasks"] = tasks
        
        assert len(tasks) == 4
        
        doc_path = save_document(scenario.name, "task_list", {"patient": patient, "tasks": tasks})
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_15_edge_case_exactly_2000(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 15: Patient with exactly $2,000 in assets."""
    scenario = TestScenario(
        "15_Edge_Case_2000",
        "Patient with exactly $2,000 - at the Medicaid limit"
    )
    try:
        eligibility = await check_eligibility(client, {
            "financials": {
                "checking": 1000,
                "savings": 1000,
                "social_security": 1500
            },
            "veteran_status": {"is_veteran": False}
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["medicaid"]["eligible"] is True
        assert eligibility["medicaid"]["over_by"] == 0
        
        doc_path = save_document(scenario.name, "edge_case_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_16_edge_case_2001(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 16: Patient with $2,001 in assets."""
    scenario = TestScenario(
        "16_Edge_Case_2001",
        "Patient with $2,001 - just over Medicaid limit"
    )
    try:
        eligibility = await check_eligibility(client, {
            "financials": {
                "checking": 1001,
                "savings": 1000,
                "social_security": 1500
            },
            "veteran_status": {"is_veteran": False}
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["medicaid"]["eligible"] is False
        assert eligibility["medicaid"]["over_by"] == 1
        
        doc_path = save_document(scenario.name, "edge_case_2001_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_17_dual_eligible(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 17: Patient eligible for both Medicaid and VA."""
    scenario = TestScenario(
        "17_Dual_Eligible",
        "Veteran eligible for both Medicaid and VA A&A"
    )
    try:
        eligibility = await check_eligibility(client, {
            "financials": {
                "checking": 800,
                "savings": 700,
                "social_security": 1200
            },
            "veteran_status": {
                "is_veteran": True,
                "wartime_service": True
            }
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["medicaid"]["eligible"] is True
        assert eligibility["va_aa"]["eligible"] is True
        
        doc_path = save_document(scenario.name, "dual_eligible_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_18_high_income_medicaid(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 18: High income but low assets - ICP Medicaid."""
    scenario = TestScenario(
        "18_High_Income_ICP",
        "Patient with high income but low assets - ICP pathway"
    )
    try:
        eligibility = await check_eligibility(client, {
            "financials": {
                "checking": 1000,
                "savings": 800,
                "social_security": 2500,
                "pension": 2000
            },
            "veteran_status": {"is_veteran": False}
        })
        scenario.results["eligibility"] = eligibility
        
        doc_path = save_document(scenario.name, "high_income_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_19_multiple_gifts(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 19: Multiple gifts in look-back period."""
    scenario = TestScenario(
        "19_Multiple_Gifts",
        "Patient with multiple gifts totaling $100,000"
    )
    try:
        gifts = [
            {"amount": 30000, "gift_date": (date.today() - timedelta(days=365)).isoformat(), "recipient": "Son"},
            {"amount": 40000, "gift_date": (date.today() - timedelta(days=730)).isoformat(), "recipient": "Daughter"},
            {"amount": 30000, "gift_date": (date.today() - timedelta(days=1095)).isoformat(), "recipient": "Grandson"}
        ]
        
        eligibility = await check_eligibility(client, {
            "financials": {
                "checking": 1000,
                "savings": 500,
                "social_security": 1800
            },
            "veteran_status": {"is_veteran": False},
            "gifts": gifts
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["gift_penalty"]["has_penalty"] is True
        
        doc_path = save_document(scenario.name, "multiple_gifts_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_20_gift_outside_lookback(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 20: Gift outside 60-month look-back period."""
    scenario = TestScenario(
        "20_Gift_Outside_Lookback",
        "Gift made 6 years ago - no penalty"
    )
    try:
        old_gift_date = (date.today() - timedelta(days=2200)).isoformat()
        
        eligibility = await check_eligibility(client, {
            "financials": {
                "checking": 1000,
                "savings": 500,
                "social_security": 1800
            },
            "veteran_status": {"is_veteran": False},
            "gifts": [{"amount": 50000, "gift_date": old_gift_date, "recipient": "Child"}]
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["gift_penalty"]["has_penalty"] is False
        
        doc_path = save_document(scenario.name, "old_gift_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_21_chat_facility_question(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 21: Chat about facility selection."""
    scenario = TestScenario(
        "21_Chat_Facility",
        "User asks about choosing between AL and MC"
    )
    try:
        response = await send_chat(
            client,
            "My mother has early-stage dementia. Should we look at assisted living or memory care? What's the difference?"
        )
        scenario.results["chat_response"] = response
        
        assert len(response["message"]) > 50
        
        doc_path = save_document(scenario.name, "facility_chat", response)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_22_chat_urgent_placement(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 22: Chat about urgent hospital discharge."""
    scenario = TestScenario(
        "22_Chat_Urgent_Placement",
        "User needs urgent placement after hospital stay"
    )
    try:
        response = await send_chat(
            client,
            "My father is being discharged from the hospital in 3 days and can't go home. What are our options and what should we do first?"
        )
        scenario.results["chat_response"] = response
        
        assert len(response["message"]) > 50
        
        doc_path = save_document(scenario.name, "urgent_placement_chat", response)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_23_spend_down_small(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 23: Small spend-down amount."""
    scenario = TestScenario(
        "23_Spend_Down_Small",
        "Patient needs to spend down $5,000"
    )
    try:
        spend_down = await get_spend_down(client, 5000)
        scenario.results["spend_down"] = spend_down
        
        assert len(spend_down["options"]) > 0
        
        doc_path = save_document(scenario.name, "small_spend_down", spend_down)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_24_spend_down_large(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 24: Large spend-down amount."""
    scenario = TestScenario(
        "24_Spend_Down_Large",
        "Patient needs to spend down $200,000"
    )
    try:
        spend_down = await get_spend_down(client, 200000)
        scenario.results["spend_down"] = spend_down
        
        assert len(spend_down["options"]) > 0
        
        doc_path = save_document(scenario.name, "large_spend_down", spend_down)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_25_debt_joint_account(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 25: Deceased spouse debt - joint account."""
    scenario = TestScenario(
        "25_Debt_Joint_Account",
        "Debt was in joint names - survivor IS responsible"
    )
    try:
        debt_check = await check_debt(client, "credit_card", "deceased_spouse", True)
        scenario.results["debt_check"] = debt_check
        
        doc_path = save_document(scenario.name, "joint_debt_guidance", debt_check)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_26_va_no_wartime(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 26: Veteran without wartime service."""
    scenario = TestScenario(
        "26_VA_No_Wartime",
        "Veteran served during peacetime - not eligible for A&A"
    )
    try:
        eligibility = await check_eligibility(client, {
            "financials": {
                "checking": 3000,
                "savings": 2000,
                "social_security": 1800
            },
            "veteran_status": {
                "is_veteran": True,
                "wartime_service": False
            }
        })
        scenario.results["eligibility"] = eligibility
        
        assert eligibility["va_aa"]["eligible"] is False
        
        doc_path = save_document(scenario.name, "no_wartime_report", eligibility)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_27_chat_documents_needed(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 27: Chat about documents needed for Medicaid."""
    scenario = TestScenario(
        "27_Chat_Documents",
        "User asks what documents are needed for Medicaid application"
    )
    try:
        response = await send_chat(
            client,
            "What documents do I need to gather for my mother's Medicaid application in Florida?"
        )
        scenario.results["chat_response"] = response
        
        assert len(response["message"]) > 50
        
        doc_path = save_document(scenario.name, "documents_chat", response)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_28_chat_timeline(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 28: Chat about Medicaid application timeline."""
    scenario = TestScenario(
        "28_Chat_Timeline",
        "User asks how long Medicaid application takes"
    )
    try:
        response = await send_chat(
            client,
            "How long does the Medicaid application process take in Florida? What can delay it?"
        )
        scenario.results["chat_response"] = response
        
        assert len(response["message"]) > 50
        
        doc_path = save_document(scenario.name, "timeline_chat", response)
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_29_complex_case(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 29: Complex case with multiple factors."""
    scenario = TestScenario(
        "29_Complex_Case",
        "Veteran widow with gifts, high assets, and urgent placement need"
    )
    try:
        patient = await create_patient(client, {
            "first_name": "Margaret",
            "last_name": "Thompson",
            "date_of_birth": "1935-06-18",
            "state": "FL",
            "zip_code": "33480",
            "county": "Palm Beach",
            "current_location": "hospital",
            "care_level_needed": "MC",
            "discharge_date": (date.today() + timedelta(days=5)).isoformat(),
            "care_needs": {
                "dementia_diagnosis": True,
                "wandering_risk": True,
                "medication_management": True,
                "bathing": True,
                "dressing": True
            },
            "veteran_status": {
                "is_veteran": False,
                "is_spouse_of_veteran": True,
                "veteran_deceased": True,
                "wartime_service": True
            },
            "financials": {
                "social_security": 2100,
                "checking": 25000,
                "savings": 40000,
                "cds": 20000,
                "owns_home": True,
                "home_value": 350000,
                "intends_to_return": False
            },
            "gifts": [{
                "amount": 25000,
                "recipient": "Granddaughter",
                "gift_date": (date.today() - timedelta(days=400)).isoformat()
            }]
        })
        scenario.results["patient"] = patient
        
        eligibility = await check_eligibility(client, {
            "financials": {
                "social_security": 2100,
                "checking": 25000,
                "savings": 40000,
                "cds": 20000,
                "owns_home": True,
                "home_value": 350000
            },
            "veteran_status": {
                "is_veteran": False,
                "is_spouse_of_veteran": True,
                "veteran_deceased": True,
                "wartime_service": True
            },
            "gifts": [{
                "amount": 25000,
                "gift_date": (date.today() - timedelta(days=400)).isoformat(),
                "recipient": "Granddaughter"
            }]
        })
        scenario.results["eligibility"] = eligibility
        
        facilities = await search_facilities(client, {
            "zip_code": "33480",
            "care_level": "MC",
            "medicaid_required": True,
            "radius_miles": 30,
            "patient_income": 2100,
            "va_benefit": 1432
        })
        scenario.results["facilities"] = facilities
        
        spend_down = await get_spend_down(client, eligibility["medicaid"]["over_by"])
        scenario.results["spend_down"] = spend_down
        
        doc_path = save_document(scenario.name, "complex_case_full_report", {
            "patient": patient,
            "eligibility": eligibility,
            "facilities": facilities,
            "spend_down": spend_down
        })
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


async def scenario_30_full_workflow(client: httpx.AsyncClient) -> TestScenario:
    """Scenario 30: Complete end-to-end workflow."""
    scenario = TestScenario(
        "30_Full_Workflow",
        "Complete workflow: intake -> eligibility -> facilities -> tasks -> chat"
    )
    try:
        patient = await create_patient(client, {
            "first_name": "William",
            "last_name": "Anderson",
            "date_of_birth": "1941-12-07",
            "state": "FL",
            "zip_code": "33301",
            "county": "Broward",
            "current_location": "home",
            "care_level_needed": "AL",
            "care_needs": {
                "bathing": True,
                "dressing": True,
                "medication_management": True,
                "transferring": True
            },
            "veteran_status": {
                "is_veteran": True,
                "wartime_service": True,
                "dd214_available": True
            },
            "financials": {
                "social_security": 1950,
                "pension": 500,
                "checking": 8000,
                "savings": 12000,
                "owns_home": True,
                "home_value": 280000,
                "intends_to_return": True
            }
        })
        scenario.results["patient"] = patient
        
        eligibility = await check_eligibility(client, {
            "financials": {
                "social_security": 1950,
                "pension": 500,
                "checking": 8000,
                "savings": 12000,
                "owns_home": True,
                "home_value": 280000
            },
            "veteran_status": {
                "is_veteran": True,
                "wartime_service": True
            }
        })
        scenario.results["eligibility"] = eligibility
        
        spend_down = await get_spend_down(client, eligibility["medicaid"]["over_by"])
        scenario.results["spend_down"] = spend_down
        
        facilities = await search_facilities(client, {
            "zip_code": "33301",
            "care_level": "AL",
            "medicaid_required": True,
            "radius_miles": 25,
            "patient_income": 2450,
            "va_benefit": 2229
        })
        scenario.results["facilities"] = facilities
        
        tasks = []
        for task_data in [
            {"title": "Apply for VA Aid & Attendance", "priority": "urgent", "category": "benefit"},
            {"title": "Gather 5 years of bank statements", "priority": "high", "category": "document"},
            {"title": "Schedule tours at top 3 facilities", "priority": "high", "category": "facility"},
            {"title": "Consult elder law attorney about spend-down", "priority": "medium", "category": "legal"}
        ]:
            task = await create_task(client, patient["id"], task_data)
            tasks.append(task)
        scenario.results["tasks"] = tasks
        
        chat_response = await send_chat(
            client,
            f"I just completed intake for my father William. He's a Vietnam veteran with about $20,000 in assets. What should we focus on first?",
            patient["id"]
        )
        scenario.results["chat_response"] = chat_response
        
        doc_path = save_document(scenario.name, "full_workflow_report", {
            "patient": patient,
            "eligibility": eligibility,
            "spend_down": spend_down,
            "facilities": facilities,
            "tasks": tasks,
            "chat_response": chat_response
        })
        scenario.documents.append(doc_path)
        
        scenario.passed = True
    except Exception as e:
        scenario.error = str(e)
    return scenario


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_all_scenarios():
    """Run all 30 test scenarios."""
    print("=" * 70)
    print("CareNav Florida - 30 Scenario End-to-End Test Suite")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"Base URL: {BASE_URL}")
    print(f"Documents will be saved to: {DOCS_DIR}")
    print("=" * 70)
    
    scenarios = [
        scenario_01_medicaid_eligible,
        scenario_02_medicaid_over_limit,
        scenario_03_va_veteran_eligible,
        scenario_04_va_surviving_spouse,
        scenario_05_gift_penalty,
        scenario_06_deceased_spouse_debt,
        scenario_07_facility_search_al,
        scenario_08_facility_search_mc,
        scenario_09_facility_search_snf,
        scenario_10_chat_medicaid_question,
        scenario_11_chat_va_benefits,
        scenario_12_chat_spend_down,
        scenario_13_chat_look_back,
        scenario_14_task_creation,
        scenario_15_edge_case_exactly_2000,
        scenario_16_edge_case_2001,
        scenario_17_dual_eligible,
        scenario_18_high_income_medicaid,
        scenario_19_multiple_gifts,
        scenario_20_gift_outside_lookback,
        scenario_21_chat_facility_question,
        scenario_22_chat_urgent_placement,
        scenario_23_spend_down_small,
        scenario_24_spend_down_large,
        scenario_25_debt_joint_account,
        scenario_26_va_no_wartime,
        scenario_27_chat_documents_needed,
        scenario_28_chat_timeline,
        scenario_29_complex_case,
        scenario_30_full_workflow,
    ]
    
    results = []
    passed = 0
    failed = 0
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, scenario_func in enumerate(scenarios, 1):
            print(f"\n[{i:02d}/30] Running: {scenario_func.__name__}...")
            try:
                result = await scenario_func(client)
                results.append({
                    "name": result.name,
                    "description": result.description,
                    "passed": result.passed,
                    "error": result.error,
                    "documents": result.documents
                })
                
                if result.passed:
                    passed += 1
                    print(f"         PASSED - {result.description}")
                    if result.documents:
                        print(f"         Documents: {', '.join(result.documents)}")
                else:
                    failed += 1
                    print(f"         FAILED - {result.error}")
            except Exception as e:
                failed += 1
                print(f"         ERROR - {str(e)}")
                results.append({
                    "name": scenario_func.__name__,
                    "description": "Unknown",
                    "passed": False,
                    "error": str(e),
                    "documents": []
                })
    
    final_results = {
        "timestamp": datetime.now().isoformat(),
        "total": len(scenarios),
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{(passed/len(scenarios))*100:.1f}%",
        "scenarios": results
    }
    
    with open(RESULTS_FILE, "w") as f:
        json.dump(final_results, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Scenarios: {len(scenarios)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {(passed/len(scenarios))*100:.1f}%")
    print(f"\nResults saved to: {RESULTS_FILE}")
    print(f"Documents saved to: {DOCS_DIR}")
    print("=" * 70)
    
    return final_results


if __name__ == "__main__":
    asyncio.run(run_all_scenarios())
