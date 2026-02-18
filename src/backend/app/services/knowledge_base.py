"""ChromaDB knowledge base service for CareNav Florida."""
# Built by Gregory Katz and Rick Weyenberg
# Code is as-is, open source

# ============================================================
# AZURE AI SEARCH SWAP — Rick: Replace this entire file with
# search_service.py after provisioning Azure AI Search
# (see RICK_ENGINEERING_WORKBOOK.md §1C)
#
# New file should:
# 1. Import azure-search-documents + azure-core
# 2. Create SearchClient with AZURE_SEARCH_ENDPOINT + AZURE_SEARCH_API_KEY
# 3. Use index name: "carenav-documents"
# 4. Implement hybrid_search() with VectorizedQuery + semantic ranking
# 5. Use text-embedding-3-large (3072 dimensions) for embeddings
#
# Key swap:
#   OLD: chromadb.PersistentClient → collection.query(query_texts=[...])
#   NEW: SearchClient → search(search_text=..., vector_queries=[...], query_type="semantic")
#
# Existing export endpoint (/api/knowledge/export/azure-search/)
# already formats documents for Azure AI Search bulk upload.
# Use it to seed the index after provisioning.
# ============================================================

import os
from typing import Optional

# Only import chromadb if not in production (to save memory on Fly.io)
DISABLE_CHROMADB = os.environ.get("DISABLE_CHROMADB", "false").lower() == "true"


class KnowledgeBaseService:
    """Service for managing the elder law knowledge base in ChromaDB."""
    
    def __init__(self):
        self.disabled = DISABLE_CHROMADB
        self.client = None
        self.elder_law_collection = None
        self.facility_collection = None
        
        if not self.disabled:
            try:
                import chromadb
                from chromadb.config import Settings as ChromaSettings
                from app.config import get_settings
                settings = get_settings()
                self.client = chromadb.PersistentClient(
                    path=settings.chroma_persist_directory,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
                self.elder_law_collection = self.client.get_or_create_collection(
                    name="florida_elder_law",
                    metadata={"description": "Florida Medicaid, VA, elder law guidance"}
                )
                self.facility_collection = self.client.get_or_create_collection(
                    name="facilities",
                    metadata={"description": "Florida facility information"}
                )
            except ImportError:
                self.disabled = True
    
    def add_document(
        self,
        collection_name: str,
        doc_id: str,
        content: str,
        metadata: Optional[dict] = None,
    ):
        """Add a document to a collection."""
        if self.disabled:
            return
        collection = self._get_collection(collection_name)
        collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata or {}],
        )
    
    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: Optional[dict] = None,
    ) -> list[dict]:
        """Query a collection for relevant documents."""
        if self.disabled:
            return []
        collection = self._get_collection(collection_name)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )
        documents = []
        for i, doc_id in enumerate(results["ids"][0]):
            documents.append({
                "id": doc_id,
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None,
            })
        return documents
    
    def _get_collection(self, name: str):
        """Get a collection by name."""
        if name == "florida_elder_law":
            return self.elder_law_collection
        elif name == "facilities":
            return self.facility_collection
        else:
            return self.client.get_or_create_collection(name=name)
    
    def load_knowledge_base(self):
        """Load the comprehensive elder law knowledge base documents."""
        documents = [
            {
                "id": "deceased_spouse_debt",
                "content": DECEASED_SPOUSE_DEBT_KNOWLEDGE,
                "metadata": {"category": "debt", "priority": "high", "topic": "estate"}
            },
            {
                "id": "spend_down_strategies",
                "content": SPEND_DOWN_KNOWLEDGE,
                "metadata": {"category": "medicaid", "priority": "high", "topic": "financial_planning"}
            },
            {
                "id": "va_aid_attendance",
                "content": VA_BENEFITS_KNOWLEDGE,
                "metadata": {"category": "va", "priority": "high", "topic": "benefits"}
            },
            {
                "id": "florida_medicaid_rules",
                "content": FLORIDA_MEDICAID_KNOWLEDGE,
                "metadata": {"category": "medicaid", "priority": "high", "topic": "eligibility"}
            },
            {
                "id": "medicare_medicaid_coordination",
                "content": MEDICARE_MEDICAID_COORDINATION,
                "metadata": {"category": "medicare", "priority": "high", "topic": "dual_eligible"}
            },
            {
                "id": "assisted_living_regulations",
                "content": ASSISTED_LIVING_REGULATIONS,
                "metadata": {"category": "facility", "priority": "high", "topic": "regulations"}
            },
            {
                "id": "estate_planning_elder_care",
                "content": ESTATE_PLANNING_ELDER_CARE,
                "metadata": {"category": "legal", "priority": "high", "topic": "estate_planning"}
            },
            {
                "id": "document_requirements",
                "content": DOCUMENT_REQUIREMENTS,
                "metadata": {"category": "documents", "priority": "high", "topic": "checklists"}
            },
            {
                "id": "care_transition_checklist",
                "content": CARE_TRANSITION_CHECKLIST,
                "metadata": {"category": "transition", "priority": "high", "topic": "checklists"}
            },
            {
                "id": "florida_alf_inspection_guide",
                "content": FLORIDA_ALF_INSPECTION_GUIDE,
                "metadata": {"category": "facility", "priority": "medium", "topic": "quality"}
            },
        ]
        for doc in documents:
            try:
                self.add_document(
                    "florida_elder_law",
                    doc["id"],
                    doc["content"],
                    doc["metadata"],
                )
            except Exception:
                pass  # Document may already exist
    
    def get_all_documents(self) -> list[dict]:
        """Get all documents in the knowledge base for export/migration."""
        if self.disabled:
            return []
        try:
            results = self.elder_law_collection.get()
            documents = []
            for i, doc_id in enumerate(results["ids"]):
                documents.append({
                    "id": doc_id,
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                })
            return documents
        except Exception:
            return []
    
    def export_for_azure_search(self) -> list[dict]:
        """Export knowledge base in Azure AI Search compatible format."""
        documents = self.get_all_documents()
        azure_docs = []
        for doc in documents:
            azure_docs.append({
                "@search.action": "upload",
                "id": doc["id"],
                "content": doc["content"],
                "category": doc["metadata"].get("category", "general"),
                "priority": doc["metadata"].get("priority", "medium"),
                "topic": doc["metadata"].get("topic", "general"),
            })
        return azure_docs


