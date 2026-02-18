# Built by Gregory Katz and Rick Weyenberg
# Code is as-is, open source

"""Create a fully populated demo scenario for CareNav Florida.

Updated for 8 Enhancement Tickets:
- Ticket 1: Spouse Death Intake (Robert Thompson deceased, Vietnam veteran)
- Ticket 2: Task Dependencies (bank before SSA, title before sale)
- Ticket 3: Bill Tracking (facility, funeral, utilities)
- Ticket 4: Income Phases (current, Phase 2 after SSA, Phase 3 after VA)
- Ticket 5: Benefit Applications (SSA survivor, VA A&A, Medicaid ICP)
- Ticket 6: Contact Directory (facility, legal, government, insurance)
- Ticket 7: Document Location + Procurement (DD-214 in hand, title in transit)
- Ticket 8: Asset Sale Pipeline (vehicle title in transit, sale blocked)
"""
import asyncio
import httpx
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"

async def create_demo():
    """Create a complete demo scenario with realistic data."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("Creating demo patient: Margaret Thompson...")
        
        # Create a realistic demo patient - elderly widow of Vietnam veteran
        # Assets: $3,000 total (close to Medicaid $2,000 limit - needs to spend down $1,000)
        # Ticket 1: Robert Thompson (spouse) recently passed - triggers estate tasks
        patient_data = {
            "first_name": "Margaret",
            "last_name": "Thompson",
            "date_of_birth": "1942-03-15",
            "ssn_last_four": "4521",
            "address": "1234 Palm Beach Gardens Dr",
            "city": "West Palm Beach",
            "state": "FL",
            "zip_code": "33401",
            "county": "Palm Beach",
            "phone": "(561) 555-0123",
            "current_location": "hospital",
            "diagnosis": "Hip fracture, early-stage dementia, diabetes Type 2",
            "discharge_date": str(date.today() + timedelta(days=5)),
            "care_level_needed": "MC",
            # Ticket 1: Spouse Death fields
            "spouse_deceased": True,
            "deceased_spouse_name": "Robert Thompson",
            "spouse_date_of_death": str(date.today() - timedelta(days=45)),
            "death_cert_status": "in_hand",
            "marriage_date": "1964-06-15",
            "marriage_location": "Miami, FL",
            "deceased_was_veteran": True,
            "care_needs": {
                "bathing": True,
                "dressing": True,
                "toileting": True,
                "transferring": True,
                "eating": False,
                "continence": True,
                "medication_management": True,
                "dementia_diagnosis": True,
                "wandering_risk": True,
                "behavioral_issues": False,
                "skilled_nursing": False,
                "physical_therapy": True,
                "wound_care": False,
                "iv_therapy": False
            },
            "veteran_status": {
                "is_veteran": False,
                "is_spouse_of_veteran": True,
                "veteran_deceased": True,
                "branch": "Army",
                "service_start": "1965-06-01",
                "service_end": "1969-08-15",
                "wartime_service": True,
                "discharge_type": "Honorable",
                "dd214_available": True
            },
            "financials": {
                "social_security": 1850.00,
                "pension": 450.00,
                "va_pension": 0,
                "other_income": 125.00,
                "checking": 1500.00,
                "savings": 1500.00,
                "cds": 0,
                "money_market": 0,
                "ira": 0,
                "four01k": 0,
                "brokerage": 0,
                "annuities": 0,
                "stocks": 0,
                "bonds": 0,
                "owns_home": True,
                "home_value": 285000.00,
                "home_mortgage": 0,
                "intends_to_return": False,
                "vehicle_1_value": 8000.00,
                "vehicle_2_value": 0,
                "life_insurance_face": 10000.00,
                "life_insurance_cash": 0,
                "credit_card_debt": 500.00,
                "medical_debt": 0,
                "other_debt": 0
            },
            "gifts": []
        }
        
        response = await client.post(f"{BASE_URL}/api/patients/", json=patient_data)
        response.raise_for_status()
        patient = response.json()
        patient_id = patient["id"]
        print(f"  Created patient ID: {patient_id}")
        
        # Check eligibility
        print("Checking eligibility...")
        elig_data = {
            "patient_id": patient_id,
            "financials": patient_data["financials"],
            "veteran_status": patient_data["veteran_status"],
            "gifts": patient_data["gifts"]
        }
        response = await client.post(f"{BASE_URL}/api/eligibility/check", json=elig_data)
        response.raise_for_status()
        eligibility = response.json()
        print(f"  Medicaid eligible: {eligibility['medicaid']['eligible']}")
        print(f"  VA A&A eligible: {eligibility['va_aa']['eligible']}")
        print(f"  Gift penalty: {eligibility['gift_penalty']['has_penalty']}")
        
        # Search for facilities
        print("Searching for Memory Care facilities...")
        facility_data = {
            "zip_code": "33401",
            "care_level": "MC",
            "radius_miles": 25,
            "medicaid_required": True,
            "patient_income": 2425.00,
            "va_benefit": 1432.00
        }
        response = await client.post(f"{BASE_URL}/api/facilities/search", json=facility_data)
        response.raise_for_status()
        facilities = response.json()
        print(f"  Found {facilities['total_found']} facilities")
        
        # Create tasks - Margaret only needs to spend down $1,000 to qualify for Medicaid
        print("Creating care planning tasks...")
        tasks = [
            {
                "title": "Gather DD-214 for VA benefits application",
                "description": "Contact National Personnel Records Center or use eBenefits to obtain copy of late husband's DD-214",
                "category": "veteran",
                "priority": "urgent",
                "due_date": str(date.today() + timedelta(days=3)),
                "phone": "1-314-801-0800"
            },
            {
                "title": "Apply for VA Survivors Pension with Aid & Attendance",
                "description": "Complete VA Form 21-534EZ. Margaret qualifies as surviving spouse of Vietnam veteran. Potential benefit: $1,432/month",
                "category": "benefit",
                "priority": "urgent",
                "due_date": str(date.today() + timedelta(days=7)),
                "phone": "1-800-827-1000"
            },
            {
                "title": "Spend down $1,000 to reach Medicaid asset limit",
                "description": "Margaret has $3,000 in countable assets. Medicaid limit is $2,000. Options: prepay funeral ($1,000), pay off credit card ($500), buy exempt items.",
                "category": "financial",
                "priority": "urgent",
                "due_date": str(date.today() + timedelta(days=5)),
                "phone": None
            },
            {
                "title": "Submit Medicaid application to DCF",
                "description": "Once assets are below $2,000, submit application. Processing takes 45-90 days. Apply at ACCESS Florida or local DCF office.",
                "category": "benefit",
                "priority": "high",
                "due_date": str(date.today() + timedelta(days=7)),
                "phone": "1-866-762-2237"
            },
            {
                "title": "Tour Palm Beach Memory Care Center",
                "description": "Top-rated facility accepting Medicaid. Schedule tour before discharge. Ask about availability and waitlist.",
                "category": "facility",
                "priority": "high",
                "due_date": str(date.today() + timedelta(days=4)),
                "phone": "(561) 555-7890"
            },
            {
                "title": "Tour Sunrise Senior Living - Wellington",
                "description": "Second choice facility. Higher private pay rate but excellent dementia program.",
                "category": "facility",
                "priority": "medium",
                "due_date": str(date.today() + timedelta(days=6)),
                "phone": "(561) 555-4567"
            },
            {
                "title": "Gather 5 years of bank statements",
                "description": "Required for Medicaid application look-back period review. Need statements from all accounts.",
                "category": "document",
                "priority": "high",
                "due_date": str(date.today() + timedelta(days=10)),
                "phone": None
            },
            {
                "title": "Prepay funeral expenses (spend-down strategy)",
                "description": "Irrevocable funeral trust is exempt from Medicaid. Use $1,000+ to prepay funeral costs. This reduces countable assets.",
                "category": "financial",
                "priority": "high",
                "due_date": str(date.today() + timedelta(days=5)),
                "phone": "(561) 555-3456"
            },
            {
                "title": "Contact hospital discharge planner",
                "description": "Coordinate discharge date with facility placement. Request PT/OT evaluation for care level documentation.",
                "category": "general",
                "priority": "urgent",
                "due_date": str(date.today() + timedelta(days=2)),
                "phone": "(561) 555-1000"
            },
            {
                "title": "Verify home exemption for Medicaid",
                "description": "Primary residence is exempt if Margaret intends to return OR if spouse/dependent lives there. Home value: $285,000.",
                "category": "legal",
                "priority": "medium",
                "due_date": str(date.today() + timedelta(days=10)),
                "phone": None
            }
        ]
        
        for task in tasks:
            response = await client.post(f"{BASE_URL}/api/tasks/{patient_id}", json=task)
            response.raise_for_status()
            print(f"  Created task: {task['title'][:50]}...")
        
        # Ticket 3: Create bills
        print("Creating bills (Ticket 3)...")
        bills = [
            {
                "vendor": "Palm Beach Memory Care Center",
                "amount": 6500.00,
                "due_date": str(date.today() + timedelta(days=30)),
                "category": "facility",
                "contact_name": "Billing Department",
                "contact_phone": "(561) 555-7890",
                "recurring": True,
                "notes": "First month deposit + first month rent. Medicaid pending."
            },
            {
                "vendor": "Eternal Rest Funeral Home",
                "amount": 2500.00,
                "due_date": str(date.today() + timedelta(days=14)),
                "category": "funeral",
                "contact_name": "James Wilson",
                "contact_phone": "(561) 555-3456",
                "recurring": False,
                "notes": "Balance due for Robert's funeral services. Prepaid $5,000."
            },
            {
                "vendor": "FPL Electric",
                "amount": 145.00,
                "due_date": str(date.today() + timedelta(days=7)),
                "category": "utility",
                "contact_name": "Customer Service",
                "contact_phone": "1-800-375-2434",
                "recurring": True,
                "notes": "Home utility - keep active until home sale decision."
            },
            {
                "vendor": "Shady Pines Mobile Home Park",
                "amount": 450.00,
                "due_date": str(date.today() + timedelta(days=5)),
                "category": "lot_rent",
                "contact_name": "Park Office",
                "contact_phone": "(561) 555-2222",
                "recurring": True,
                "notes": "Monthly lot rent. Due 1st of month."
            },
            {
                "vendor": "Walgreens Pharmacy",
                "amount": 85.00,
                "due_date": str(date.today() + timedelta(days=3)),
                "category": "medical",
                "contact_name": "Pharmacy",
                "contact_phone": "(561) 555-9999",
                "recurring": True,
                "notes": "Monthly prescriptions - diabetes and dementia meds."
            },
        ]
        
        for bill in bills:
            response = await client.post(f"{BASE_URL}/api/bills/{patient_id}", json=bill)
            if response.status_code == 200:
                print(f"  Created bill: {bill['vendor']}")
        
        # Ticket 4: Create income phases
        print("Creating income phases (Ticket 4)...")
        income_phases = [
            {
                "phase_name": "Phase 1: Current Income",
                "monthly_amount": 2425.00,
                "source": "Social Security + Pension",
                "status": "current",
                "estimated_start": "Now",
                "notes": "Margaret's SS ($1,850) + Robert's pension survivor benefit ($450) + other ($125)"
            },
            {
                "phase_name": "Phase 2: After SSA Survivor Benefits",
                "monthly_amount": 3125.00,
                "source": "Social Security + Survivor Benefits",
                "status": "submitted",
                "estimated_start": "March 2026",
                "notes": "SSA survivor benefits application submitted. Adds ~$700/month."
            },
            {
                "phase_name": "Phase 3: After VA A&A Approval",
                "monthly_amount": 4557.00,
                "source": "SS + Survivor + VA A&A",
                "status": "preparing",
                "estimated_start": "June 2026",
                "notes": "VA Aid & Attendance ($1,432/month) - preparing application. Need DD-214."
            },
        ]
        
        for phase in income_phases:
            response = await client.post(f"{BASE_URL}/api/income-phases/{patient_id}", json=phase)
            if response.status_code == 200:
                print(f"  Created income phase: {phase['phase_name']}")
        
        # Ticket 5: Create benefit applications
        print("Creating benefit applications (Ticket 5)...")
        benefit_apps = [
            {
                "benefit_type": "ssa_survivor",
                "display_name": "Social Security Survivor Benefits",
                "status": "submitted",
                "monthly_amount": 700.00,
                "submitted_date": str(date.today() - timedelta(days=30)),
                "expected_weeks": 8,
                "missing_documents": None,
                "contact_phone": "1-800-772-1213",
                "notes": "Application submitted. Awaiting determination."
            },
            {
                "benefit_type": "va_aa",
                "display_name": "VA Aid & Attendance (Survivor)",
                "status": "preparing",
                "monthly_amount": 1432.00,
                "submitted_date": None,
                "expected_weeks": 16,
                "missing_documents": "DD-214 (ordered), Marriage Certificate",
                "contact_phone": "1-800-827-1000",
                "notes": "Gathering documents. DD-214 ordered from NPRC."
            },
            {
                "benefit_type": "medicaid_icp",
                "display_name": "Florida Medicaid ICP",
                "status": "researching",
                "monthly_amount": 0,
                "submitted_date": None,
                "expected_weeks": 12,
                "missing_documents": "5-year bank statements, Asset verification",
                "contact_phone": "1-866-762-2237",
                "notes": "Need to spend down $1,000 before applying. Gathering look-back docs."
            },
        ]
        
        for app in benefit_apps:
            response = await client.post(f"{BASE_URL}/api/benefit-applications/{patient_id}", json=app)
            if response.status_code == 200:
                print(f"  Created benefit application: {app['display_name']}")
        
        # Ticket 6: Create contacts
        print("Creating contacts (Ticket 6)...")
        contacts = [
            {
                "name": "Sarah Johnson",
                "organization": "Palm Beach Memory Care Center",
                "role": "Admissions Director",
                "phone": "(561) 555-7890",
                "email": "sjohnson@pbmcc.com",
                "category": "facility",
                "notes": "Primary contact for placement. Toured facility 2/10."
            },
            {
                "name": "Michael Chen, Esq.",
                "organization": "Chen Elder Law",
                "role": "Elder Law Attorney",
                "phone": "(561) 555-4000",
                "email": "mchen@chenelderlaw.com",
                "category": "legal",
                "notes": "Handling Medicaid planning and estate matters."
            },
            {
                "name": "Lisa Martinez",
                "organization": "FL DCF - Palm Beach",
                "role": "Medicaid Caseworker",
                "phone": "(561) 555-6000",
                "email": None,
                "category": "government",
                "notes": "Assigned caseworker for Medicaid application."
            },
            {
                "name": "VA Regional Office",
                "organization": "US Dept of Veterans Affairs",
                "role": "Benefits Hotline",
                "phone": "1-800-827-1000",
                "email": None,
                "category": "government",
                "notes": "For VA survivor benefits and A&A application."
            },
            {
                "name": "James Wilson",
                "organization": "Eternal Rest Funeral Home",
                "role": "Funeral Director",
                "phone": "(561) 555-3456",
                "email": "jwilson@eternalrest.com",
                "category": "facility",
                "notes": "Handled Robert's services. Balance due $2,500."
            },
            {
                "name": "State Farm Insurance",
                "organization": "State Farm",
                "role": "Auto Insurance",
                "phone": "1-800-782-8332",
                "email": None,
                "category": "insurance",
                "notes": "Vehicle insurance - cancel AFTER vehicle sale."
            },
            {
                "name": "Jennifer Thompson",
                "organization": None,
                "role": "Daughter (Primary Caregiver)",
                "phone": "(561) 555-1234",
                "email": "jthompson@email.com",
                "category": "family",
                "notes": "POA for healthcare and finances. Primary decision maker."
            },
            {
                "name": "Dr. Robert Kim",
                "organization": "Palm Beach Medical Group",
                "role": "Primary Care Physician",
                "phone": "(561) 555-8000",
                "email": None,
                "category": "medical",
                "notes": "Margaret's PCP. Can provide medical necessity letters."
            },
        ]
        
        for contact in contacts:
            response = await client.post(f"{BASE_URL}/api/contacts/{patient_id}", json=contact)
            if response.status_code == 200:
                print(f"  Created contact: {contact['name']}")
        
        # Ticket 8: Create assets
        print("Creating assets (Ticket 8)...")
        assets = [
            {
                "name": "2018 Toyota Camry",
                "asset_type": "vehicle",
                "owner": "deceased",
                "estimated_value": 8000.00,
                "title_status": "in_transit",
                "sale_status": "preparing",
                "sale_channel": "private",
                "linked_insurance": "State Farm Auto Policy #12345",
                "notes": "Title transfer requested from FL DMV. Expected 2-3 weeks. Cannot sell until title received."
            },
            {
                "name": "Mobile Home - 1234 Palm Beach Gardens Dr",
                "asset_type": "property",
                "owner": "joint",
                "estimated_value": 285000.00,
                "title_status": "in_hand",
                "sale_status": "not_for_sale",
                "sale_channel": None,
                "linked_insurance": "Citizens Homeowners Policy",
                "notes": "Primary residence - exempt from Medicaid. Decision pending on sale vs rent."
            },
            {
                "name": "Bank of America Checking",
                "asset_type": "account",
                "owner": "patient",
                "estimated_value": 1500.00,
                "title_status": "not_needed",
                "sale_status": "not_for_sale",
                "sale_channel": None,
                "linked_insurance": None,
                "notes": "Countable asset for Medicaid. Need to spend down."
            },
            {
                "name": "Bank of America Savings",
                "asset_type": "account",
                "owner": "patient",
                "estimated_value": 1500.00,
                "title_status": "not_needed",
                "sale_status": "not_for_sale",
                "sale_channel": None,
                "linked_insurance": None,
                "notes": "Countable asset for Medicaid. Need to spend down."
            },
            {
                "name": "Wedding Ring Set",
                "asset_type": "jewelry",
                "owner": "patient",
                "estimated_value": 2500.00,
                "title_status": "not_needed",
                "sale_status": "not_for_sale",
                "sale_channel": None,
                "linked_insurance": None,
                "notes": "Personal jewelry - exempt from Medicaid asset count."
            },
        ]
        
        for asset in assets:
            response = await client.post(f"{BASE_URL}/api/assets/{patient_id}", json=asset)
            if response.status_code == 200:
                print(f"  Created asset: {asset['name']}")
        
        # NEW: Create medical info
        print("Creating medical info...")
        medical_info = {
            "medicare_id": "1EG4-TE5-MK72",
            "medicaid_id": None,  # Pending
            "physician_name": "Dr. Robert Kim",
            "physician_phone": "(561) 555-8000",
            "blood_pressure": "138/82",
            "pulse": 72,
            "temperature": 98.4,
            "respiration": 16,
            "vitals_date": str(date.today() - timedelta(days=2)),
            "allergies": "Penicillin, Sulfa drugs, Shellfish",
            "diet": "Diabetic / Low Sodium / Mechanical Soft",
            "code_status": "FULL CODE"
        }
        response = await client.post(f"{BASE_URL}/api/medical/{patient_id}/info", json=medical_info)
        if response.status_code == 200:
            print(f"  Created medical info")
        
        # Create diagnoses
        print("Creating diagnoses...")
        diagnoses = [
            {"name": "Alzheimer's Disease, Early Onset", "icd_code": "G30.0", "is_primary": True},
            {"name": "Type 2 Diabetes Mellitus", "icd_code": "E11.9", "is_primary": False},
            {"name": "Essential Hypertension", "icd_code": "I10", "is_primary": False},
            {"name": "Hip Fracture, Right", "icd_code": "S72.001A", "is_primary": False},
            {"name": "Chronic Kidney Disease, Stage 3", "icd_code": "N18.3", "is_primary": False},
            {"name": "Major Depressive Disorder", "icd_code": "F33.1", "is_primary": False},
            {"name": "Anxiety Disorder", "icd_code": "F41.9", "is_primary": False},
            {"name": "Osteoporosis", "icd_code": "M81.0", "is_primary": False},
            {"name": "Hypothyroidism", "icd_code": "E03.9", "is_primary": False},
            {"name": "GERD", "icd_code": "K21.0", "is_primary": False},
        ]
        for dx in diagnoses:
            response = await client.post(f"{BASE_URL}/api/medical/{patient_id}/diagnoses", json=dx)
            if response.status_code == 200:
                print(f"  Created diagnosis: {dx['name']}")
        
        # Create medications
        print("Creating medications...")
        medications = [
            {"name": "Metformin", "dosage": "500mg", "frequency": "2x/day", "route": "oral", "purpose": "Diabetes"},
            {"name": "Lisinopril", "dosage": "10mg", "frequency": "1x/day", "route": "oral", "purpose": "Blood Pressure"},
            {"name": "Donepezil (Aricept)", "dosage": "10mg", "frequency": "1x/day", "route": "oral", "purpose": "Dementia"},
            {"name": "Memantine", "dosage": "10mg", "frequency": "2x/day", "route": "oral", "purpose": "Dementia"},
            {"name": "Sertraline", "dosage": "50mg", "frequency": "1x/day", "route": "oral", "purpose": "Depression"},
            {"name": "Omeprazole", "dosage": "20mg", "frequency": "1x/day", "route": "oral", "purpose": "GERD"},
            {"name": "Levothyroxine", "dosage": "50mcg", "frequency": "1x/day", "route": "oral", "purpose": "Thyroid"},
            {"name": "Calcium + Vitamin D", "dosage": "600mg/400IU", "frequency": "2x/day", "route": "oral", "purpose": "Osteoporosis"},
            {"name": "Lorazepam", "dosage": "0.5mg", "frequency": "PRN", "route": "oral", "purpose": "Anxiety"},
        ]
        for med in medications:
            response = await client.post(f"{BASE_URL}/api/medical/{patient_id}/medications", json=med)
            if response.status_code == 200:
                print(f"  Created medication: {med['name']}")
        
        # NEW: Create insurance policies
        print("Creating insurance policies...")
        insurance_policies = [
            {
                "insurance_type": "medicare",
                "carrier": "Medicare Part A & B",
                "policy_number": "1EG4-TE5-MK72",
                "subscriber_name": "Margaret Thompson",
                "effective_date": "2007-03-01",
                "phone": "1-800-633-4227",
                "status": "active",
                "notes": "Original Medicare. No Part D - uses Humana for prescriptions."
            },
            {
                "insurance_type": "supplemental",
                "carrier": "Humana Gold Plus",
                "policy_number": "H5216-086",
                "group_number": "FL-2024",
                "subscriber_name": "Margaret Thompson",
                "effective_date": "2024-01-01",
                "phone": "1-800-457-4708",
                "status": "active",
                "notes": "Medicare Advantage plan. Includes Part D prescription coverage."
            },
            {
                "insurance_type": "medicaid",
                "carrier": "Florida Medicaid ICP",
                "policy_number": None,
                "subscriber_name": "Margaret Thompson",
                "effective_date": None,
                "phone": "1-866-762-2237",
                "status": "pending",
                "notes": "Application in progress. Need to spend down $1,000 first."
            },
        ]
        for policy in insurance_policies:
            response = await client.post(f"{BASE_URL}/api/insurance/{patient_id}", json=policy)
            if response.status_code == 200:
                print(f"  Created insurance: {policy['carrier']}")
        
        # NEW: Create selected facility
        print("Creating selected facility...")
        selected_facility = {
            "name": "Palm Beach Memory Care Center",
            "address": "2500 Palm Beach Lakes Blvd, West Palm Beach, FL 33409",
            "apt_number": "#214",
            "phone": "(561) 555-7890",
            "fax": "(561) 555-7891",
            "admissions_contact": "Sarah Johnson (Admissions)",
            "community_rep": "Maria Garcia (Community Rep)",
            "keys_date": str(date.today() + timedelta(days=8)) + "T10:00:00",
            "move_in_date": str(date.today() + timedelta(days=10)),
            "base_rent": 5200.00,
            "vet_discount_pct": 5.0,
            "care_level": "Memory Care Level II",
            "care_level_cost": 1800.00,
            "total_monthly": 6740.00,
            "deposit_amount": 2500.00,
            "deposit_paid": False,
            "community_fee": 3500.00,
            "status": "selected",
            "notes": "Top choice facility. Accepts Medicaid after 24 months private pay. Vet discount available."
        }
        response = await client.post(f"{BASE_URL}/api/selected-facility/{patient_id}", json=selected_facility)
        if response.status_code == 200:
            print(f"  Created selected facility: {selected_facility['name']}")
        
        # NEW: Create wins/accomplishments
        print("Creating wins...")
        wins = [
            {
                "title": "Death Certificate Obtained",
                "description": "Received 10 certified copies of Robert's death certificate from FL Vital Records",
                "amount": None,
                "amount_type": None,
                "win_date": str(date.today() - timedelta(days=40)),
                "category": "document"
            },
            {
                "title": "VA Burial Benefit Filed",
                "description": "Filed VA Form 21P-530EZ for burial allowance. $2,000 expected.",
                "amount": 2000.00,
                "amount_type": "one_time",
                "win_date": str(date.today() - timedelta(days=35)),
                "category": "financial"
            },
            {
                "title": "SSA Survivor Benefits Submitted",
                "description": "Application submitted for Social Security survivor benefits. ~$700/month expected.",
                "amount": 700.00,
                "amount_type": "monthly",
                "win_date": str(date.today() - timedelta(days=30)),
                "category": "financial"
            },
            {
                "title": "Facility Secured",
                "description": "Palm Beach Memory Care Center confirmed availability. Unit #214 reserved.",
                "amount": None,
                "amount_type": None,
                "win_date": str(date.today() - timedelta(days=5)),
                "category": "facility"
            },
            {
                "title": "Bank Access Established",
                "description": "Added Jennifer as joint account holder on all accounts. Full access confirmed.",
                "amount": None,
                "amount_type": None,
                "win_date": str(date.today() - timedelta(days=20)),
                "category": "legal"
            },
        ]
        for win in wins:
            response = await client.post(f"{BASE_URL}/api/wins/{patient_id}", json=win)
            if response.status_code == 200:
                print(f"  Created win: {win['title']}")
        
        # Send a chat message to populate conversation
        print("Creating sample chat conversation...")
        chat_messages = [
            "My mother Margaret is being discharged from the hospital in 5 days after a hip fracture. She has early dementia and we need to find memory care. Her late husband was a Vietnam veteran. What should we do first?",
        ]
        
        for msg in chat_messages:
            response = await client.post(
                f"{BASE_URL}/api/chat/",
                json={"message": msg, "patient_id": patient_id, "conversation_history": []}
            )
            if response.status_code == 200:
                print(f"  Chat response received")
        
        print("\n" + "="*60)
        print("DEMO SCENARIO CREATED SUCCESSFULLY")
        print("="*60)
        print(f"\nPatient: Margaret Thompson (ID: {patient_id})")
        print(f"Age: 83 years old")
        print(f"Situation: Hospital discharge in 5 days, needs Memory Care")
        print(f"Veteran Status: Surviving spouse of Vietnam veteran (Robert Thompson)")
        print(f"Spouse Death: Robert passed {45} days ago - estate tasks auto-generated")
        print(f"\nFinancial Summary:")
        print(f"  Checking Account: $1,500")
        print(f"  Savings Account: $1,500")
        print(f"  Total Countable Assets: $3,000")
        print(f"  Medicaid Asset Limit: $2,000")
        print(f"  Over Limit By: $1,000 (ALMOST ELIGIBLE!)")
        print(f"  Monthly Income: $2,425 (Phase 1)")
        print(f"\nIncome Phases (Ticket 4):")
        print(f"  Phase 1 (Current): $2,425/month")
        print(f"  Phase 2 (After SSA): $3,125/month")
        print(f"  Phase 3 (After VA A&A): $4,557/month")
        print(f"\nBenefits Pipeline (Ticket 5):")
        print(f"  SSA Survivor: SUBMITTED")
        print(f"  VA A&A: PREPARING")
        print(f"  Medicaid ICP: RESEARCHING")
        print(f"\nBills Due (Ticket 3): {len(bills)} bills tracked")
        print(f"Contacts (Ticket 6): {len(contacts)} contacts")
        print(f"Assets (Ticket 8): {len(assets)} assets")
        print(f"  - Vehicle: Title IN TRANSIT (sale blocked)")
        print(f"\nTasks Created: {len(tasks)} + estate tasks (auto-generated)")
        print(f"Facilities Found: {facilities['total_found']}")
        print("="*60)
        
        return patient_id

if __name__ == "__main__":
    asyncio.run(create_demo())
