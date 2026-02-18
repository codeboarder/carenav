"""
Wins/Accomplishments API router.
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from sqlalchemy import select
from ..models.database import get_async_session_maker, Win

router = APIRouter(prefix="/api/wins", tags=["wins"])


class WinSchema(BaseModel):
    id: int
    patient_id: int
    title: str
    description: Optional[str] = None
    amount: Optional[float] = None
    amount_type: Optional[str] = None  # one_time, monthly, saved
    win_date: Optional[date] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True


class WinCreate(BaseModel):
    title: str
    description: Optional[str] = None
    amount: Optional[float] = None
    amount_type: Optional[str] = None
    win_date: Optional[date] = None
    category: Optional[str] = None


@router.get("/{patient_id}", response_model=List[WinSchema])
async def get_wins(patient_id: int):
    """Get all wins for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        result = await session.execute(
            select(Win).where(Win.patient_id == patient_id).order_by(Win.win_date.desc())
        )
        wins = result.scalars().all()
        return [WinSchema.model_validate(w) for w in wins]


@router.post("/{patient_id}", response_model=WinSchema)
async def create_win(patient_id: int, data: WinCreate):
    """Add a win for a patient."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        win = Win(patient_id=patient_id, **data.model_dump())
        session.add(win)
        await session.commit()
        await session.refresh(win)
        return WinSchema.model_validate(win)