DECEASED_SPOUSE_DEBT_KNOWLEDGE = """
# DECEASED SPOUSE DEBT RULE - FLORIDA

## Florida Law
Florida is a "common law" property state, NOT a community property state.

## What This Means
When a spouse dies, the surviving spouse is generally NOT responsible for the deceased spouse's individual debts.

## Individual Debts (Surviving Spouse NOT Responsible):
- Credit cards in deceased's name only
- Personal loans in deceased's name only
- Medical bills in deceased's name only
- Car loans for deceased's vehicle only

## Joint Debts (Surviving Spouse IS Responsible):
- Joint credit cards (both names on account)
- Joint mortgage
- Joint auto loans
- Any debt co-signed

## Critical Guidance
1. NEVER pay a deceased spouse's individual debt
2. Creditors may call and pressure - do not pay
3. Debts may be paid from the deceased's estate, not survivor's assets
4. Consult elder law attorney if creditors are aggressive
5. Paying deceased's debt wastes assets needed for care

## Medicaid Implications
- Survivor's assets are what matter for Medicaid eligibility
- Paying deceased's debts reduces survivor's assets (bad for planning)
- Those assets should be used for legal spend-down instead

## What to Say to Creditors
"The account holder is deceased. Please send a written request to the estate. Do not call this number again."
"""

