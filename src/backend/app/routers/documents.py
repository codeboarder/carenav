"""Documents API router for CareNav Florida."""
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.models.database import (
    Document, get_async_session_maker, MedicalInfo, Diagnosis, Medication,
    Insurance, Contact, Bill, Asset, SelectedFacility, Win
)
from app.services.llm_service import get_llm_provider

router = APIRouter(prefix="/api/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    id: int
    patient_id: int
    name: str
    category: Optional[str] = None
    doc_type: Optional[str] = None
    status: str
    content: Optional[str] = None
    extracted_data: Optional[dict] = None
    ai_analysis: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    patient_id: int
    name: str
    category: Optional[str] = None
    doc_type: Optional[str] = None
    content: Optional[str] = None
    extracted_data: Optional[dict] = None
    ai_analysis: Optional[str] = None


@router.get("/{patient_id}/")
async def get_patient_documents(patient_id: int) -> list[DocumentResponse]:
    """Get all documents for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        result = await session.execute(
            select(Document).where(Document.patient_id == patient_id)
        )
        documents = result.scalars().all()
        return [DocumentResponse.model_validate(doc) for doc in documents]


@router.post("/")
async def create_document(doc: DocumentCreate) -> DocumentResponse:
    """Create a new document."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        new_doc = Document(
            patient_id=doc.patient_id,
            name=doc.name,
            category=doc.category,
            doc_type=doc.doc_type,
            content=doc.content,
            extracted_data=doc.extracted_data,
            ai_analysis=doc.ai_analysis,
            status="generated",
            uploaded_at=datetime.utcnow(),
        )
        session.add(new_doc)
        await session.commit()
        await session.refresh(new_doc)
        return DocumentResponse.model_validate(new_doc)


@router.delete("/{doc_id}/")
async def delete_document(doc_id: int):
    """Delete a document."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        result = await session.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        await session.delete(doc)
        await session.commit()
        return {"status": "deleted"}


@router.post("/{patient_id}/generate-demo/")
async def generate_demo_documents(patient_id: int):
    """Generate comprehensive demo documents for a patient."""
    from app.services.demo_documents import create_demo_documents_for_patient
    result = await create_demo_documents_for_patient(patient_id)
    return result


class DocumentParseRequest(BaseModel):
    patient_id: int
    content: str
    document_type: Optional[str] = None  # e.g., "medical", "insurance", "contact", "bill", "facility"


class ParsedDataResponse(BaseModel):
    success: bool
    document_type: str
    extracted_data: dict
    records_created: list[str]
    unstructured_data: Optional[dict] = None


@router.post("/parse/")
async def parse_and_store_document(request: DocumentParseRequest) -> ParsedDataResponse:
    """
    Parse document content using AI and store extracted data in appropriate tables.
    If no matching table exists, store as unstructured JSON in the document.
    """
    llm = get_llm_provider()
    
    # AI prompt to extract structured data
    parse_prompt = f"""Analyze this document and extract structured data. Identify the document type and extract relevant fields.

Document content:
{request.content}

Respond with JSON in this exact format:
{{
    "document_type": "medical|insurance|contact|bill|facility|task|win|other",
    "confidence": 0.0-1.0,
    "extracted_fields": {{
        // Fields depend on document_type:
        // medical: diagnoses (list), medications (list), vitals, allergies, physician_name, physician_phone
        // insurance: carrier, policy_number, group_number, insurance_type, phone, effective_date
        // contact: name, relationship, phone, email, address, is_emergency
        // bill: payee, amount, due_date, category, status
        // facility: name, address, phone, monthly_cost, care_level
        // task: title, description, priority, due_date, category
        // win: title, description, amount, category, win_date
        // other: any relevant key-value pairs
    }}
}}

