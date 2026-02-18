"""Selected Facility API router."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from sqlalchemy import select
from ..models.database import get_async_session_maker, SelectedFacility

router = APIRouter(prefix="/api/selected-facility", tags=["selected_facility"])


class SelectedFacilitySchema(BaseModel):
    id: int
    patient_id: int
    name: str
    address: Optional[str] = None
    apt_number: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    admissions_contact: Optional[str] = None
    community_rep: Optional[str] = None
    keys_date: Optional[datetime] = None
    move_in_date: Optional[date] = None
    base_rent: Optional[float] = None
    vet_discount_pct: Optional[float] = None
    care_level: Optional[str] = None
    care_level_cost: Optional[float] = None
    total_monthly: Optional[float] = None
    deposit_amount: Optional[float] = None
    deposit_paid: bool = False
    community_fee: Optional[float] = None
    status: str = "selected"
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class SelectedFacilityCreate(BaseModel):
    name: str
    address: Optional[str] = None
    apt_number: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    admissions_contact: Optional[str] = None
    community_rep: Optional[str] = None
    keys_date: Optional[datetime] = None
    move_in_date: Optional[date] = None
    base_rent: Optional[float] = None
    vet_discount_pct: Optional[float] = None
    care_level: Optional[str] = None
    care_level_cost: Optional[float] = None
    total_monthly: Optional[float] = None
    deposit_amount: Optional[float] = None
    deposit_paid: bool = False
    community_fee: Optional[float] = None
    status: str = "selected"
    notes: Optional[str] = None


@router.get("/{patient_id}", response_model=Optional[SelectedFacilitySchema])
async def get_selected_facility(patient_id: int):
    """Get the selected facility for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        result = await session.execute(
            select(SelectedFacility).where(SelectedFacility.patient_id == patient_id)
        )
        facility = result.scalar_one_or_none()
        if facility:
            return SelectedFacilitySchema.model_validate(facility)
        return None


@router.post("/{patient_id}", response_model=SelectedFacilitySchema)
async def create_selected_facility(patient_id: int, data: SelectedFacilityCreate):
    """Create or update the selected facility for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        # Check if exists
        result = await session.execute(
            select(SelectedFacility).where(SelectedFacility.patient_id == patient_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(existing, key, value)
            await session.commit()
            await session.refresh(existing)
            return SelectedFacilitySchema.model_validate(existing)
        else:
            # Create
            facility = SelectedFacility(patient_id=patient_id, **data.model_dump())
            session.add(facility)
            await session.commit()
            await session.refresh(facility)
            return SelectedFacilitySchema.model_validate(facility)
