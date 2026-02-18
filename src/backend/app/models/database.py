"""SQLite database models for CareNav Florida."""
# Built by Gregory Katz and Rick Weyenberg
# Code is as-is, open source

from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime,
    ForeignKey, Numeric, JSON, create_engine
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# ============================================================
# AZURE SQL SWAP — Rick: Uncomment this block after provisioning
# Azure SQL Server + Database (see RICK_ENGINEERING_WORKBOOK.md §1A)
# ============================================================
# import os
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
#
# AZURE_SQL_CONNECTION = (
#     "mssql+aioodbc://"
#     f"{os.getenv('AZURE_SQL_USERNAME')}:{os.getenv('AZURE_SQL_PASSWORD')}"
#     f"@{os.getenv('AZURE_SQL_SERVER')}/{os.getenv('AZURE_SQL_DATABASE')}"
#     "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
# )
#
# # Replace the SQLite engine below with:
# # engine = create_async_engine(AZURE_SQL_CONNECTION, echo=False)
# ============================================================

Base = declarative_base()


class User(Base):
    """The adult child navigating care for their parent."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True)
    name = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    
    patients = relationship("Patient", back_populates="user")


class Patient(Base):
    """The parent needing care."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date)
    ssn_last_four = Column(String(4))
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(2), default="FL")
    zip_code = Column(String(10))
    county = Column(String(100))
    phone = Column(String(50))
    current_location = Column(String(50), default="home")  # hospital, home, rehab, al, snf
    diagnosis = Column(Text)
    discharge_date = Column(Date)
    care_level_needed = Column(String(10), default="AL")  # AL, MC, SNF
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Ticket 1: Spouse Death fields
    spouse_deceased = Column(Boolean, default=False)
    deceased_spouse_name = Column(String(255))
    spouse_date_of_death = Column(Date)
    death_cert_status = Column(String(50), default="not_ordered")  # not_ordered, ordered, received
    marriage_date = Column(Date)
    marriage_location = Column(String(255))
    deceased_was_veteran = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="patients")
    care_needs = relationship("CareNeeds", back_populates="patient", uselist=False)
    veteran_status = relationship("VeteranStatus", back_populates="patient", uselist=False)
    financials = relationship("Financials", back_populates="patient")
    gifts = relationship("Gift", back_populates="patient")
    documents = relationship("Document", back_populates="patient")
    tasks = relationship("Task", back_populates="patient")
    facility_matches = relationship("FacilityMatch", back_populates="patient")
    conversations = relationship("Conversation", back_populates="patient")
    bills = relationship("Bill", back_populates="patient")
    income_phases = relationship("IncomePhase", back_populates="patient")
    benefit_applications = relationship("BenefitApplication", back_populates="patient")
    contacts = relationship("Contact", back_populates="patient")
    assets = relationship("Asset", back_populates="patient")
    # New relationships
    medical_info = relationship("MedicalInfo", back_populates="patient", uselist=False)
    diagnoses = relationship("Diagnosis", back_populates="patient")
    medications = relationship("Medication", back_populates="patient")
    insurance_policies = relationship("Insurance", back_populates="patient")
    selected_facility = relationship("SelectedFacility", back_populates="patient", uselist=False)
    wins = relationship("Win", back_populates="patient")


class CareNeeds(Base):
    """Care needs assessment for a patient."""
    __tablename__ = "care_needs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    
    # ADLs (Activities of Daily Living)
    bathing = Column(Boolean, default=False)
    dressing = Column(Boolean, default=False)
    toileting = Column(Boolean, default=False)
    transferring = Column(Boolean, default=False)
    eating = Column(Boolean, default=False)
    continence = Column(Boolean, default=False)
    
    # Medication and Cognitive
    medication_management = Column(Boolean, default=False)
    dementia_diagnosis = Column(Boolean, default=False)
    wandering_risk = Column(Boolean, default=False)
    behavioral_issues = Column(Boolean, default=False)
    
    # Skilled Medical
    skilled_nursing = Column(Boolean, default=False)
    physical_therapy = Column(Boolean, default=False)
    wound_care = Column(Boolean, default=False)
    iv_therapy = Column(Boolean, default=False)
    
    # Computed
    recommended_care_level = Column(String(10))  # AL, MC, SNF
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="care_needs")


