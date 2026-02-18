"""Medical information API router."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from sqlalchemy import select
from ..models.database import get_async_session_maker, MedicalInfo, Diagnosis, Medication

router = APIRouter(prefix="/api/medical", tags=["medical"])


class MedicalInfoSchema(BaseModel):
    id: int
    patient_id: int
    medicare_id: Optional[str] = None
    medicaid_id: Optional[str] = None
    physician_name: Optional[str] = None
    physician_phone: Optional[str] = None
    blood_pressure: Optional[str] = None
    pulse: Optional[int] = None
    temperature: Optional[float] = None
    respiration: Optional[int] = None
    vitals_date: Optional[date] = None
    allergies: Optional[str] = None
    diet: Optional[str] = None
    code_status: Optional[str] = None

    class Config:
        from_attributes = True


class DiagnosisSchema(BaseModel):
    id: int
    patient_id: int
    name: str
    icd_code: Optional[str] = None
    diagnosis_date: Optional[date] = None
    is_primary: bool = False
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class MedicationSchema(BaseModel):
    id: int
    patient_id: int
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    purpose: Optional[str] = None
    prescriber: Optional[str] = None
    start_date: Optional[date] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class MedicalInfoCreate(BaseModel):
    medicare_id: Optional[str] = None
    medicaid_id: Optional[str] = None
    physician_name: Optional[str] = None
    physician_phone: Optional[str] = None
    blood_pressure: Optional[str] = None
    pulse: Optional[int] = None
    temperature: Optional[float] = None
    respiration: Optional[int] = None
    vitals_date: Optional[date] = None
    allergies: Optional[str] = None
    diet: Optional[str] = None
    code_status: Optional[str] = None


class DiagnosisCreate(BaseModel):
    name: str
    icd_code: Optional[str] = None
    diagnosis_date: Optional[date] = None
    is_primary: bool = False
    notes: Optional[str] = None


class MedicationCreate(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    purpose: Optional[str] = None
    prescriber: Optional[str] = None
    start_date: Optional[date] = None
    notes: Optional[str] = None


class FullMedicalResponse(BaseModel):
    info: Optional[MedicalInfoSchema] = None
    diagnoses: List[DiagnosisSchema] = []
    medications: List[MedicationSchema] = []


@router.get("/{patient_id}", response_model=FullMedicalResponse)
async def get_medical_info(patient_id: int):
    """Get all medical info for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        # Get medical info
        result = await session.execute(
            select(MedicalInfo).where(MedicalInfo.patient_id == patient_id)
        )
        info = result.scalar_one_or_none()
        
        # Get diagnoses
        result = await session.execute(
            select(Diagnosis).where(Diagnosis.patient_id == patient_id).order_by(Diagnosis.is_primary.desc())
        )
        diagnoses = result.scalars().all()
        
        # Get medications
        result = await session.execute(
            select(Medication).where(Medication.patient_id == patient_id).order_by(Medication.name)
        )
        medications = result.scalars().all()
        
        return FullMedicalResponse(
            info=MedicalInfoSchema.model_validate(info) if info else None,
            diagnoses=[DiagnosisSchema.model_validate(d) for d in diagnoses],
            medications=[MedicationSchema.model_validate(m) for m in medications]
        )


@router.post("/{patient_id}/info", response_model=MedicalInfoSchema)
async def create_medical_info(patient_id: int, data: MedicalInfoCreate):
    """Create or update medical info for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        # Check if exists
        result = await session.execute(
            select(MedicalInfo).where(MedicalInfo.patient_id == patient_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(existing, key, value)
            await session.commit()
            await session.refresh(existing)
            return MedicalInfoSchema.model_validate(existing)
        else:
            # Create
            info = MedicalInfo(patient_id=patient_id, **data.model_dump())
            session.add(info)
            await session.commit()
            await session.refresh(info)
            return MedicalInfoSchema.model_validate(info)


@router.post("/{patient_id}/diagnoses", response_model=DiagnosisSchema)
async def create_diagnosis(patient_id: int, data: DiagnosisCreate):
    """Add a diagnosis for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        diagnosis = Diagnosis(patient_id=patient_id, **data.model_dump())
        session.add(diagnosis)
        await session.commit()
        await session.refresh(diagnosis)
        return DiagnosisSchema.model_validate(diagnosis)


@router.post("/{patient_id}/medications", response_model=MedicationSchema)
async def create_medication(patient_id: int, data: MedicationCreate):
    """Add a medication for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        medication = Medication(patient_id=patient_id, **data.model_dump())
        session.add(medication)
        await session.commit()
        await session.refresh(medication)
        return MedicationSchema.model_validate(medication)
