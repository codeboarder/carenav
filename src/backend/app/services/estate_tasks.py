"""Estate task auto-generation service for CareNav Florida (Ticket 1).

When spouse_deceased = TRUE during intake, this service auto-generates
the standard estate settlement tasks with proper dependencies.
"""
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Task, Patient


# Estate settlement task templates with dependencies
ESTATE_TASKS = [
    {
        "title": "Visit bank branch with death certificate",
        "description": "Bring original death certificate to bank. Update account ownership or close joint accounts. Get certified copies of statements.",
        "category": "estate",
        "priority": "high",
        "assignee": "primary",
        "phone_name": "Bank Customer Service",
        "task_key": "bank_branch_visit",
        "days_offset": 7,
        "blocked_by_key": None,
    },
    {
        "title": "Report death to Social Security Administration",
        "description": "Call SSA to report death. Apply for survivor benefits if eligible. IMPORTANT: Must complete bank visit first to avoid frozen accounts.",
        "category": "estate",
        "priority": "high",
        "assignee": "primary",
        "phone": "1-800-772-1213",
        "phone_name": "Social Security Administration",
        "task_key": "ssa_death_report",
        "days_offset": 14,
        "blocked_by_key": "bank_branch_visit",  # Bank BEFORE SSA
    },
    {
        "title": "Order certified death certificates (10 copies)",
        "description": "Order from county vital records. Need copies for: bank, SSA, VA, insurance, DMV, pension, attorney, and spares.",
        "category": "estate",
        "priority": "high",
        "assignee": "primary",
        "phone_name": "County Vital Records",
        "task_key": "order_death_certs",
        "days_offset": 3,
        "blocked_by_key": None,
    },
    {
        "title": "Notify VA of veteran death",
        "description": "Report death to VA. Apply for survivor DIC/pension benefits. Request burial benefits if applicable.",
        "category": "estate",
        "priority": "high",
        "assignee": "primary",
        "phone": "1-800-827-1000",
        "phone_name": "VA Benefits Hotline",
        "task_key": "va_death_report",
        "days_offset": 14,
        "blocked_by_key": None,
    },
    {
        "title": "Consult elder law attorney",
        "description": "Review estate documents, discuss Medicaid planning, asset protection strategies. Get guidance on probate if needed.",
        "category": "legal",
        "priority": "high",
        "assignee": "primary",
        "phone_name": "Elder Law Attorney",
        "task_key": "consult_attorney",
        "days_offset": 7,
        "blocked_by_key": None,
    },
    {
        "title": "Request vehicle title transfer",
        "description": "Apply for title transfer at DMV. Need death certificate and proof of ownership. Cannot sell vehicle until title received.",
        "category": "estate",
        "priority": "medium",
        "assignee": "primary",
        "phone_name": "DMV",
        "task_key": "request_title_transfer",
        "days_offset": 14,
        "blocked_by_key": None,
    },
    {
        "title": "Receive vehicle title",
        "description": "Track title transfer status. Title must be in hand before vehicle can be sold.",
        "category": "estate",
        "priority": "medium",
        "assignee": "primary",
        "task_key": "receive_title",
        "days_offset": 45,
        "blocked_by_key": "request_title_transfer",
    },
    {
        "title": "Sell vehicle",
        "description": "List vehicle for sale once title is received. Consider private sale vs dealer trade-in for best value.",
        "category": "estate",
        "priority": "medium",
        "assignee": "primary",
        "task_key": "sell_vehicle",
        "days_offset": 60,
        "blocked_by_key": "receive_title",  # Title BEFORE sale
    },
    {
        "title": "Cancel vehicle insurance after sale",
        "description": "Cancel auto insurance policy after vehicle is sold. Request refund of unused premium.",
        "category": "estate",
        "priority": "low",
        "assignee": "primary",
        "phone_name": "Insurance Company",
        "task_key": "cancel_vehicle_insurance",
        "days_offset": 65,
        "blocked_by_key": "sell_vehicle",  # Sell BEFORE cancel insurance
    },
    {
        "title": "Notify pension/retirement plan administrators",
        "description": "Report death to any pension or retirement plan. Apply for survivor benefits if available.",
        "category": "estate",
        "priority": "medium",
        "assignee": "primary",
        "task_key": "notify_pension",
        "days_offset": 14,
        "blocked_by_key": None,
    },
    {
        "title": "Update property deeds",
        "description": "Work with attorney to update property ownership. May need affidavit of survivorship or probate.",
        "category": "legal",
        "priority": "medium",
        "assignee": "attorney",
        "task_key": "update_deeds",
        "days_offset": 30,
        "blocked_by_key": "consult_attorney",
    },
    {
        "title": "Review and update beneficiaries",
        "description": "Update beneficiaries on all accounts, insurance policies, and retirement plans.",
        "category": "estate",
        "priority": "medium",
        "assignee": "primary",
        "task_key": "update_beneficiaries",
        "days_offset": 30,
        "blocked_by_key": None,
    },
]


async def generate_estate_tasks(
    db: AsyncSession,
    patient: Patient,
    deceased_spouse_name: str = None,
    deceased_was_veteran: bool = False,
) -> list[Task]:
    """
    Generate estate settlement tasks for a patient whose spouse has died.
    
    Args:
        db: Database session
        patient: Patient record
        deceased_spouse_name: Name of deceased spouse for task descriptions
        deceased_was_veteran: Whether deceased was a veteran (adds VA tasks)
    
    Returns:
        List of created Task objects
    """
    created_tasks = []
    task_id_map = {}  # Maps task_key to task.id for dependency linking
    
    today = date.today()
    spouse_name = deceased_spouse_name or "deceased spouse"
    
    for template in ESTATE_TASKS:
        # Skip VA task if deceased was not a veteran
        if template["task_key"] == "va_death_report" and not deceased_was_veteran:
            continue
        
        # Calculate due date
        due_date = today + timedelta(days=template["days_offset"])
        
        # Customize description with spouse name
        description = template["description"]
        if "{spouse_name}" in description:
            description = description.replace("{spouse_name}", spouse_name)
        
        # Create task
        task = Task(
            patient_id=patient.id,
            title=template["title"],
            description=description,
            category=template["category"],
            priority=template["priority"],
            due_date=due_date,
            phone=template.get("phone"),
            phone_name=template.get("phone_name"),
            assignee=template.get("assignee", "primary"),
            status="pending",
        )
        
        db.add(task)
        await db.flush()  # Get the task ID
        
        task_id_map[template["task_key"]] = task.id
        created_tasks.append((task, template.get("blocked_by_key")))
    
    # Second pass: set blocked_by_id now that we have all task IDs
    for task, blocked_by_key in created_tasks:
        if blocked_by_key and blocked_by_key in task_id_map:
            task.blocked_by_id = task_id_map[blocked_by_key]
    
    await db.commit()
    
    return [task for task, _ in created_tasks]


def get_estate_task_count() -> int:
    """Return the number of estate tasks that will be generated."""
    return len(ESTATE_TASKS)