class VeteranStatus(Base):
    """Veteran status for VA benefits eligibility."""
    __tablename__ = "veteran_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    
    is_veteran = Column(Boolean, default=False)
    is_spouse_of_veteran = Column(Boolean, default=False)
    veteran_deceased = Column(Boolean, default=False)
    wartime_service = Column(Boolean, default=False)
    branch = Column(String(50))
    service_start = Column(Date)
    service_end = Column(Date)
    discharge_type = Column(String(50))
    dd214_available = Column(Boolean, default=False)
    va_eligible = Column(Boolean, default=False)
    va_benefit_amount = Column(Numeric(10, 2))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="veteran_status")


class Financials(Base):
    """Financial snapshot for eligibility calculations."""
    __tablename__ = "financials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    snapshot_date = Column(Date, default=date.today)
    
    # Income (monthly)
    social_security = Column(Numeric(10, 2), default=0)
    pension = Column(Numeric(10, 2), default=0)
    va_pension = Column(Numeric(10, 2), default=0)
    other_income = Column(Numeric(10, 2), default=0)
    
    # Bank Accounts
    checking = Column(Numeric(10, 2), default=0)
    savings = Column(Numeric(10, 2), default=0)
    cds = Column(Numeric(10, 2), default=0)
    money_market = Column(Numeric(10, 2), default=0)
    
    # Investments
    ira = Column(Numeric(10, 2), default=0)
    four01k = Column(Numeric(10, 2), default=0)
    brokerage = Column(Numeric(10, 2), default=0)
    annuities = Column(Numeric(10, 2), default=0)
    stocks = Column(Numeric(10, 2), default=0)
    bonds = Column(Numeric(10, 2), default=0)
    
    # Life Insurance
    life_insurance_face = Column(Numeric(10, 2), default=0)
    life_insurance_cash = Column(Numeric(10, 2), default=0)
    
    # Property
    home_value = Column(Numeric(10, 2), default=0)
    home_mortgage = Column(Numeric(10, 2), default=0)
    owns_home = Column(Boolean, default=False)
    intends_to_return = Column(Boolean, default=True)
    vehicle_1_value = Column(Numeric(10, 2), default=0)
    vehicle_2_value = Column(Numeric(10, 2), default=0)
    
    # Other
    jewelry = Column(Numeric(10, 2), default=0)
    household_goods = Column(Numeric(10, 2), default=0)
    
    # Debts
    credit_card_debt = Column(Numeric(10, 2), default=0)
    medical_debt = Column(Numeric(10, 2), default=0)
    other_debt = Column(Numeric(10, 2), default=0)
    
    # Computed (stored for quick access)
    countable_assets = Column(Numeric(10, 2))
    exempt_assets = Column(Numeric(10, 2))
    medicaid_eligible = Column(Boolean)
    over_limit_by = Column(Numeric(10, 2))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="financials")


class Gift(Base):
    """Gift/transfer history for look-back period analysis."""
    __tablename__ = "gifts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    amount = Column(Numeric(10, 2))
    recipient = Column(String(255))
    description = Column(Text)
    gift_date = Column(Date)
    documented = Column(Boolean, default=False)
    document_path = Column(String(500))
    potentially_exempt = Column(Boolean, default=False)
    exemption_reason = Column(Text)
    penalty_months = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="gifts")


