"""Base agent class for CareNav Florida multi-agent system."""
from abc import ABC, abstractmethod
from typing import Optional
from app.services.llm_service import get_llm_provider


class BaseAgent(ABC):
    """Base class for all CareNav agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        # Use the LLM abstraction layer - can be swapped between Azure OpenAI and Copilot SDK
        self.openai = get_llm_provider()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    async def run(
        self,
        user_message: str,
        context: Optional[dict] = None,
        conversation_history: Optional[list] = None,
    ) -> dict:
        """Run the agent with the given input."""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        if context:
            context_message = self._format_context(context)
            messages.append({"role": "system", "content": context_message})
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        response = await self.openai.chat_completion_json(messages=messages)
        return response
    
    def _format_context(self, context: dict) -> str:
        """Format patient context for the agent."""
        return f"""
## PATIENT CONTEXT

**Patient:** {context.get('patient_name', 'Unknown')}, {context.get('patient_age', 'Unknown')} years old
**Location:** {context.get('county', 'Unknown')} County, Florida (ZIP: {context.get('zip_code', 'Unknown')})
**Current Status:** {context.get('current_location', 'Unknown')}
**Diagnosis:** {context.get('diagnosis', 'Unknown')}
**Discharge Date:** {context.get('discharge_date', 'Unknown')}
**Care Level Needed:** {context.get('care_level', 'Unknown')}

**Navigator:** {context.get('navigator_name', 'Unknown')} ({context.get('relationship', 'Unknown')})

## FINANCIAL SUMMARY

**Monthly Income:**
- Social Security: ${context.get('social_security', 0):,.2f}
- Pension: ${context.get('pension', 0):,.2f}
- Other: ${context.get('other_income', 0):,.2f}
- **Total: ${context.get('total_income', 0):,.2f}/month**

**Assets:**
- Countable: ${context.get('countable_assets', 0):,.2f} (Medicaid limit: $2,000)
- Exempt: ${context.get('exempt_assets', 0):,.2f}
- Over limit by: ${context.get('over_limit', 0):,.2f}

## ELIGIBILITY STATUS

**Medicaid:** {context.get('medicaid_status', 'Unknown')}
**VA A&A:** {context.get('va_status', 'Unknown')}

## VETERAN STATUS

**Is Veteran:** {context.get('is_veteran', False)}
**Spouse of Veteran:** {context.get('is_spouse_of_veteran', False)}
**Veteran Deceased:** {context.get('veteran_deceased', False)}
**Wartime Service:** {context.get('wartime_service', False)}
"""
