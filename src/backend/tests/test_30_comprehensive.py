"""
30 Comprehensive End-to-End Tests for CareNav Florida
Tests all features with complex AI prompts
Built by Gregory Katz and Rick Weyenberg
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api(name, method, endpoint, data=None, expected_status=200):
    """Helper function to test API endpoints"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=60)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, timeout=30)
        
        success = response.status_code == expected_status
        result = "PASS" if success else "FAIL"
        print(f"[{result}] {name}")
        if not success:
            print(f"       Expected {expected_status}, got {response.status_code}")
            print(f"       Response: {response.text[:200]}")
        return success, response
    except Exception as e:
        print(f"[FAIL] {name}")
        print(f"       Error: {str(e)}")
        return False, None

def run_tests():
    passed = 0
    failed = 0
    
    print("\n" + "="*60)
    print("CareNav Florida - 30 Comprehensive End-to-End Tests")
    print("="*60 + "\n")
    
    # === HEALTH & INFRASTRUCTURE TESTS ===
    print("--- Health & Infrastructure Tests ---")
    
    # Test 1: Health check (correct endpoint is /healthz)
    success, _ = test_api("1. Health check endpoint", "GET", "/healthz")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 2: API docs available
    success, _ = test_api("2. API documentation available", "GET", "/docs", expected_status=200)
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # === PATIENT MANAGEMENT TESTS ===
    print("\n--- Patient Management Tests ---")
    
    # Test 3: List patients
    success, resp = test_api("3. List all patients", "GET", "/api/patients/")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 4: Get specific patient (Margaret Thompson)
    success, resp = test_api("4. Get Margaret Thompson patient", "GET", "/api/patients/")
    if success and resp:
        patients = resp.json()
        margaret = next((p for p in patients if "Margaret" in p.get("first_name", "")), None)
        if margaret:
            print(f"       Found Margaret Thompson (ID: {margaret.get('id')})")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # === DOCUMENT MANAGEMENT TESTS ===
    print("\n--- Document Management Tests ---")
    
    # Test 5: List documents for patient 1 (correct endpoint requires patient_id)
    success, resp = test_api("5. List documents for Margaret", "GET", "/api/documents/1/")
    passed += 1 if success else 0; failed += 0 if success else 1
    if success and resp:
        docs = resp.json()
        print(f"       Found {len(docs)} documents")
    
    # Test 6: Get patient context (includes documents)
    success, _ = test_api("6. Get patient context with documents", "GET", "/api/patients/1/context")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # === TASK MANAGEMENT TESTS ===
    print("\n--- Task Management Tests ---")
    
    # Test 7: List tasks for patient 1 (correct endpoint requires patient_id)
    success, resp = test_api("7. List tasks for Margaret", "GET", "/api/tasks/1")
    passed += 1 if success else 0; failed += 0 if success else 1
    if success and resp:
        tasks = resp.json()
        print(f"       Found {len(tasks)} tasks")
    
    # Test 8: Get tasks with dependencies
    success, _ = test_api("8. Get tasks with dependencies", "GET", "/api/tasks/1/with-dependencies")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # === ELIGIBILITY TESTS ===
    print("\n--- Eligibility Calculation Tests ---")
    
    # Test 9: Eligibility check (correct endpoint)
    success, resp = test_api("9. Eligibility check", "POST", "/api/eligibility/check", 
        data={"patient_id": 1, "total_assets": 3000, "monthly_income": 2425})
    passed += 1 if success else 0; failed += 0 if success else 1
    if success and resp:
        result = resp.json()
        print(f"       Result: {result}")
    
    # Test 10: Spend-down calculation
    success, resp = test_api("10. Spend-down calculation", "GET", "/api/eligibility/spend-down/1000")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # === FACILITY SEARCH TESTS ===
    print("\n--- Facility Search Tests ---")
    
    # Test 11: Search facilities (correct endpoint and params)
    success, resp = test_api("11. Search Memory Care facilities", "POST", "/api/facilities/search",
        data={"care_type": "memory_care", "zip_code": "33480", "accepts_medicaid": True})
    passed += 1 if success else 0; failed += 0 if success else 1
    if success and resp:
        facilities = resp.json()
        print(f"       Found {len(facilities) if isinstance(facilities, list) else 'N/A'} facilities")
    
    # Test 12: Get facility matches for patient
    success, _ = test_api("12. Get facility matches for Margaret", "GET", "/api/facilities/matches/1")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # === KNOWLEDGE BASE TESTS ===
    print("\n--- Knowledge Base (RAG) Tests ---")
    
    # Test 13: Query knowledge base - Medicaid
    success, resp = test_api("13. KB Query: Medicaid asset limits", "POST", "/api/knowledge/query/",
        data={"query": "What are the Florida Medicaid asset limits?", "n_results": 3})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 14: Query knowledge base - VA
    success, _ = test_api("14. KB Query: VA survivor benefits", "POST", "/api/knowledge/query/",
        data={"query": "What VA benefits can a surviving spouse receive?", "n_results": 3})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 15: Knowledge base categories
    success, _ = test_api("15. KB Categories list", "GET", "/api/knowledge/categories/")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 16: Knowledge base summary
    success, _ = test_api("16. KB Summary", "GET", "/api/knowledge/summary/")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # === COMPLEX AI CHAT TESTS ===
    print("\n--- Complex AI Chat Tests ---")
    
    # Test 17: Simple eligibility question
    success, resp = test_api("17. AI: Simple Medicaid question", "POST", "/api/chat/",
        data={"message": "Is Margaret eligible for Medicaid?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    if success and resp:
        ai_resp = resp.json()
        has_content = len(ai_resp.get("response", "")) > 50
        print(f"       Response length: {len(ai_resp.get('response', ''))} chars, Has content: {has_content}")
    
    # Test 18: Multi-step reasoning
    success, resp = test_api("18. AI: Multi-step reasoning (eligibility + spend-down)", "POST", "/api/chat/",
        data={"message": "Margaret has $3,000 in assets. Is she eligible for Medicaid and if not, what are her legal spend-down options?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 19: Cross-domain query (Medicaid + VA)
    success, resp = test_api("19. AI: Cross-domain (Medicaid + VA benefits)", "POST", "/api/chat/",
        data={"message": "Can Margaret receive both Medicaid and VA survivor benefits at the same time? How do they interact?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 20: Facility + eligibility combined
    success, resp = test_api("20. AI: Facility + eligibility combined", "POST", "/api/chat/",
        data={"message": "What Memory Care facilities in Palm Beach accept Medicaid and what does Margaret need to qualify for admission?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 21: Legal guidance - deceased spouse debt
    success, resp = test_api("21. AI: Legal - deceased spouse debt", "POST", "/api/chat/",
        data={"message": "Margaret's husband Robert passed away with credit card debt. Is Margaret responsible for paying his debts in Florida?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 22: Timeline and deadlines
    success, resp = test_api("22. AI: Timeline and Medicare Day 100", "POST", "/api/chat/",
        data={"message": "Margaret is on Medicare Day 85 in skilled nursing. What's the deadline and what needs to happen before Day 100?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 23: Document requirements
    success, resp = test_api("23. AI: Document requirements for VA", "POST", "/api/chat/",
        data={"message": "What documents does Margaret need to apply for VA Aid & Attendance as a surviving spouse?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 24: Look-back period analysis
    success, resp = test_api("24. AI: Medicaid look-back period", "POST", "/api/chat/",
        data={"message": "Margaret gave her daughter $10,000 as a gift 3 years ago. Will this affect her Medicaid eligibility under Florida's look-back rules?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 25: Care transition requirements
    success, resp = test_api("25. AI: SNF to ALF transition requirements", "POST", "/api/chat/",
        data={"message": "What clinical requirements must Margaret meet to transition from skilled nursing to assisted living?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 26: Income analysis
    success, resp = test_api("26. AI: Income phases and benefit stacking", "POST", "/api/chat/",
        data={"message": "Margaret currently receives $2,425/month. How will her income change when she gets SSA survivor benefits and VA A&A?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 27: Comprehensive action plan
    success, resp = test_api("27. AI: Comprehensive action plan", "POST", "/api/chat/",
        data={"message": "Give me a prioritized action plan for Margaret's care transition this week, including who to call and what documents to gather.", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 28: Edge case - home exemption
    success, resp = test_api("28. AI: Home exemption rules", "POST", "/api/chat/",
        data={"message": "Margaret owns a mobile home worth $285,000. Is this exempt from Medicaid asset calculations?", "patient_id": 1})
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # === DATA INTEGRITY TESTS ===
    print("\n--- Data Integrity Tests ---")
    
    # Test 29: Medical info exists (correct endpoint requires patient_id)
    success, _ = test_api("29. Medical info for Margaret", "GET", "/api/medical/1")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # Test 30: Insurance info exists (correct endpoint requires patient_id)
    success, _ = test_api("30. Insurance info for Margaret", "GET", "/api/insurance/1")
    passed += 1 if success else 0; failed += 0 if success else 1
    
    # === SUMMARY ===
    print("\n" + "="*60)
    total = passed + failed
    pass_rate = (passed / total * 100) if total > 0 else 0
    print(f"RESULTS: {passed}/{total} tests passed ({pass_rate:.1f}%)")
    print("="*60)
    
    return passed, failed

if __name__ == "__main__":
    run_tests()
