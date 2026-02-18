"""
Task API endpoints for CareNav Florida (Ticket 2: Dependencies + Assignees).
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.models.database import Task, get_async_session_maker
from app.schemas import TaskCreate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Ticket 2: Task dependency sequence rules (Legal Agent hardcoded rules)
TASK_SEQUENCE_RULES = {
    "ssa_death_report": ["bank_branch_visit"],  # Bank branch BEFORE SSA death report
    "sell_asset": ["receive_title"],  # Receive title BEFORE sell asset
    "cancel_vehicle_insurance": ["sell_vehicle"],  # Sell vehicle BEFORE cancel vehicle insurance
    "asset_transfer": ["consult_attorney"],  # Consult attorney BEFORE asset transfers
}


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


def check_task_blocked(task: Task, all_tasks: list[Task]) -> bool:
    """Check if a task is blocked by an incomplete dependency."""
    if task.blocked_by_id:
        blocking_task = next((t for t in all_tasks if t.id == task.blocked_by_id), None)
        if blocking_task and blocking_task.status != "completed":
            return True
    return False


@router.post("/{patient_id}", response_model=TaskResponse)
async def create_task(
    patient_id: int,
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new task for a patient."""
    task = Task(
        patient_id=patient_id,
        title=task_data.title,
        description=task_data.description,
        category=task_data.category,
        priority=task_data.priority,
        due_date=task_data.due_date,
        phone=task_data.phone,
        phone_name=task_data.phone_name,
        assignee=task_data.assignee,
        blocked_by_id=task_data.blocked_by_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/{patient_id}", response_model=list[TaskResponse])
async def get_patient_tasks(
    patient_id: int,
    status: str = None,
    assignee: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all tasks for a patient."""
    query = select(Task).where(Task.patient_id == patient_id)
    if status:
        query = query.where(Task.status == status)
    if assignee:
        query = query.where(Task.assignee == assignee)
    query = query.order_by(Task.priority.desc(), Task.due_date)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Check blocked status for each task
    for task in tasks:
        if check_task_blocked(task, tasks) and task.status == "pending":
            task.status = "blocked"
    
    return tasks


@router.get("/{patient_id}/with-dependencies")
async def get_tasks_with_dependencies(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all tasks with dependency information for UI."""
    query = select(Task).where(Task.patient_id == patient_id)
    query = query.order_by(Task.priority.desc(), Task.due_date)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    task_list = []
    for task in tasks:
        is_blocked = check_task_blocked(task, tasks)
        blocking_task_title = None
        if task.blocked_by_id:
            blocking_task = next((t for t in tasks if t.id == task.blocked_by_id), None)
            if blocking_task:
                blocking_task_title = blocking_task.title
        
        task_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "category": task.category,
            "priority": task.priority,
            "status": "blocked" if is_blocked and task.status == "pending" else task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "phone": task.phone,
            "phone_name": task.phone_name,
            "assignee": task.assignee,
            "blocked_by_id": task.blocked_by_id,
            "blocked_by_title": blocking_task_title,
            "is_blocked": is_blocked,
            "completed_date": task.completed_date.isoformat() if task.completed_date else None,
        })
    
    return {"tasks": task_list, "total": len(task_list)}


@router.patch("/{task_id}/status")
async def update_task_status(
    task_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
):
    """Update task status."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if task is blocked
    if status == "in_progress" or status == "completed":
        all_tasks_result = await db.execute(select(Task).where(Task.patient_id == task.patient_id))
        all_tasks = all_tasks_result.scalars().all()
        if check_task_blocked(task, all_tasks):
            raise HTTPException(status_code=400, detail="Task is blocked by an incomplete dependency")
    
    task.status = status
    if status == "completed":
        task.completed_date = date.today()
    
    await db.commit()
    return {"id": task_id, "status": status, "completed_date": task.completed_date}


@router.patch("/{task_id}/note")
async def update_task_note(
    task_id: int,
    note_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update task note (for RAG context)."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.notes = note_data.get("note", "")
    await db.commit()
    return {"id": task_id, "notes": task.notes}


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
    return {"deleted": True}
