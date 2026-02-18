"""
Contact directory API endpoints for CareNav Florida (Ticket 6).
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import Contact, get_async_session_maker
from app.schemas import ContactCreate, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@router.post("/{patient_id}", response_model=ContactResponse)
async def create_contact(
    patient_id: int,
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new contact for a patient."""
    contact = Contact(
        patient_id=patient_id,
        name=contact_data.name,
        organization=contact_data.organization,
        role=contact_data.role,
        phone=contact_data.phone,
        email=contact_data.email,
        category=contact_data.category,
        notes=contact_data.notes,
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.get("/{patient_id}", response_model=list[ContactResponse])
async def get_patient_contacts(
    patient_id: int,
    category: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all contacts for a patient."""
    query = select(Contact).where(Contact.patient_id == patient_id)
    if category:
        query = query.where(Contact.category == category)
    query = query.order_by(Contact.category, Contact.name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{patient_id}/grouped")
async def get_contacts_grouped(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get contacts grouped by category for directory view."""
    query = select(Contact).where(Contact.patient_id == patient_id)
    query = query.order_by(Contact.category, Contact.name)
    result = await db.execute(query)
    contacts = result.scalars().all()
    
    grouped = {}
    for contact in contacts:
        category = contact.category or "other"
        if category not in grouped:
            grouped[category] = []
        grouped[category].append({
            "id": contact.id,
            "name": contact.name,
            "organization": contact.organization,
            "role": contact.role,
            "phone": contact.phone,
            "email": contact.email,
            "notes": contact.notes,
        })
    
    return {
        "grouped": grouped,
        "total_contacts": len(contacts),
    }


@router.patch("/{contact_id}")
async def update_contact(
    contact_id: int,
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
):
    """Update a contact."""
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.name = contact_data.name
    contact.organization = contact_data.organization
    contact.role = contact_data.role
    contact.phone = contact_data.phone
    contact.email = contact_data.email
    contact.category = contact_data.category
    contact.notes = contact_data.notes
    
    await db.commit()
    return {"id": contact_id, "name": contact.name}


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a contact."""
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    await db.delete(contact)
    await db.commit()
    return {"deleted": True}
