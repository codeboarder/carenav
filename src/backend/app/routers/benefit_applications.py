"""Benefit application pipeline API endpoints for CareNav Florida (Ticket 5)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.models.database import BenefitApplication, get_async_session_maker
from app.schemas import BenefitApplicationCreate, BenefitApplicationResponse, BenefitApplicationUpdate

router = APIRouter(prefix="/benefit-applications", tags=["benefit-applications"])


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@router.post("/{patient_id}", response_model=BenefitApplicationResponse)
async def create_benefit_application(
    patient_id: int,
    app_data: BenefitApplicationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new benefit application for a patient."""
    application = BenefitApplication(
        patient_id=patient_id,
        benefit_type=app_data.benefit_type,
        display_name=app_data.display_name,
        monthly_amount=app_data.monthly_amount,
        status=app_data.status,
        expected_weeks=app_data.expected_weeks,
        missing_documents=app_data.missing_documents,
        contact_phone=app_data.contact_phone,
        notes=app_data.notes,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


@router.get("/{patient_id}", response_model=list[BenefitApplicationResponse])
async def get_patient_benefit_applications(
    patient_id: int,
    status: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all benefit applications for a patient."""
    query = select(BenefitApplication).where(BenefitApplication.patient_id == patient_id)
    if status:
        query = query.where(BenefitApplication.status == status)
    query = query.order_by(BenefitApplication.id)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{patient_id}/pipeline")
async def get_benefit_pipeline(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get benefit application pipeline for Programs view."""
    query = select(BenefitApplication).where(BenefitApplication.patient_id == patient_id)
    result = await db.execute(query)
    applications = result.scalars().all()
    
    pipeline = {
        "researching": [],
        "preparing": [],
        "submitted": [],
        "processing": [],
        "approved": [],
        "denied": [],
    }
    
    total_approved = 0
    total_pending = 0
    
    for app in applications:
        status = app.status or "researching"
        if status in pipeline:
            pipeline[status].append({
                "id": app.id,
                "benefit_type": app.benefit_type,
                "display_name": app.display_name,
                "monthly_amount": float(app.monthly_amount) if app.monthly_amount else 0,
                "submitted_date": app.submitted_date.isoformat() if app.submitted_date else None,
                "expected_weeks": app.expected_weeks,
                "missing_documents": app.missing_documents,
                "contact_phone": app.contact_phone,
            })
        
        if status == "approved" and app.monthly_amount:
            total_approved += float(app.monthly_amount)
        elif status in ["submitted", "processing"] and app.monthly_amount:
            total_pending += float(app.monthly_amount)
    
    return {
        "pipeline": pipeline,
        "total_approved_monthly": total_approved,
        "total_pending_monthly": total_pending,
        "total_applications": len(applications),
    }


@router.patch("/{application_id}")
async def update_benefit_application(
    application_id: int,
    update_data: BenefitApplicationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update benefit application status or details."""
    result = await db.execute(select(BenefitApplication).where(BenefitApplication.id == application_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Benefit application not found")
    
    if update_data.status is not None:
        application.status = update_data.status
    if update_data.submitted_date is not None:
        application.submitted_date = update_data.submitted_date
    if update_data.missing_documents is not None:
        application.missing_documents = update_data.missing_documents
    if update_data.notes is not None:
        application.notes = update_data.notes
    
    await db.commit()
    return {"id": application_id, "status": application.status}


@router.delete("/{application_id}")
async def delete_benefit_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a benefit application."""
    result = await db.execute(select(BenefitApplication).where(BenefitApplication.id == application_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Benefit application not found")
    
    await db.delete(application)
    await db.commit()
    return {"deleted": True}