SPEND_DOWN_KNOWLEDGE = """
# LEGAL MEDICAID SPEND-DOWN STRATEGIES - FLORIDA

## Overview
To qualify for Florida Medicaid, countable assets must be <= $2,000.
These strategies legally reduce countable assets.

## TIER 1: SAFEST (No Attorney Needed)

### 1. Irrevocable Prepaid Funeral
- Citation: FL Stat. 497.458; 42 CFR 435.725
- Max Amount: Typically $10,000-15,000
- Requirements: Must be IRREVOCABLE, Florida-licensed funeral home
- Can include: casket, burial, service, flowers, obituary

### 2. Pay Applicant's Own Debts
- Citation: 42 CFR 435.725
- What Qualifies: Credit cards, medical bills, mortgage IN APPLICANT'S NAME
- Keep receipts for Medicaid application
- WARNING: Do NOT pay deceased spouse's individual debts

### 3. Home Repairs and Modifications
- Citation: 42 CFR 435.726 (home is exempt)
- Max Amount: Typically up to $25,000
- What Qualifies: Roof, HVAC, accessibility modifications, plumbing, electrical

### 4. Medical/Dental/Vision/Hearing
- Citation: 42 CFR 435.725
- Max Amount: Typically up to $15,000
- What Qualifies: Dentures, hearing aids, glasses, medical equipment

### 5. Vehicle Purchase/Upgrade
- Citation: 42 CFR 435.726
- Rule: One vehicle exempt at ANY value
- Strategy: Trade in old car for newer/reliable vehicle

### 6. Burial Plot and Headstone
- Citation: 42 CFR 435.725(c)
- Who: Applicant AND immediate family members
- Max Amount: Typically $3,000-5,000 per person

## PROHIBITED ACTIONS (WILL Create Penalties)
- Gifts to family members: 1 month penalty per $10,809
- Sell assets below market value
- Add children to deeds/accounts
- Pay family members' debts
- Large charitable donations
"""

VA_BENEFITS_KNOWLEDGE = """
# VA BENEFITS FOR ELDER CARE - 2026

## Aid & Attendance (A&A) Monthly Benefits

| Situation | Monthly Benefit |
|-----------|-----------------|
| Veteran (single) | $2,229 |
| Veteran with spouse | $2,642 |
| Surviving spouse | $1,432 |

## Who Qualifies

### Veteran Qualifies If:
- 90+ days active duty
- 1+ day during wartime period
- Honorable or general discharge
- Net worth under $150,538
- Needs help with daily activities

### Surviving Spouse Qualifies If:
- Was married to qualifying veteran
- Veteran served during wartime
- Did not remarry (or remarried after age 57)
- Net worth under $150,538
- Needs help with daily activities

## Wartime Periods
- WWII: Dec 7, 1941 - Dec 31, 1946
- Korean: Jun 27, 1950 - Jan 31, 1955
- Vietnam: Aug 5, 1964 - May 7, 1975
- Gulf War: Aug 2, 1990 - Present

## VA vs Medicaid Comparison
| Factor | VA A&A | Florida Medicaid |
|--------|--------|------------------|
| Asset Limit | $150,538 | $2,000 |
| Look-Back | 36 months | 60 months |
| Payment | Cash to veteran/spouse | Directly to facility |
| Estate Recovery | No | Yes |

## Key Phone Numbers
- VA Benefits Hotline: 1-800-827-1000
- eBenefits Help: 1-800-983-0937
"""

FLORIDA_MEDICAID_KNOWLEDGE = """
# FLORIDA MEDICAID RULES FOR LONG-TERM CARE - 2026

## Asset Limit
$2,000 for individual applicant (HARD limit)

## Income Limit
$2,829/month for ICP (Institutional Care Program)

## Countable Assets
- Bank accounts (checking, savings)
- CDs, money market
- Stocks, bonds, mutual funds
- IRA, 401k, retirement accounts
- Annuities (cash surrender value)
- Life insurance (face > $2,500) - cash value counts
- Second vehicle
- Real estate (not homestead)

## Exempt Assets
- Homestead (up to $713,000 equity)
- One vehicle (unlimited value)
- Household goods
- Personal effects
- Burial plots
- Irrevocable burial trust
- Life insurance (face <= $2,500)
- Term life insurance (no cash value)

## Look-Back Period
60 months (5 years) from application date

## Penalty Calculation
Gift Amount / $10,809 = Penalty Months (rounded up)

Example: $25,000 gift = 3 months penalty

## Key Phone Numbers
- ACCESS Florida: 1-866-762-2237
- SHINE (Medicare counseling): 1-800-963-5337
- Elder Helpline: 1-800-963-5337
"""