Only respond with valid JSON, no other text."""

    try:
        response = await llm.chat_completion([
            {"role": "system", "content": "You are a document parsing assistant. Extract structured data from documents and return valid JSON only."},
            {"role": "user", "content": parse_prompt}
        ])
        
        # Parse AI response - response is a dict with 'content' key
        response_text = response["content"].strip()
        # Clean up response if it has markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        parsed = json.loads(response_text)
        
        doc_type = parsed.get("document_type", "other")
        extracted = parsed.get("extracted_fields", {})
        records_created = []
        unstructured_data = None
        
        session_maker = get_async_session_maker()
        async with session_maker() as session:
            # Store data based on document type
            if doc_type == "medical":
                # Store diagnoses
                for diag in extracted.get("diagnoses", []):
                    new_diag = Diagnosis(
                        patient_id=request.patient_id,
                        name=diag.get("name", "Unknown"),
                        icd_code=diag.get("icd_code"),
                        is_primary=diag.get("is_primary", False)
                    )
                    session.add(new_diag)
                    records_created.append(f"Diagnosis: {diag.get('name')}")
                
                # Store medications
                for med in extracted.get("medications", []):
                    new_med = Medication(
                        patient_id=request.patient_id,
                        name=med.get("name", "Unknown"),
                        dosage=med.get("dosage"),
                        frequency=med.get("frequency"),
                        purpose=med.get("purpose")
                    )
                    session.add(new_med)
                    records_created.append(f"Medication: {med.get('name')}")
                    
            elif doc_type == "insurance":
                new_insurance = Insurance(
                    patient_id=request.patient_id,
                    carrier=extracted.get("carrier"),
                    policy_number=extracted.get("policy_number"),
                    group_number=extracted.get("group_number"),
                    insurance_type=extracted.get("insurance_type"),
                    phone=extracted.get("phone"),
                    effective_date=extracted.get("effective_date"),
                    status="active"
                )
                session.add(new_insurance)
                records_created.append(f"Insurance: {extracted.get('carrier')}")
                
            elif doc_type == "contact":
                new_contact = Contact(
                    patient_id=request.patient_id,
                    name=extracted.get("name", "Unknown"),
                    relationship=extracted.get("relationship"),
                    phone=extracted.get("phone"),
                    email=extracted.get("email"),
                    address=extracted.get("address"),
                    is_emergency=extracted.get("is_emergency", False)
                )
                session.add(new_contact)
                records_created.append(f"Contact: {extracted.get('name')}")
                
            elif doc_type == "bill":
                new_bill = Bill(
                    patient_id=request.patient_id,
                    payee=extracted.get("payee", "Unknown"),
                    amount=extracted.get("amount", 0),
                    due_date=extracted.get("due_date"),
                    category=extracted.get("category"),
                    status=extracted.get("status", "pending")
                )
                session.add(new_bill)
                records_created.append(f"Bill: {extracted.get('payee')}")
                
            elif doc_type == "win":
                new_win = Win(
                    patient_id=request.patient_id,
                    title=extracted.get("title", "Accomplishment"),
                    description=extracted.get("description"),
                    amount=extracted.get("amount"),
                    category=extracted.get("category"),
                    win_date=extracted.get("win_date")
                )
                session.add(new_win)
                records_created.append(f"Win: {extracted.get('title')}")
                
            else:
                # Store as unstructured JSON in a document
                unstructured_data = extracted
                new_doc = Document(
                    patient_id=request.patient_id,
                    name=f"Parsed Document - {doc_type}",
                    category=doc_type,
                    content=request.content,
                    extracted_data=extracted,
                    status="parsed",
                    uploaded_at=datetime.utcnow()
                )
                session.add(new_doc)
                records_created.append(f"Document: {doc_type} (unstructured)")
            
            await session.commit()
        
        return ParsedDataResponse(
            success=True,
            document_type=doc_type,
            extracted_data=extracted,
            records_created=records_created,
            unstructured_data=unstructured_data
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document parsing failed: {str(e)}")
