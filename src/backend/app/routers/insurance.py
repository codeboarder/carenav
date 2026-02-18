"""Insurance API router."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from sqlalchemy import select
from ..models.database import get_async_session_maker, Insurance

router = APIRouter(prefix="/api/insurance", tags=["insurance"])


class InsuranceSchema(BaseModel):
    id: int
    patient_id: int
    insurance_type: Optional[str] = None
    carrier: Optional[str] = None
    policy_number: Optional[str] = None
    group_number: Optional[str] = None
    subscriber_name: Optional[str] = None
    subscriber_id: Optional[str] = None
    effective_date: Optional[date] = None
    termination_date: Optional[date] = None
    phone: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class InsuranceCreate(BaseModel):
    insurance_type: Optional[str] = None
    carrier: Optional[str] = None
    policy_number: Optional[str] = None
    group_number: Optional[str] = None
    subscriber_name: Optional[str] = None
    subscriber_id: Optional[str] = None
    effective_date: Optional[date] = None
    termination_date: Optional[date] = None
    phone: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None


@router.get("/{patient_id}", response_model=List[InsuranceSchema])
async def get_insurance(patient_id: int):
    """Get all insurance policies for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        result = await session.execute(
            select(Insurance).where(Insurance.patient_id == patient_id).order_by(Insurance.insurance_type)
        )
        policies = result.scalars().all()
        return [InsuranceSchema.model_validate(p) for p in policies]


@router.post("/{patient_id}", response_model=InsuranceSchema)
async def create_insurance(patient_id: int, data: InsuranceCreate):
    """Add an insurance policy for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        policy = Insurance(patient_id=patient_id, **data.model_dump())
        session.add(policy)
        await session.commit()
        await session.refresh(policy)
        return InsuranceSchema.model_validate(policy)