MEDICARE_MEDICAID_COORDINATION = """
# MEDICARE AND MEDICAID COORDINATION - DUAL ELIGIBILITY

## Overview
Many seniors qualify for both Medicare and Medicaid (dual eligible).
Understanding how these programs work together is critical for care planning.

## Medicare Coverage
### Part A (Hospital Insurance)
- Inpatient hospital stays
- Skilled nursing facility (up to 100 days after hospital stay)
- Home health care
- Hospice care
- Premium: Usually $0 if 40+ quarters of work

### Part B (Medical Insurance)
- Doctor visits
- Outpatient care
- Medical equipment
- Preventive services
- Premium: $174.70/month (2026 standard)

### Part D (Prescription Drugs)
- Prescription medications
- Premium: Varies by plan
- Coverage gap (donut hole) considerations

## Medicaid Coverage (Florida)
### What Medicaid Covers That Medicare Doesn't
- Long-term nursing home care (beyond 100 days)
- Personal care services
- Adult day care
- Home and community-based services
- Dental, vision, hearing (limited)

## Dual Eligible Benefits
### Medicare Savings Programs (MSP)
- QMB (Qualified Medicare Beneficiary): Pays Part A & B premiums, deductibles, coinsurance
- SLMB (Specified Low-Income Medicare Beneficiary): Pays Part B premium only
- QI (Qualifying Individual): Pays Part B premium only

### Income Limits for MSP (2026)
- QMB: $1,275/month individual
- SLMB: $1,529/month individual
- QI: $1,715/month individual

## Skilled Nursing Facility Coverage
### Medicare SNF Coverage (Days 1-100)
- Days 1-20: $0 copay (Medicare pays 100%)
- Days 21-100: $204/day copay (2026)
- Day 101+: Medicare stops, Medicaid takes over if eligible

### Transition Planning
1. Apply for Medicaid BEFORE Medicare SNF coverage ends
2. Medicaid application takes 45-90 days
3. Start application by Day 30 of SNF stay
4. Medicaid can be retroactive up to 3 months

## Key Coordination Rules
1. Medicare is always PRIMARY payer
2. Medicaid pays what Medicare doesn't cover
3. Medicaid pays Medicare premiums for dual eligibles
4. No gap in coverage if properly coordinated
"""

ASSISTED_LIVING_REGULATIONS = """
# FLORIDA ASSISTED LIVING FACILITY REGULATIONS

## License Types
### Standard License
- Basic supervision and assistance
- Medication management
- Personal care assistance
- 24-hour staff availability

### Extended Congregate Care (ECC) License
- Higher level of nursing services
- Can accept residents who need more care
- Licensed nurses on staff
- Can provide limited nursing services

### Limited Nursing Services (LNS) License
- Can provide specific nursing services
- Medication administration by nurses
- Wound care, catheter care
- Insulin injections

### Limited Mental Health (LMH) License
- Specialized for mental health residents
- Additional staff training required
- Mental health services coordination

## Resident Rights (Florida Statute 429.28)
1. Live in a safe, decent, sanitary environment
2. Be treated with dignity and respect
3. Retain and use personal possessions
4. Privacy in treatment and personal care
5. Unrestricted communication with family
6. Manage own financial affairs
7. Voice grievances without retaliation
8. Refuse medication and treatment
9. Receive visitors at reasonable hours
10. Access to ombudsman program

## Admission Requirements
### Medical Documentation Needed
- Health assessment within 30 days of admission
- Physician orders for medications
- TB test results
- Cognitive assessment if memory care
- ADL (Activities of Daily Living) assessment

### Financial Requirements
- Proof of ability to pay
- Long-term care insurance verification
- Medicaid pending documentation if applicable
- Responsible party agreement

## Medicaid in Assisted Living
### OSS (Optional State Supplementation)
- Florida Medicaid program for ALF residents
- Covers room and board portion
- Facility must accept Medicaid rate
- Limited number of Medicaid beds per facility

### Medicaid Waiver Programs
- Assisted Living Waiver
- Long-Term Care Diversion Waiver
- Cover services beyond room and board
- Waitlists may apply

## Cost Structure
### Typical Monthly Costs (2026)
- Base rent: $3,500-6,000/month
- Care levels: Additional $500-2,500/month
- Memory care premium: Additional $1,000-2,000/month
- Community fee (one-time): $2,000-5,000
- Deposit: Usually equal to one month rent

### What's Typically Included
- Room and utilities
- Three meals daily
- Housekeeping and laundry
- Activities and transportation
- Basic personal care assistance
- Medication management

### What's Typically Extra
- Higher care levels
- Incontinence supplies
- Specialized therapies
- Beauty/barber services
- Guest meals
- Pet fees

## Discharge Rules
### Facility Can Discharge For
- Non-payment (30-day notice required)
- Resident's needs exceed license
- Facility closure
- Resident endangers others

### Resident Protections
- 30-day written notice required
- Right to appeal discharge
- Ombudsman assistance available
- Cannot discharge for filing complaints
"""

