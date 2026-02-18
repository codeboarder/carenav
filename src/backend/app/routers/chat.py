"""Chat API endpoints for CareNav Florida."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import Patient, Conversation, get_async_session_maker
from app.schemas import ChatRequest, ChatResponse, ActionItem
from app.agents.orchestrator import OrchestratorAgent
from app.routers.patients import get_patient_context

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize orchestrator
orchestrator = OrchestratorAgent()


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Process a chat message through the multi-agent system."""
    patient_context = None
    
    # Get patient context if patient_id provided
    if request.patient_id:
        result = await db.execute(
            select(Patient).where(Patient.id == request.patient_id)
        )
        patient = result.scalar_one_or_none()
        if patient:
            from app.routers.patients import get_patient_context as get_ctx
            patient_context = await get_ctx(request.patient_id, db)
    
    # Convert conversation history to list of dicts
    history = None
    if request.conversation_history:
        history = [{"role": m.role, "content": m.content} for m in request.conversation_history]
    
    # Process through orchestrator
    try:
        result = await orchestrator.process_message(
            user_message=request.message,
            patient_context=patient_context,
            conversation_history=history,
        )
    except Exception as e:
        # Fallback response if agent fails
        return ChatResponse(
            message=f"I encountered an issue processing your request. Please try again or rephrase your question. Error: {str(e)}",
            action_items=[],
            warnings=["Agent processing failed - using fallback response"],
            confidence=0,
        )
    
    # Save conversation to database
    conversation = Conversation(
        patient_id=request.patient_id,
        role="user",
        content=request.message,
    )
    db.add(conversation)
    
    assistant_conversation = Conversation(
        patient_id=request.patient_id,
        role="assistant",
        content=result.get("message", ""),
    )
    db.add(assistant_conversation)
    await db.commit()
    
    # Format action items
    action_items = [
        ActionItem(
            action=item.get("action", ""),
            priority=item.get("priority", "medium"),
            phone=item.get("phone"),
            deadline=item.get("deadline"),
        )
        for item in result.get("action_items", [])
    ]
    
    return ChatResponse(
        message=result.get("message", ""),
        action_items=action_items,
        warnings=result.get("warnings", []),
        confidence=result.get("confidence", 75),
    )


@router.get("/history/{patient_id}")
async def get_chat_history(
    patient_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get chat history for a patient."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.patient_id == patient_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    conversations = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "role": c.role,
            "content": c.content,
            "created_at": c.created_at,
        }
        for c in reversed(conversations)
    ]
