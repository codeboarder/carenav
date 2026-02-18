"""API routers for CareNav Florida."""
from .patients import router as patients_router
from .chat import router as chat_router
from .eligibility import router as eligibility_router
from .facilities import router as facilities_router
from .tasks import router as tasks_router
from .documents import router as documents_router
from .bills import router as bills_router
from .income_phases import router as income_phases_router
from .benefit_applications import router as benefit_applications_router
from .contacts import router as contacts_router
from .assets import router as assets_router
from .medical import router as medical_router
from .insurance import router as insurance_router
from .selected_facility import router as selected_facility_router
from .wins import router as wins_router

__all__ = [
    "patients_router",
    "chat_router",
    "eligibility_router",
    "facilities_router",
    "tasks_router",
    "documents_router",
    "bills_router",
    "income_phases_router",
    "benefit_applications_router",
    "contacts_router",
    "assets_router",
    "medical_router",
    "insurance_router",
    "selected_facility_router",
    "wins_router",
]