ESTATE_PLANNING_ELDER_CARE = """
# ESTATE PLANNING FOR ELDER CARE - FLORIDA

## Essential Documents
### Healthcare Documents
1. **Healthcare Surrogate Designation**
   - Names person to make medical decisions
   - Effective when patient cannot decide
   - Florida Statute 765.202
   - Must be witnessed by 2 adults

2. **Living Will (Advance Directive)**
   - States end-of-life wishes
   - Covers life-prolonging procedures
   - Florida Statute 765.302
   - Must be witnessed by 2 adults, 1 not family

3. **HIPAA Authorization**
   - Allows access to medical records
   - Name specific individuals
   - Can be broad or limited
   - Separate from healthcare surrogate

### Financial Documents
1. **Durable Power of Attorney**
   - Names agent for financial matters
   - "Durable" means survives incapacity
   - Florida Statute 709.2101
   - Must be notarized
   - Consider "springing" vs immediate

2. **Trust Documents**
   - Revocable Living Trust (avoid probate)
   - Irrevocable Trust (Medicaid planning)
   - Special Needs Trust (preserve benefits)

### After Death Documents
1. **Last Will and Testament**
   - Distributes probate assets
   - Names personal representative
   - Must be witnessed by 2 adults
   - Self-proving affidavit recommended

2. **Beneficiary Designations**
   - Life insurance
   - Retirement accounts
   - Bank accounts (POD)
   - Investment accounts (TOD)

## Medicaid Planning Considerations
### 5-Year Look-Back
- All transfers reviewed for 60 months
- Gifts create penalty periods
- Penalty = gift amount / $10,809
- Planning must start EARLY

### Exempt Transfers
- Transfers to spouse (unlimited)
- Transfers to disabled child
- Transfers to caregiver child (lived in home 2+ years)
- Transfers of homestead to certain family

### Asset Protection Strategies
1. **Spousal Protections**
   - CSRA (Community Spouse Resource Allowance): Up to $154,140
   - MMMNA (Monthly Maintenance Needs Allowance): Up to $3,853.50
   - Spousal refusal (last resort)

2. **Irrevocable Trusts**
   - Must be established 5+ years before need
   - Medicaid Asset Protection Trust
   - Income-only trust

3. **Annuities**
   - Medicaid-compliant annuities
   - Must be irrevocable, non-assignable
   - Actuarially sound
   - State named as remainder beneficiary

## Probate Avoidance
### Non-Probate Assets
- Joint accounts with right of survivorship
- POD (Payable on Death) accounts
- TOD (Transfer on Death) accounts
- Life insurance with named beneficiary
- Retirement accounts with named beneficiary
- Property in trust

### Florida Probate Thresholds
- Summary administration: Estate under $75,000
- Formal administration: Estate over $75,000
- Ancillary probate for out-of-state property

## Key Contacts
- Florida Bar Lawyer Referral: 1-800-342-8011
- Florida Elder Law Section: elderlaw.flabar.org
- Area Agency on Aging: 1-800-963-5337
"""

