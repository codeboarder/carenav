"""
Facility API endpoints for CareNav Florida.
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import Facility, FacilityMatch, get_async_session_maker
from app.schemas import (
    FacilitySearchRequest, FacilitySearchResponse, FacilityResult, AffordabilityInfo
)
from app.agents.facility import FacilityAgent

router = APIRouter(prefix="/facilities", tags=["facilities"])


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@router.post("/search", response_model=FacilitySearchResponse)
async def search_facilities(request: FacilitySearchRequest):
    """Search for facilities matching criteria."""
    # Get sample facilities (in production, this would query real data)
    facilities = FacilityAgent.get_sample_facilities(
        zip_code=request.zip_code,
        care_level=request.care_level,
    )
    
    # Filter by Medicaid if required
    if request.medicaid_required:
        facilities = [f for f in facilities if f.get("accepts_medicaid")]
    
    # Score and enrich facilities
    results = []
    for facility in facilities:
        score = FacilityAgent.calculate_match_score(
            facility=facility,
            patient_income=request.patient_income,
            care_level=request.care_level,
            medicaid_required=request.medicaid_required,
            va_benefit=request.va_benefit,
        )
        
        affordability = FacilityAgent.calculate_affordability(
            facility_rate=facility.get("rate_low", 0),
            patient_income=request.patient_income,
            va_benefit=request.va_benefit,
        )
        
        results.append(FacilityResult(
            name=facility.get("name", ""),
            address=facility.get("address", ""),
            phone=facility.get("phone", ""),
            license_type=facility.get("license_type", "ALF"),
            capacity=facility.get("capacity", 0),
            beds_available=facility.get("beds_available"),
            rate_low=facility.get("rate_low", 0),
            rate_high=facility.get("rate_high", 0),
            accepts_medicaid=facility.get("accepts_medicaid", False),
            medicaid_day_one=facility.get("medicaid_day_one", False),
            memory_care=facility.get("memory_care", False),
            rating=facility.get("rating", 0),
            distance_miles=facility.get("distance_miles", 0),
            match_score=score,
            affordability=AffordabilityInfo(**affordability),
        ))
    
    # Sort by match score
    results.sort(key=lambda x: x.match_score, reverse=True)
    
    return FacilitySearchResponse(
        facilities=results,
        search_criteria={
            "zip_code": request.zip_code,
            "care_level": request.care_level,
            "radius_miles": request.radius_miles,
            "medicaid_required": request.medicaid_required,
        },
        total_found=len(results),
    )


@router.get("/{facility_id}")
async def get_facility(
    facility_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get facility details by ID."""
    result = await db.execute(select(Facility).where(Facility.id == facility_id))
    facility = result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility


@router.post("/match/{patient_id}/{facility_id}")
async def save_facility_match(
    patient_id: int,
    facility_id: int,
    match_score: int,
    notes: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Save a facility match for a patient."""
    match = FacilityMatch(
        patient_id=patient_id,
        facility_id=facility_id,
        match_score=match_score,
        notes=notes,
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return {"id": match.id, "status": "saved"}


@router.get("/matches/{patient_id}")
async def get_patient_matches(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all facility matches for a patient."""
    result = await db.execute(
        select(FacilityMatch)
        .where(FacilityMatch.patient_id == patient_id)
        .order_by(FacilityMatch.match_score.desc())
    )
    matches = result.scalars().all()
    return [
        {
            "id": m.id,
            "facility_id": m.facility_id,
            "match_score": m.match_score,
            "status": m.status,
            "notes": m.notes,
            "created_at": m.created_at,
        }
        for m in matches
    ]