class Document(Base):
    """Document tracking for applications."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    name = Column(String(255), nullable=False)
    category = Column(String(50))  # income, bank, insurance, legal, veteran, property, medical, ai_analysis
    doc_type = Column(String(100))  # bank_statement, dd214, death_cert, medical_record, ai_report, etc.
    status = Column(String(20), default="needed")  # needed, requested, uploaded, verified, generated
    file_path = Column(String(500))
    content = Column(Text)  # Full text content for RAG indexing
    extracted_data = Column(JSON)  # Structured data extracted from document
    ai_analysis = Column(Text)  # AI-generated analysis of the document
    phone_to_request = Column(String(50))
    company_name = Column(String(255))
    due_date = Column(Date)
    notes = Column(Text)
    uploaded_at = Column(DateTime)
    verified_at = Column(DateTime)
    indexed_in_chroma = Column(Boolean, default=False)  # Whether indexed in ChromaDB
    
    # Ticket 7: Document Location + Procurement
    physical_location = Column(String(255))  # e.g., "Filing cabinet", "Safe deposit box", "Attorney's office"
    procurement_status = Column(String(20), default="in_hand")  # in_hand, ordered, in_transit
    ordered_from = Column(String(255))  # e.g., "FL Vital Records", "VA Records Center"
    expected_delivery = Column(Date)
    copies_needed = Column(Integer, default=1)
    copies_on_hand = Column(Integer, default=0)
    needed_for = Column(Text)  # JSON: which benefits need this doc
    
    patient = relationship("Patient", back_populates="documents")


class Task(Base):
    """Tasks/actions for the user to complete."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default="medium")  # urgent, high, medium, low
    category = Column(String(50))  # legal, financial, facility, document, benefit, estate
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled, blocked
    due_date = Column(Date)
    phone = Column(String(50))
    contact_name = Column(String(255))
    notes = Column(Text)  # User notes for RAG context
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Ticket 2: Task Dependencies + Assignees
    blocked_by_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    assignee = Column(String(50))  # primary, secondary, both, attorney, social_worker
    phone_name = Column(String(255))  # Name associated with phone number
    completed_date = Column(Date)
    
    patient = relationship("Patient", back_populates="tasks")
    blocked_by = relationship("Task", remote_side=[id], backref="blocks")


class Facility(Base):
    """Cached facility information from searches."""
    __tablename__ = "facilities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    license_number = Column(String(50), unique=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(2), default="FL")
    zip_code = Column(String(10))
    county = Column(String(100))
    phone = Column(String(50))
    website = Column(String(500))
    license_type = Column(String(10))  # ALF, SNF, AFC
    capacity = Column(Integer)
    
    # Medicaid
    accepts_medicaid = Column(Boolean)
    medicaid_day_one = Column(Boolean)
    private_pay_months = Column(Integer)
    
    # Rates
    rate_low = Column(Numeric(10, 2))
    rate_high = Column(Numeric(10, 2))
    rate_memory_care = Column(Numeric(10, 2))
    
    # Features
    memory_care = Column(Boolean, default=False)
    skilled_nursing = Column(Boolean, default=False)
    rehab_services = Column(Boolean, default=False)
    
    # Quality
    rating = Column(Numeric(2, 1))
    review_count = Column(Integer)
    last_inspection_date = Column(Date)
    violations_12_months = Column(Integer)
    
    # Location
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    
    # Meta
    data_source = Column(String(100))
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    matches = relationship("FacilityMatch", back_populates="facility")


class FacilityMatch(Base):
    """Facility matches for a specific patient."""
    __tablename__ = "facility_matches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    facility_id = Column(Integer, ForeignKey("facilities.id"))
    match_score = Column(Integer)  # 0-100
    distance_miles = Column(Numeric(5, 2))
    affordability_gap = Column(Numeric(10, 2))  # negative = surplus
    toured = Column(Boolean, default=False)
    tour_date = Column(Date)
    tour_notes = Column(Text)
    interested = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="facility_matches")
    facility = relationship("Facility", back_populates="matches")