DOCUMENT_REQUIREMENTS = """
# DOCUMENT REQUIREMENTS FOR ELDER CARE APPLICATIONS

## Medicaid Application Documents
### Identity Documents
- [ ] Florida Driver's License or State ID
- [ ] Social Security Card
- [ ] Birth Certificate
- [ ] Marriage Certificate (if applicable)
- [ ] Divorce Decree (if applicable)
- [ ] Death Certificate of Spouse (if applicable)
- [ ] Naturalization Papers (if applicable)

### Financial Documents (60 months)
- [ ] Bank Statements - ALL accounts (60 months)
- [ ] Investment Account Statements (60 months)
- [ ] IRA/401k Statements (60 months)
- [ ] Life Insurance Policies (face value and cash value)
- [ ] Annuity Contracts
- [ ] Stock/Bond Certificates
- [ ] CD Certificates

### Income Documents
- [ ] Social Security Award Letter (current year)
- [ ] Pension Statements
- [ ] Annuity Payment Statements
- [ ] Rental Income Documentation
- [ ] Any Other Income Sources

### Property Documents
- [ ] Property Deeds
- [ ] Property Tax Statements
- [ ] Mortgage Statements
- [ ] Vehicle Titles
- [ ] Vehicle Registration

### Medical Documents
- [ ] Physician's Statement of Need
- [ ] CARES Assessment (scheduled by DCF)
- [ ] Hospital Discharge Summary
- [ ] Nursing Assessment
- [ ] Medication List

### Legal Documents
- [ ] Power of Attorney (Durable)
- [ ] Healthcare Surrogate Designation
- [ ] Trust Documents (if applicable)
- [ ] Guardianship Papers (if applicable)

## VA Aid & Attendance Documents
### Veteran Documents
- [ ] DD-214 (Discharge Papers)
- [ ] VA Claim Number (if prior claim)
- [ ] Marriage Certificate
- [ ] Death Certificate of Veteran (for survivors)

### Medical Documents
- [ ] Physician's Statement (VA Form 21-2680)
- [ ] Medical Records Supporting Need
- [ ] List of Medications
- [ ] Diagnosis Documentation

### Financial Documents
- [ ] Net Worth Statement
- [ ] Income Documentation
- [ ] Medical Expense Documentation
- [ ] Assisted Living/Care Costs

## Facility Admission Documents
### Required for Admission
- [ ] Photo ID
- [ ] Insurance Cards (Medicare, Medicaid, Private)
- [ ] Physician Orders
- [ ] Health Assessment (within 30 days)
- [ ] TB Test Results
- [ ] Medication List with Dosages
- [ ] Advance Directives
- [ ] Emergency Contact Information
- [ ] Responsible Party Agreement

### Financial Documents
- [ ] Proof of Income
- [ ] Long-Term Care Insurance Policy
- [ ] Medicaid Approval Letter (if applicable)
- [ ] Payment Agreement

## Tips for Document Collection
1. Start gathering documents IMMEDIATELY
2. Request bank statements online (faster)
3. Order death certificates (10+ copies)
4. Keep originals, provide copies
5. Organize by category in folders
6. Create digital backups
7. Note any missing documents early
"""

