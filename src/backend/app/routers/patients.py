"""
Patient API endpoints for CareNav Florida (Ticket 1: Spouse Death Intake).
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models.database import (
    Patient, CareNeeds, VeteranStatus, Financials, Gift, get_async_session_maker
)
from app.schemas import (
    PatientCreate, PatientResponse, GiftCreate
)
from app.services.estate_tasks import generate_estate_tasks

router = APIRouter(prefix="/patients", tags=["patients"])


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new patient record.
    
    Ticket 1: If spouse_deceased = TRUE, auto-generates estate settlement tasks.
    """
    # Create patient with spouse death fields (Ticket 1)
    patient = Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        date_of_birth=patient_data.date_of_birth,
        ssn_last_four=patient_data.ssn_last_four,
        address=patient_data.address,
        city=patient_data.city,
        state=patient_data.state,
        zip_code=patient_data.zip_code,
        county=patient_data.county,
        phone=patient_data.phone,
        current_location=patient_data.current_location,
        diagnosis=patient_data.diagnosis,
        discharge_date=patient_data.discharge_date,
        care_level_needed=patient_data.care_level_needed,
        # Ticket 1: Spouse death fields
        spouse_deceased=patient_data.spouse_deceased,
        deceased_spouse_name=patient_data.deceased_spouse_name,
        spouse_date_of_death=patient_data.spouse_date_of_death,
        death_cert_status=patient_data.death_cert_status,
        marriage_date=patient_data.marriage_date,
        marriage_location=patient_data.marriage_location,
        deceased_was_veteran=patient_data.deceased_was_veteran,
    )
    db.add(patient)
    await db.flush()
    
    # Create care needs if provided
    if patient_data.care_needs:
        care_needs = CareNeeds(
            patient_id=patient.id,
            **patient_data.care_needs.model_dump(),
        )
        db.add(care_needs)
    
    # Create veteran status if provided
    if patient_data.veteran_status:
        veteran_status = VeteranStatus(
            patient_id=patient.id,
            **patient_data.veteran_status.model_dump(),
        )
        db.add(veteran_status)
    
    # Create financials if provided
    if patient_data.financials:
        financials = Financials(
            patient_id=patient.id,
            **patient_data.financials.model_dump(),
        )
        db.add(financials)
    
    # Create gifts if provided
    if patient_data.gifts:
        for gift_data in patient_data.gifts:
            gift = Gift(
                patient_id=patient.id,
                **gift_data.model_dump(),
            )
            db.add(gift)
    
    await db.commit()
    await db.refresh(patient)
    
    # Ticket 1: Auto-generate estate settlement tasks if spouse deceased
    if patient_data.spouse_deceased:
        await generate_estate_tasks(
            db=db,
            patient=patient,
            deceased_spouse_name=patient_data.deceased_spouse_name,
            deceased_was_veteran=patient_data.deceased_was_veteran,
        )
    
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a patient by ID."""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/", response_model=list[PatientResponse])
async def list_patients(
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all patients, optionally filtered by user."""
    query = select(Patient)
    if user_id:
        query = query.where(Patient.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{patient_id}/context")
async def get_patient_context(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get full patient context for agent processing."""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get related data
    care_needs_result = await db.execute(
        select(CareNeeds).where(CareNeeds.patient_id == patient_id)
    )
    care_needs = care_needs_result.scalar_one_or_none()
    
    veteran_result = await db.execute(
        select(VeteranStatus).where(VeteranStatus.patient_id == patient_id)
    )
    veteran_status = veteran_result.scalar_one_or_none()
    
    financials_result = await db.execute(
        select(Financials).where(Financials.patient_id == patient_id)
    )
    financials = financials_result.scalar_one_or_none()
    
    gifts_result = await db.execute(
        select(Gift).where(Gift.patient_id == patient_id)
    )
    gifts = gifts_result.scalars().all()
    
    # Build context dict
    context = {
        "patient_id": patient.id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "patient_age": _calculate_age(patient.date_of_birth),
        "zip_code": patient.zip_code,
        "county": patient.county,
        "current_location": patient.current_location,
        "diagnosis": patient.diagnosis,
        "discharge_date": str(patient.discharge_date) if patient.discharge_date else None,
        "care_level": patient.care_level_needed,
    }
    
    if financials:
        context["financials"] = {
            "social_security": financials.social_security,
            "pension": financials.pension,
            "va_pension": financials.va_pension,
            "other_income": financials.other_income,
            "checking": financials.checking,
            "savings": financials.savings,
            "cds": financials.cds,
            "money_market": financials.money_market,
            "ira": financials.ira,
            "four01k": financials.four01k,
            "brokerage": financials.brokerage,
            "annuities": financials.annuities,
            "stocks": financials.stocks,
            "bonds": financials.bonds,
            "owns_home": financials.owns_home,
            "home_value": financials.home_value,
            "home_mortgage": financials.home_mortgage,
            "intends_to_return": financials.intends_to_return,
            "vehicle_1_value": financials.vehicle_1_value,
            "vehicle_2_value": financials.vehicle_2_value,
            "life_insurance_face": financials.life_insurance_face,
            "life_insurance_cash": financials.life_insurance_cash,
            "credit_card_debt": financials.credit_card_debt,
            "medical_debt": financials.medical_debt,
            "other_debt": financials.other_debt,
        }
        context["total_income"] = (
            financials.social_security + financials.pension +
            financials.va_pension + financials.other_income
        )
    
    if veteran_status:
        context["veteran_status"] = {
            "is_veteran": veteran_status.is_veteran,
            "is_spouse_of_veteran": veteran_status.is_spouse_of_veteran,
            "veteran_deceased": veteran_status.veteran_deceased,
            "wartime_service": veteran_status.wartime_service,
        }
    
    if gifts:
        context["gifts"] = [
            {
                "gift_date": g.gift_date,
                "amount": g.amount,
                "recipient": g.recipient,
                "potentially_exempt": g.potentially_exempt,
            }
            for g in gifts
        ]
    
    return context


def _calculate_age(birth_date) -> int:
    """Calculate age from birth date."""
    from datetime import date
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
