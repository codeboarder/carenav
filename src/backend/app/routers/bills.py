"""
Bill tracking API endpoints for CareNav Florida (Ticket 3).
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.models.database import Bill, get_async_session_maker
from app.schemas import BillCreate, BillResponse, BillUpdate

router = APIRouter(prefix="/bills", tags=["bills"])


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@router.post("/{patient_id}", response_model=BillResponse)
async def create_bill(
    patient_id: int,
    bill_data: BillCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new bill for a patient."""
    bill = Bill(
        patient_id=patient_id,
        vendor=bill_data.vendor,
        amount=bill_data.amount,
        due_date=bill_data.due_date,
        category=bill_data.category,
        contact_name=bill_data.contact_name,
        contact_phone=bill_data.contact_phone,
        payment_link=bill_data.payment_link,
        recurring=bill_data.recurring,
        notes=bill_data.notes,
    )
    db.add(bill)
    await db.commit()
    await db.refresh(bill)
    return bill


@router.get("/{patient_id}", response_model=list[BillResponse])
async def get_patient_bills(
    patient_id: int,
    status: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all bills for a patient."""
    query = select(Bill).where(Bill.patient_id == patient_id)
    if status:
        query = query.where(Bill.status == status)
    query = query.order_by(Bill.due_date)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{patient_id}/summary")
async def get_bills_summary(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get bills summary for dashboard card."""
    query = select(Bill).where(Bill.patient_id == patient_id)
    result = await db.execute(query)
    bills = result.scalars().all()
    
    total_due = sum(float(b.amount) - float(b.amount_paid or 0) for b in bills if b.status != "paid")
    overdue_count = sum(1 for b in bills if b.due_date and b.due_date < date.today() and b.status != "paid")
    next_due = min((b.due_date for b in bills if b.due_date and b.status != "paid"), default=None)
    
    return {
        "total_due": total_due,
        "overdue_count": overdue_count,
        "next_due_date": next_due,
        "total_bills": len(bills),
    }


@router.patch("/{bill_id}")
async def update_bill(
    bill_id: int,
    update_data: BillUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update bill status or payment."""
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    if update_data.status is not None:
        bill.status = update_data.status
    if update_data.amount_paid is not None:
        bill.amount_paid = update_data.amount_paid
        if bill.amount_paid >= bill.amount:
            bill.status = "paid"
        elif bill.amount_paid > 0:
            bill.status = "partial"
    if update_data.notes is not None:
        bill.notes = update_data.notes
    
    await db.commit()
    return {"id": bill_id, "status": bill.status, "amount_paid": float(bill.amount_paid or 0)}


@router.delete("/{bill_id}")
async def delete_bill(
    bill_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a bill."""
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    await db.delete(bill)
    await db.commit()
    return {"deleted": True}