CARE_TRANSITION_CHECKLIST = """
# CARE TRANSITION CHECKLIST - HOSPITAL TO FACILITY

## Before Discharge (Days 1-3)
### Immediate Actions
- [ ] Meet with hospital discharge planner
- [ ] Request PT/OT evaluation for care level
- [ ] Get physician orders for facility admission
- [ ] Obtain discharge summary
- [ ] Get medication reconciliation list

### Facility Selection
- [ ] Identify facilities accepting patient's care level
- [ ] Verify Medicaid acceptance (if applicable)
- [ ] Schedule facility tours
- [ ] Check state inspection reports (AHCA)
- [ ] Verify availability/waitlist status

### Financial Planning
- [ ] Calculate monthly care costs
- [ ] Review insurance coverage
- [ ] Start Medicaid application if needed
- [ ] Contact VA if veteran/survivor
- [ ] Identify funding gap and plan

## Week 1: Documentation
### Medical Records
- [ ] Hospital discharge summary
- [ ] Nursing assessment
- [ ] PT/OT evaluation
- [ ] Medication list with dosages
- [ ] Physician orders for facility

### Legal Documents
- [ ] Power of Attorney (if not already done)
- [ ] Healthcare Surrogate
- [ ] Advance Directive
- [ ] HIPAA Authorization

### Financial Documents
- [ ] Begin gathering bank statements
- [ ] Locate insurance policies
- [ ] Find property deeds
- [ ] Gather income documentation

## Week 2: Applications
### Medicaid (if applicable)
- [ ] Complete ACCESS Florida application
- [ ] Submit required documents
- [ ] Schedule CARES assessment
- [ ] Provide facility information

### VA Benefits (if applicable)
- [ ] Obtain DD-214
- [ ] Complete VA Form 21-534EZ (survivors) or 21-2680
- [ ] Gather medical evidence
- [ ] Submit application

### Facility
- [ ] Complete admission paperwork
- [ ] Sign resident agreement
- [ ] Pay deposit/community fee
- [ ] Provide insurance information

## Week 3-4: Transition
### Move Preparation
- [ ] Create list of items to bring
- [ ] Label all clothing and belongings
- [ ] Arrange transportation
- [ ] Notify current providers of move

### Day of Move
- [ ] Bring all medications in original bottles
- [ ] Bring medical equipment (wheelchair, walker)
- [ ] Bring comfort items (photos, blanket)
- [ ] Meet with facility staff
- [ ] Review care plan

### Post-Move (First Week)
- [ ] Attend care plan meeting
- [ ] Meet with social worker
- [ ] Set up family communication plan
- [ ] Address any concerns immediately
- [ ] Update address with SSA, VA, banks

## Ongoing Tasks
### Monthly
- [ ] Review care plan
- [ ] Check medication accuracy
- [ ] Review billing statements
- [ ] Visit regularly

### Quarterly
- [ ] Attend care conferences
- [ ] Review Medicaid status
- [ ] Update financial documents
- [ ] Assess care level appropriateness

### Annually
- [ ] Medicaid redetermination
- [ ] VA benefit review
- [ ] Update legal documents if needed
- [ ] Review facility satisfaction
"""

FLORIDA_ALF_INSPECTION_GUIDE = """
# FLORIDA ASSISTED LIVING FACILITY INSPECTION GUIDE

## How to Research Facilities
### AHCA (Agency for Health Care Administration)
- Website: ahca.myflorida.com
- Search: Facility Locator
- View: Inspection reports, complaints, deficiencies

### What to Look For in Reports
1. **Class I Deficiencies** (Most Serious)
   - Immediate threat to health/safety
   - Facility must correct immediately
   - May result in license action

2. **Class II Deficiencies** (Serious)
   - Direct threat to health/safety
   - Must correct within specified time
   - Repeated violations = fines

3. **Class III Deficiencies** (Minor)
   - Indirect threat
   - Must correct within specified time

### Red Flags
- Multiple Class I or II deficiencies
- Repeated same deficiencies
- Complaints about medication errors
- Staffing violations
- Abuse/neglect allegations
- Financial exploitation reports

## Questions to Ask During Tours
### Staffing
1. What is the staff-to-resident ratio?
2. How many nurses on each shift?
3. What training do caregivers receive?
4. How long have staff members worked here?
5. Is there a nurse on-site 24/7?

### Care
1. How do you handle medical emergencies?
2. What happens if care needs increase?
3. How are medications managed?
4. What activities are offered?
5. How do you handle dementia/wandering?

### Costs
1. What is included in base rate?
2. What are the care level charges?
3. How often do rates increase?
4. What is the discharge policy?
5. Is there a Medicaid bed available?

### Quality of Life
1. Can residents personalize rooms?
2. What are visiting hours?
3. Are pets allowed?
4. What is the food like? (ask to see menu)
5. How do you handle complaints?

## Ombudsman Program
### What They Do
- Advocate for residents
- Investigate complaints
- Mediate disputes
- Provide information
- FREE service

### Contact
- Florida Long-Term Care Ombudsman: 1-888-831-0404
- Local ombudsman: Contact Area Agency on Aging

## Filing Complaints
### AHCA Complaint Hotline
- Phone: 1-888-419-3456
- Online: ahca.myflorida.com/complaint

### What to Report
- Abuse or neglect
- Medication errors
- Staffing problems
- Unsafe conditions
- Billing issues
- Rights violations
"""


_service: Optional[KnowledgeBaseService] = None


def get_knowledge_base_service() -> KnowledgeBaseService:
    """Get or create the knowledge base service singleton."""
    global _service
    if _service is None:
        _service = KnowledgeBaseService()
        _service.load_knowledge_base()
    return _service
