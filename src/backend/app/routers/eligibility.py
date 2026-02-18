"""Eligibility API endpoints for CareNav Florida."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import Patient, Financials, VeteranStatus, Gift, get_async_session_maker
from app.schemas import (
    EligibilityRequest, EligibilityResponse,
    MedicaidResult, VAResult, GiftPenaltyResult
)
from app.agents.eligibility import EligibilityAgent

router = APIRouter(prefix="/eligibility", tags=["eligibility"])


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@router.post("/check", response_model=EligibilityResponse)
async def check_eligibility(
    request: EligibilityRequest,
    db: AsyncSession = Depends(get_db),
):
    """Check Medicaid and VA eligibility."""
    financials_dict = {}
    veteran_dict = {}
    gifts_list = []
    
    # Get data from patient if patient_id provided
    if request.patient_id:
        fin_result = await db.execute(
            select(Financials).where(Financials.patient_id == request.patient_id)
        )
        financials = fin_result.scalar_one_or_none()
        if financials:
            financials_dict = {
                "social_security": financials.social_security,
                "pension": financials.pension,
                "va_pension": financials.va_pension,
                "other_income": financials.other_income,
                "checking": financials.checking,
                "savings": financials.savings,
                "cds": financials.cds,
                "money_market": financials.money_market,
                "ira": financials.ira,
                "four01k": financials.four01k,
                "brokerage": financials.brokerage,
                "annuities": financials.annuities,
                "stocks": financials.stocks,
                "bonds": financials.bonds,
                "owns_home": financials.owns_home,
                "home_value": financials.home_value,
                "home_mortgage": financials.home_mortgage,
                "vehicle_1_value": financials.vehicle_1_value,
                "vehicle_2_value": financials.vehicle_2_value,
                "life_insurance_face": financials.life_insurance_face,
                "life_insurance_cash": financials.life_insurance_cash,
            }
        
        vet_result = await db.execute(
            select(VeteranStatus).where(VeteranStatus.patient_id == request.patient_id)
        )
        veteran = vet_result.scalar_one_or_none()
        if veteran:
            veteran_dict = {
                "is_veteran": veteran.is_veteran,
                "is_spouse_of_veteran": veteran.is_spouse_of_veteran,
                "veteran_deceased": veteran.veteran_deceased,
                "wartime_service": veteran.wartime_service,
            }
        
        gifts_result = await db.execute(
            select(Gift).where(Gift.patient_id == request.patient_id)
        )
        gifts = gifts_result.scalars().all()
        gifts_list = [
            {
                "gift_date": g.gift_date,
                "amount": g.amount,
                "potentially_exempt": g.potentially_exempt,
            }
            for g in gifts
        ]
    
    # Override with request data if provided
    if request.financials:
        financials_dict = request.financials.model_dump()
    if request.veteran_status:
        veteran_dict = request.veteran_status.model_dump()
    if request.gifts:
        gifts_list = [g.model_dump() for g in request.gifts]
    
    # Run eligibility checks
    medicaid = EligibilityAgent.check_medicaid_eligibility(financials_dict)
    va = EligibilityAgent.check_va_eligibility(veteran_dict, financials_dict)
    penalty = EligibilityAgent.calculate_gift_penalty(gifts_list)
    
    return EligibilityResponse(
        medicaid=MedicaidResult(**medicaid),
        va_aa=VAResult(**va),
        gift_penalty=GiftPenaltyResult(**penalty),
        confidence=85,
    )


@router.get("/spend-down/{amount}")
async def get_spend_down_options(amount: float):
    """Get legal spend-down options for a given amount."""
    from app.agents.legal import LegalAgent
    
    options = LegalAgent.get_spend_down_options(amount)
    return {
        "amount_to_spend": amount,
        "options": options,
        "total_covered": sum(o["amount"] for o in options),
        "warning": "Do NOT give money to family members or pay deceased spouse's individual debts.",
    }


@router.post("/debt-check")
async def check_debt_payment(
    debt_type: str,
    debt_holder: str,
    joint_account: bool = False,
):
    """Check if a debt should be paid."""
    from app.agents.legal import LegalAgent
    
    result = LegalAgent.evaluate_debt_payment(debt_type, debt_holder, joint_account)
    return result
