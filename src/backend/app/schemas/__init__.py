"""Pydantic schemas for CareNav Florida API."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


# Patient schemas
class CareNeedsCreate(BaseModel):
    bathing: bool = False
    dressing: bool = False
    toileting: bool = False
    transferring: bool = False
    eating: bool = False
    continence: bool = False
    medication_management: bool = False
    dementia_diagnosis: bool = False
    wandering_risk: bool = False
    behavioral_issues: bool = False
    skilled_nursing: bool = False
    physical_therapy: bool = False
    wound_care: bool = False
    iv_therapy: bool = False


class VeteranStatusCreate(BaseModel):
    is_veteran: bool = False
    is_spouse_of_veteran: bool = False
    veteran_deceased: bool = False
    branch: Optional[str] = None
    service_start: Optional[date] = None
    service_end: Optional[date] = None
    wartime_service: bool = False
    discharge_type: Optional[str] = None
    dd214_available: bool = False


class FinancialsCreate(BaseModel):
    # Income
    social_security: float = 0
    pension: float = 0
    va_pension: float = 0
    other_income: float = 0
    
    # Bank accounts
    checking: float = 0
    savings: float = 0
    cds: float = 0
    money_market: float = 0
    
    # Investments
    ira: float = 0
    four01k: float = 0
    brokerage: float = 0
    annuities: float = 0
    stocks: float = 0
    bonds: float = 0
    
    # Real estate
    owns_home: bool = False
    home_value: float = 0
    home_mortgage: float = 0
    intends_to_return: bool = True
    
    # Vehicles
    vehicle_1_value: float = 0
    vehicle_2_value: float = 0
    
    # Life insurance
    life_insurance_face: float = 0
    life_insurance_cash: float = 0
    
    # Debts
    credit_card_debt: float = 0
    medical_debt: float = 0
    other_debt: float = 0


class GiftCreate(BaseModel):
    gift_date: date
    recipient: str
    amount: float
    description: Optional[str] = None
    potentially_exempt: bool = False


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    ssn_last_four: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: str = "FL"
    zip_code: str
    county: str
    phone: Optional[str] = None
    current_location: str = "home"
    diagnosis: Optional[str] = None
    discharge_date: Optional[date] = None
    care_level_needed: str = "AL"
    
    # Ticket 1: Spouse Death fields
    spouse_deceased: bool = False
    deceased_spouse_name: Optional[str] = None
    spouse_date_of_death: Optional[date] = None
    death_cert_status: str = "not_ordered"
    marriage_date: Optional[date] = None
    marriage_location: Optional[str] = None
    deceased_was_veteran: bool = False
    
    care_needs: Optional[CareNeedsCreate] = None
    veteran_status: Optional[VeteranStatusCreate] = None
    financials: Optional[FinancialsCreate] = None
    gifts: Optional[list[GiftCreate]] = None


class PatientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    zip_code: str
    county: str
    current_location: str
    care_level_needed: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat schemas
class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    message: str
    patient_id: Optional[int] = None
    conversation_history: Optional[list[ChatMessage]] = None


class ActionItem(BaseModel):
    action: str
    priority: str
    phone: Optional[str] = None
    deadline: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    action_items: list[ActionItem] = []
    warnings: list[str] = []
    confidence: int = 75


# Eligibility schemas
class EligibilityRequest(BaseModel):
    patient_id: Optional[int] = None
    financials: Optional[FinancialsCreate] = None
    veteran_status: Optional[VeteranStatusCreate] = None
    gifts: Optional[list[GiftCreate]] = None


class MedicaidResult(BaseModel):
    eligible: bool
    countable: float
    over_by: float
    asset_eligible: bool
    income_eligible: bool
    total_income: float
    explanation: str


class VAResult(BaseModel):
    eligible: bool
    type: str
    monthly_benefit: float
    explanation: str


class GiftPenaltyResult(BaseModel):
    has_penalty: bool
    amount: float
    months: int
    mitigation: str


class EligibilityResponse(BaseModel):
    medicaid: MedicaidResult
    va_aa: VAResult
    gift_penalty: GiftPenaltyResult
    confidence: int


# Facility schemas
class FacilitySearchRequest(BaseModel):
    zip_code: str
    care_level: str = "AL"
    radius_miles: int = 20
    medicaid_required: bool = True
    patient_income: float = 0
    va_benefit: float = 0


class AffordabilityInfo(BaseModel):
    monthly_rate: float
    patient_income: float
    va_benefit: float
    total_income: float
    gap_or_surplus: float
    affordable: bool
    needs_asset_draw: bool
    monthly_shortfall: float


class FacilityResult(BaseModel):
    name: str
    address: str
    phone: str
    license_type: str
    capacity: int
    beds_available: Optional[int] = None
    rate_low: float
    rate_high: float
    accepts_medicaid: bool
    medicaid_day_one: bool
    memory_care: bool
    rating: float
    distance_miles: float
    match_score: int
    affordability: AffordabilityInfo


class FacilitySearchResponse(BaseModel):
    facilities: list[FacilityResult]
    search_criteria: dict
    total_found: int


# Task schemas (Ticket 2: added dependencies + assignees)
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "general"
    priority: str = "medium"
    due_date: Optional[date] = None
    phone: Optional[str] = None
    phone_name: Optional[str] = None
    assignee: Optional[str] = None
    blocked_by_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: str
    priority: str
    status: str
    due_date: Optional[date]
    phone: Optional[str]
    phone_name: Optional[str] = None
    assignee: Optional[str] = None
    blocked_by_id: Optional[int] = None
    completed_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Document schemas
class DocumentCreate(BaseModel):
    name: str
    doc_type: str
    status: str = "needed"
    notes: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    name: str
    doc_type: str
    status: str
    notes: Optional[str]
    # Ticket 7: Document Location + Procurement
    physical_location: Optional[str] = None
    procurement_status: str = "in_hand"
    ordered_from: Optional[str] = None
    expected_delivery: Optional[date] = None
    copies_needed: int = 1
    copies_on_hand: int = 0
    needed_for: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Ticket 3: Bill Tracking schemas
class BillCreate(BaseModel):
    vendor: str
    amount: float
    due_date: Optional[date] = None
    category: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    payment_link: Optional[str] = None
    recurring: bool = False
    notes: Optional[str] = None


class BillResponse(BaseModel):
    id: int
    vendor: str
    amount: float
    due_date: Optional[date]
    status: str
    amount_paid: float
    category: Optional[str]
    contact_name: Optional[str]
    contact_phone: Optional[str]
    payment_link: Optional[str]
    recurring: bool
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class BillUpdate(BaseModel):
    status: Optional[str] = None
    amount_paid: Optional[float] = None
    notes: Optional[str] = None


# Ticket 4: Income Phases schemas
class IncomePhaseCreate(BaseModel):
    phase_name: str
    monthly_amount: float
    source: str
    status: str = "future"
    estimated_start: Optional[str] = None
    notes: Optional[str] = None


class IncomePhaseResponse(BaseModel):
    id: int
    phase_name: str
    monthly_amount: float
    source: str
    status: str
    estimated_start: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Ticket 5: Benefit Application Pipeline schemas
class BenefitApplicationCreate(BaseModel):
    benefit_type: str
    display_name: str
    monthly_amount: Optional[float] = None
    status: str = "researching"
    expected_weeks: Optional[int] = None
    missing_documents: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


class BenefitApplicationResponse(BaseModel):
    id: int
    benefit_type: str
    display_name: str
    status: str
    monthly_amount: Optional[float]
    submitted_date: Optional[date]
    expected_weeks: Optional[int]
    missing_documents: Optional[str]
    contact_phone: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class BenefitApplicationUpdate(BaseModel):
    status: Optional[str] = None
    submitted_date: Optional[date] = None
    missing_documents: Optional[str] = None
    notes: Optional[str] = None


# Ticket 6: Contact Directory schemas
class ContactCreate(BaseModel):
    name: str
    organization: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    name: str
    organization: Optional[str]
    role: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    category: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Ticket 8: Asset Sale Pipeline schemas
class AssetCreate(BaseModel):
    name: str
    asset_type: Optional[str] = None
    owner: Optional[str] = None
    estimated_value: Optional[float] = None
    title_status: str = "in_hand"
    sale_status: str = "not_for_sale"
    sale_channel: Optional[str] = None
    linked_insurance: Optional[str] = None
    notes: Optional[str] = None


class AssetResponse(BaseModel):
    id: int
    name: str
    asset_type: Optional[str]
    owner: Optional[str]
    estimated_value: Optional[float]
    title_status: str
    sale_status: str
    sale_channel: Optional[str]
    actual_sale_price: Optional[float]
    sale_date: Optional[date]
    linked_insurance: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssetUpdate(BaseModel):
    title_status: Optional[str] = None
    sale_status: Optional[str] = None
    sale_channel: Optional[str] = None
    actual_sale_price: Optional[float] = None
    sale_date: Optional[date] = None
    notes: Optional[str] = None