class Conversation(Base):
    """Conversation history for RAG and context."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    role = Column(String(20))  # user, assistant, system
    content = Column(Text)
    agent = Column(String(50))  # orchestrator, eligibility, facility, legal, validator, summarizer
    extra_data = Column(JSON)  # renamed from metadata to avoid SQLAlchemy reserved name
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="conversations")
    agent_outputs = relationship("AgentOutput", back_populates="conversation")


class AgentOutput(Base):
    """Agent outputs for validation and audit."""
    __tablename__ = "agent_outputs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    agent = Column(String(50), nullable=False)
    input_prompt = Column(Text)
    output_response = Column(JSON)
    confidence = Column(Integer)
    dissent = Column(Boolean, default=False)
    dissent_reason = Column(Text)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="agent_outputs")


# Ticket 3: Bill Tracking
class Bill(Base):
    """Bills and payments tracking."""
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    vendor = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2))
    due_date = Column(Date)
    status = Column(String(20), default="unpaid")  # unpaid, partial, paid, overdue
    amount_paid = Column(Numeric(10, 2), default=0)
    category = Column(String(50))  # facility, funeral, utility, lot_rent, medical, insurance
    contact_name = Column(String(255))
    contact_phone = Column(String(50))
    payment_link = Column(String(500))
    recurring = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="bills")


# Ticket 4: Income Phases
class IncomePhase(Base):
    """Income phases for financial planning."""
    __tablename__ = "income_phases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    phase_name = Column(String(100))  # Phase 1: Current, Phase 2: After SSA, Phase 3: After VA
    monthly_amount = Column(Numeric(10, 2))
    source = Column(String(100))  # social_security, va_survivor, pension, etc.
    status = Column(String(20), default="future")  # current, submitted, preparing, future, active
    estimated_start = Column(String(50))  # e.g., "March 2026", "After VA approval"
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="income_phases")


# Ticket 5: Benefit Application Pipeline
class BenefitApplication(Base):
    """Benefit application tracking."""
    __tablename__ = "benefit_applications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    benefit_type = Column(String(50))  # ssa_survivor, va_aa, medicaid_icp, medicare
    display_name = Column(String(255))
    status = Column(String(20), default="researching")  # researching, preparing, submitted, processing, approved, denied
    monthly_amount = Column(Numeric(10, 2))
    submitted_date = Column(Date)
    expected_weeks = Column(Integer)
    missing_documents = Column(Text)  # JSON list of missing doc names
    contact_phone = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="benefit_applications")


# Ticket 6: Contact Directory
class Contact(Base):
    """Contact directory for case management."""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    name = Column(String(255), nullable=False)
    organization = Column(String(255))
    role = Column(String(100))
    phone = Column(String(50))
    email = Column(String(255))
    category = Column(String(50))  # facility, legal, government, insurance, family, medical
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="contacts")


# Ticket 8: Asset Sale Pipeline
class Asset(Base):
    """Asset tracking with sale pipeline."""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    name = Column(String(255), nullable=False)
    asset_type = Column(String(50))  # vehicle, property, jewelry, account, other
    owner = Column(String(50))  # deceased, patient, joint
    estimated_value = Column(Numeric(10, 2))
    title_status = Column(String(20), default="in_hand")  # in_hand, ordered, in_transit, not_needed
    sale_status = Column(String(20), default="not_for_sale")  # not_for_sale, preparing, listed, pending_sale, sold
    sale_channel = Column(String(100))  # private, dealer, auction, estate_sale
    actual_sale_price = Column(Numeric(10, 2))
    sale_date = Column(Date)
    linked_insurance = Column(String(255))  # Insurance to cancel AFTER sale
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="assets")


# NEW: Medical Information
class MedicalInfo(Base):
    """Medical information for patient."""
    __tablename__ = "medical_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    
    # Basic Info
    medicare_id = Column(String(50))
    medicaid_id = Column(String(50))
    physician_name = Column(String(255))
    physician_phone = Column(String(50))
    
    # Vitals
    blood_pressure = Column(String(20))
    pulse = Column(Integer)
    temperature = Column(Numeric(4, 1))
    respiration = Column(Integer)
    vitals_date = Column(Date)
    
    # Care Info
    allergies = Column(Text)  # JSON list
    diet = Column(String(255))
    code_status = Column(String(50))  # FULL CODE, DNR, DNI, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="medical_info")


class Diagnosis(Base):
    """Diagnoses for patient."""
    __tablename__ = "diagnoses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    name = Column(String(255), nullable=False)
    icd_code = Column(String(20))
    diagnosis_date = Column(Date)
    is_primary = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="diagnoses")


class Medication(Base):
    """Medications for patient."""
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    name = Column(String(255), nullable=False)
    dosage = Column(String(100))
    frequency = Column(String(100))
    route = Column(String(50))  # oral, injection, topical, etc.
    purpose = Column(String(255))
    prescriber = Column(String(255))
    start_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="medications")


# NEW: Insurance Information
class Insurance(Base):
    """Insurance policies for patient."""
    __tablename__ = "insurance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    insurance_type = Column(String(50))  # medicare, medicaid, private, supplemental
    carrier = Column(String(255))
    policy_number = Column(String(100))
    group_number = Column(String(100))
    subscriber_name = Column(String(255))
    subscriber_id = Column(String(100))
    effective_date = Column(Date)
    termination_date = Column(Date)
    phone = Column(String(50))
    status = Column(String(20), default="active")  # active, pending, terminated
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="insurance_policies")


# NEW: Selected Facility (like Barr. tab)
class SelectedFacility(Base):
    """Selected/target facility with detailed info."""
    __tablename__ = "selected_facilities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    
    # Basic Info
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    apt_number = Column(String(50))
    phone = Column(String(50))
    fax = Column(String(50))
    
    # Contacts
    admissions_contact = Column(String(255))
    community_rep = Column(String(255))
    
    # Dates
    keys_date = Column(DateTime)
    move_in_date = Column(Date)
    
    # Costs
    base_rent = Column(Numeric(10, 2))
    vet_discount_pct = Column(Numeric(5, 2))
    care_level = Column(String(100))
    care_level_cost = Column(Numeric(10, 2))
    total_monthly = Column(Numeric(10, 2))
    deposit_amount = Column(Numeric(10, 2))
    deposit_paid = Column(Boolean, default=False)
    community_fee = Column(Numeric(10, 2))
    
    # Status
    status = Column(String(20), default="selected")  # selected, confirmed, moved_in
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="selected_facility")


# NEW: Recent Wins / Accomplishments
class Win(Base):
    """Recent wins/accomplishments to celebrate."""
    __tablename__ = "wins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    amount = Column(Numeric(10, 2))  # For financial wins
    amount_type = Column(String(20))  # one_time, monthly, saved
    win_date = Column(Date)
    category = Column(String(50))  # financial, legal, medical, facility, document
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="wins")


_engine = None
_session_maker = None


async def init_db(database_url: str = "sqlite+aiosqlite:///./carenav.db"):
    """Initialize the database and create all tables."""
    global _engine, _session_maker
    _engine = create_async_engine(database_url, echo=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Run migrations for existing databases
        await conn.run_sync(_run_migrations)
    _session_maker = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine


def _run_migrations(connection):
    """Run schema migrations for existing databases."""
    from sqlalchemy import text, inspect
    
    inspector = inspect(connection)
    tables = inspector.get_table_names()
    
    # Check if documents table exists and needs migration
    if 'documents' in tables:
        columns = [col['name'] for col in inspector.get_columns('documents')]
        
        # Add missing columns to documents table
        doc_migrations = [
            ("doc_type", "ALTER TABLE documents ADD COLUMN doc_type VARCHAR(100)"),
            ("content", "ALTER TABLE documents ADD COLUMN content TEXT"),
            ("extracted_data", "ALTER TABLE documents ADD COLUMN extracted_data JSON"),
            ("ai_analysis", "ALTER TABLE documents ADD COLUMN ai_analysis TEXT"),
            ("indexed_in_chroma", "ALTER TABLE documents ADD COLUMN indexed_in_chroma BOOLEAN DEFAULT 0"),
            # Ticket 7: Document Location + Procurement
            ("physical_location", "ALTER TABLE documents ADD COLUMN physical_location VARCHAR(255)"),
            ("procurement_status", "ALTER TABLE documents ADD COLUMN procurement_status VARCHAR(20) DEFAULT 'in_hand'"),
            ("ordered_from", "ALTER TABLE documents ADD COLUMN ordered_from VARCHAR(255)"),
            ("expected_delivery", "ALTER TABLE documents ADD COLUMN expected_delivery DATE"),
            ("copies_needed", "ALTER TABLE documents ADD COLUMN copies_needed INTEGER DEFAULT 1"),
            ("copies_on_hand", "ALTER TABLE documents ADD COLUMN copies_on_hand INTEGER DEFAULT 0"),
            ("needed_for", "ALTER TABLE documents ADD COLUMN needed_for TEXT"),
        ]
        
        for col_name, sql in doc_migrations:
            if col_name not in columns:
                try:
                    connection.execute(text(sql))
                except Exception as e:
                    print(f"Migration warning for documents.{col_name}: {e}")
    
    # Ticket 1: Spouse Death fields on patients table
    if 'patients' in tables:
        columns = [col['name'] for col in inspector.get_columns('patients')]
        patient_migrations = [
            ("spouse_deceased", "ALTER TABLE patients ADD COLUMN spouse_deceased BOOLEAN DEFAULT 0"),
            ("deceased_spouse_name", "ALTER TABLE patients ADD COLUMN deceased_spouse_name VARCHAR(255)"),
            ("spouse_date_of_death", "ALTER TABLE patients ADD COLUMN spouse_date_of_death DATE"),
            ("death_cert_status", "ALTER TABLE patients ADD COLUMN death_cert_status VARCHAR(50) DEFAULT 'not_ordered'"),
            ("marriage_date", "ALTER TABLE patients ADD COLUMN marriage_date DATE"),
            ("marriage_location", "ALTER TABLE patients ADD COLUMN marriage_location VARCHAR(255)"),
            ("deceased_was_veteran", "ALTER TABLE patients ADD COLUMN deceased_was_veteran BOOLEAN DEFAULT 0"),
        ]
        for col_name, sql in patient_migrations:
            if col_name not in columns:
                try:
                    connection.execute(text(sql))
                except Exception as e:
                    print(f"Migration warning for patients.{col_name}: {e}")
    
    # Ticket 2: Task Dependencies fields on tasks table
    if 'tasks' in tables:
        columns = [col['name'] for col in inspector.get_columns('tasks')]
        task_migrations = [
            ("blocked_by_id", "ALTER TABLE tasks ADD COLUMN blocked_by_id INTEGER REFERENCES tasks(id)"),
            ("assignee", "ALTER TABLE tasks ADD COLUMN assignee VARCHAR(50)"),
            ("phone_name", "ALTER TABLE tasks ADD COLUMN phone_name VARCHAR(255)"),
            ("completed_date", "ALTER TABLE tasks ADD COLUMN completed_date DATE"),
        ]
        for col_name, sql in task_migrations:
            if col_name not in columns:
                try:
                    connection.execute(text(sql))
                except Exception as e:
                    print(f"Migration warning for tasks.{col_name}: {e}")


def get_async_session_maker():
    """Get the async session maker."""
    global _session_maker
    if _session_maker is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    return _session_maker
