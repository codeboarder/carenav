"""
Income phases API endpoints for CareNav Florida (Ticket 4).
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import IncomePhase, get_async_session_maker
from app.schemas import IncomePhaseCreate, IncomePhaseResponse

router = APIRouter(prefix="/income-phases", tags=["income-phases"])


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@router.post("/{patient_id}", response_model=IncomePhaseResponse)
async def create_income_phase(
    patient_id: int,
    phase_data: IncomePhaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new income phase for a patient."""
    phase = IncomePhase(
        patient_id=patient_id,
        phase_name=phase_data.phase_name,
        monthly_amount=phase_data.monthly_amount,
        source=phase_data.source,
        status=phase_data.status,
        estimated_start=phase_data.estimated_start,
        notes=phase_data.notes,
    )
    db.add(phase)
    await db.commit()
    await db.refresh(phase)
    return phase


@router.get("/{patient_id}", response_model=list[IncomePhaseResponse])
async def get_patient_income_phases(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all income phases for a patient."""
    query = select(IncomePhase).where(IncomePhase.patient_id == patient_id)
    query = query.order_by(IncomePhase.id)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{patient_id}/timeline")
async def get_income_timeline(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get income timeline for dashboard financial section."""
    query = select(IncomePhase).where(IncomePhase.patient_id == patient_id)
    result = await db.execute(query)
    phases = result.scalars().all()
    
    current_income = sum(float(p.monthly_amount) for p in phases if p.status == "current")
    projected_income = sum(float(p.monthly_amount) for p in phases if p.status in ["current", "submitted", "preparing"])
    future_income = sum(float(p.monthly_amount) for p in phases)
    
    return {
        "current_monthly": current_income,
        "projected_monthly": projected_income,
        "future_monthly": future_income,
        "phases": [
            {
                "id": p.id,
                "name": p.phase_name,
                "amount": float(p.monthly_amount),
                "source": p.source,
                "status": p.status,
                "estimated_start": p.estimated_start,
            }
            for p in phases
        ],
    }


@router.patch("/{phase_id}/status")
async def update_phase_status(
    phase_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
):
    """Update income phase status."""
    result = await db.execute(select(IncomePhase).where(IncomePhase.id == phase_id))
    phase = result.scalar_one_or_none()
    if not phase:
        raise HTTPException(status_code=404, detail="Income phase not found")
    
    phase.status = status
    await db.commit()
    return {"id": phase_id, "status": status}


@router.delete("/{phase_id}")
async def delete_income_phase(
    phase_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an income phase."""
    result = await db.execute(select(IncomePhase).where(IncomePhase.id == phase_id))
    phase = result.scalar_one_or_none()
    if not phase:
        raise HTTPException(status_code=404, detail="Income phase not found")
    
    await db.delete(phase)
    await db.commit()
    return {"deleted": True}
