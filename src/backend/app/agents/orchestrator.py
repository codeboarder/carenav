"""
Orchestrator Agent for CareNav Florida - Coordinates all other agents.
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
import os
from typing import Optional
from app.agents.base import BaseAgent
from app.agents.eligibility import EligibilityAgent
from app.agents.facility import FacilityAgent
from app.agents.legal import LegalAgent
from app.agents.validator import ValidatorAgent
from app.agents.summarizer import SummarizerAgent

# ============================================================
# KNOWLEDGE BASE SWAP — Rick: After provisioning Azure AI Search,
# change the import below from knowledge_base to search_service
# ============================================================
# CURRENT: ChromaDB (local development)
# from app.services.knowledge_base import get_knowledge_base_service
#
# TARGET: Azure AI Search (enterprise deployment)
# from app.services.search_service import get_search_service
# ============================================================

_knowledge_base_service = None


def _get_knowledge_base():
    """
    Lazy getter for knowledge base service.
    
    Rick: After Azure AI Search is provisioned, swap this to use SearchService:
    
    CURRENT (ChromaDB):
        from app.services.knowledge_base import get_knowledge_base_service
        return get_knowledge_base_service()
    
    TARGET (Azure AI Search):
        from app.services.search_service import get_search_service
        return get_search_service()
    """
    global _knowledge_base_service
    if _knowledge_base_service is None:
        # Check if ChromaDB is disabled
        if os.environ.get("DISABLE_CHROMADB", "false").lower() == "true":
            # Return a dummy service that returns empty results
            class DummyKnowledgeBase:
                def query(self, *args, **kwargs):
                    return []
            _knowledge_base_service = DummyKnowledgeBase()
        else:
            # CURRENT: ChromaDB (swap to search_service after Azure AI Search provisioning)
            from app.services.knowledge_base import get_knowledge_base_service
            _knowledge_base_service = get_knowledge_base_service()
    return _knowledge_base_service


class OrchestratorAgent(BaseAgent):
    """Main orchestrator that coordinates all CareNav agents."""
    
    def __init__(self):
        super().__init__(
            name="orchestrator",
            description="Coordinates multi-agent system for elder care navigation"
        )
        self.eligibility = EligibilityAgent()
        self.facility = FacilityAgent()
        self.legal = LegalAgent()
        self.validator = ValidatorAgent()
        self.summarizer = SummarizerAgent()
        self.knowledge_base = _get_knowledge_base()
    
    def get_system_prompt(self) -> str:
        return """You are the CareNav Orchestrator Agent for Florida elder care navigation.

YOUR ROLE:
- Coordinate specialized agents to help families navigate Medicaid, VA benefits, and facility selection
- Route questions to the appropriate agent(s)
- Synthesize responses into clear, actionable guidance
- Ensure accuracy through validation

AVAILABLE AGENTS:
1. eligibility - Medicaid, VA, Medicare eligibility calculations
2. facility - Facility search, scoring, and comparison
3. legal - Spend-down strategies and mistake prevention
4. validator - Cross-check calculations and detect dissent
5. summarizer - Convert technical info to plain English

ROUTING RULES:
- Financial questions → eligibility + legal
- Facility questions → facility + eligibility (for affordability)
- "Can I..." questions → legal first
- Debt questions → legal (especially deceased spouse debt)
- All responses → validator → summarizer

CRITICAL RULES:
1. NEVER recommend paying deceased spouse's individual debts
2. ALWAYS flag gifts/transfers in look-back period
3. ALWAYS include confidence scores
4. ALWAYS provide citations for legal claims
5. NEVER give legal advice - give legal information

OUTPUT FORMAT (respond in JSON):
{
  "intent": "eligibility|facility|legal|general",
  "agents_to_invoke": ["string"],
  "context_needed": ["string"],
  "rag_query": "string" | null,
  "response_plan": "string"
}"""

    async def process_message(
        self,
        user_message: str,
        patient_context: Optional[dict] = None,
        conversation_history: Optional[list] = None,
    ) -> dict:
        """Process a user message through the multi-agent system."""
        # Get RAG context from knowledge base
        rag_results = self.knowledge_base.query(
            "florida_elder_law",
            user_message,
            n_results=3,
        )
        rag_context = "\n\n".join([r["content"][:500] for r in rag_results])
        
        # Determine intent and route to agents
        routing = await self._determine_routing(user_message, patient_context)
        
        # Collect agent outputs
        agent_outputs = []
        
        if "eligibility" in routing.get("agents", []):
            if patient_context and patient_context.get("financials"):
                elig_result = self._run_eligibility(patient_context)
                agent_outputs.append({"agent": "eligibility", **elig_result})
        
        if "legal" in routing.get("agents", []):
            legal_result = await self._run_legal(user_message, patient_context, rag_context)
            agent_outputs.append({"agent": "legal", **legal_result})
        
        if "facility" in routing.get("agents", []):
            if patient_context:
                facility_result = self._run_facility(patient_context)
                agent_outputs.append({"agent": "facility", **facility_result})
        
        # Validate outputs
        validation = self._validate_outputs(agent_outputs, patient_context)
        
        # Generate final summary
        summary = await self._generate_summary(
            user_message,
            agent_outputs,
            validation,
            patient_context,
        )
        
        return {
            "message": summary.get("summary", ""),
            "agent_outputs": agent_outputs,
            "validation": validation,
            "action_items": summary.get("action_items", []),
            "warnings": summary.get("warnings", []),
            "confidence": validation.get("final_confidence", 75),
        }

    async def _determine_routing(
        self,
        message: str,
        context: Optional[dict],
    ) -> dict:
        """Determine which agents to invoke based on the message."""
        message_lower = message.lower()
        agents = []
        
        # Keyword-based routing
        if any(word in message_lower for word in ["medicaid", "eligible", "qualify", "asset", "income"]):
            agents.append("eligibility")
        
        if any(word in message_lower for word in ["facility", "nursing", "assisted", "place", "where"]):
            agents.append("facility")
        
        if any(word in message_lower for word in ["debt", "pay", "spend", "gift", "transfer", "legal"]):
            agents.append("legal")
        
        if any(word in message_lower for word in ["va", "veteran", "military", "service"]):
            agents.append("eligibility")
        
        # Default to eligibility + legal for general questions
        if not agents:
            agents = ["eligibility", "legal"]
        
        return {"agents": agents}

    def _run_eligibility(self, context: dict) -> dict:
        """Run eligibility calculations."""
        financials = context.get("financials", {})
        veteran_status = context.get("veteran_status", {})
        gifts = context.get("gifts", [])
        
        medicaid = EligibilityAgent.check_medicaid_eligibility(financials)
        va = EligibilityAgent.check_va_eligibility(veteran_status, financials)
        penalty = EligibilityAgent.calculate_gift_penalty(gifts)
        
        return {
            "medicaid": medicaid,
            "va_aa": va,
            "gift_penalty": penalty,
            "confidence": 85,
        }

    async def _run_legal(
        self,
        message: str,
        context: Optional[dict],
        rag_context: str,
    ) -> dict:
        """Run legal agent for guidance."""
        # Check for deceased spouse debt question
        message_lower = message.lower()
        if "deceased" in message_lower or "late" in message_lower or "passed" in message_lower:
            if "debt" in message_lower or "pay" in message_lower or "bill" in message_lower:
                return LegalAgent.evaluate_debt_payment(
                    debt_type="credit_card",
                    debt_holder="deceased_spouse",
                    joint_account=False,
                )
        
        # Get spend-down options if over asset limit
        if context and context.get("financials"):
            medicaid = EligibilityAgent.check_medicaid_eligibility(context["financials"])
            if medicaid.get("over_by", 0) > 0:
                options = LegalAgent.get_spend_down_options(medicaid["over_by"])
                return {
                    "spend_down_options": options,
                    "amount_needed": medicaid["over_by"],
                    "guidance": f"Need to spend down ${medicaid['over_by']:,.2f} to qualify for Medicaid.",
                    "risk_level": "low",
                    "requires_attorney": False,
                }
        
        # Use LLM for complex legal questions
        messages = [
            {"role": "system", "content": self.legal.get_system_prompt()},
            {"role": "system", "content": f"RELEVANT KNOWLEDGE:\n{rag_context}"},
            {"role": "user", "content": message},
        ]
        return await self.openai.chat_completion_json(messages=messages)

    def _run_facility(self, context: dict) -> dict:
        """Run facility search and scoring."""
        zip_code = context.get("zip_code", "33401")
        care_level = context.get("care_level", "AL")
        patient_income = context.get("total_income", 0)
        va_benefit = context.get("va_benefit", 0)
        
        facilities = FacilityAgent.get_sample_facilities(zip_code, care_level)
        
        # Score and sort facilities
        for facility in facilities:
            facility["match_score"] = FacilityAgent.calculate_match_score(
                facility=facility,
                patient_income=patient_income,
                care_level=care_level,
                va_benefit=va_benefit,
            )
            facility["affordability"] = FacilityAgent.calculate_affordability(
                facility_rate=facility.get("rate_low", 0),
                patient_income=patient_income,
                va_benefit=va_benefit,
            )
        
        facilities.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "facilities": facilities[:5],
            "search_criteria": {
                "zip_code": zip_code,
                "care_level": care_level,
            },
            "confidence": 80,
        }

    def _validate_outputs(
        self,
        agent_outputs: list[dict],
        context: Optional[dict],
    ) -> dict:
        """Validate agent outputs."""
        issues = []
        confidences = []
        
        for output in agent_outputs:
            if output.get("confidence"):
                confidences.append(output["confidence"])
            
            # Validate eligibility calculations
            if output.get("agent") == "eligibility" and context:
                financials = context.get("financials", {})
                reported = output.get("medicaid", {}).get("countable", 0)
                validation = ValidatorAgent.validate_eligibility_calculation(
                    reported, financials
                )
                if not validation.get("valid"):
                    issues.append(validation)
        
        # Check for dissent
        dissent = ValidatorAgent.detect_dissent(agent_outputs)
        
        # Calculate final confidence
        final_confidence = ValidatorAgent.calculate_final_confidence(
            confidences, issues, dissent.get("detected", False)
        )
        
        return {
            "validation_passed": len(issues) == 0,
            "issues": issues,
            "dissent": dissent,
            "final_confidence": final_confidence,
        }

    async def _generate_summary(
        self,
        user_message: str,
        agent_outputs: list[dict],
        validation: dict,
        context: Optional[dict],
    ) -> dict:
        """Generate a plain English summary of the results."""
        # Build summary from agent outputs
        summary_parts = []
        action_items = []
        warnings = []
        
        # If no agent outputs, use LLM to generate a response
        if not agent_outputs:
            rag_results = self.knowledge_base.query(
                "florida_elder_law",
                user_message,
                n_results=3,
            )
            rag_context = "\n\n".join([r["content"][:500] for r in rag_results])
            
            messages = [
                {"role": "system", "content": """You are CareNav, a Florida elder care navigation assistant.
Answer questions about Medicaid eligibility, VA benefits, facility selection, and elder care planning.
Be helpful, accurate, and cite Florida-specific rules when relevant.
Key Florida Medicaid facts:
- Asset limit: $2,000 for single applicant
- Income limit: $2,829/month (2024)
- 60-month look-back period for gifts
- Home is exempt if intent to return or spouse lives there
- One vehicle is exempt
VA Aid & Attendance:
- Requires wartime service
- Up to $2,229/month for single veteran
- Up to $1,432/month for surviving spouse"""},
                {"role": "system", "content": f"RELEVANT KNOWLEDGE:\n{rag_context}"},
                {"role": "user", "content": user_message},
            ]
            
            try:
                llm_response = await self.openai.chat_completion(messages=messages)
                return {
                    "summary": llm_response,
                    "action_items": [],
                    "warnings": [],
                    "confidence": 75,
                }
            except Exception as e:
                return {
                    "summary": f"I can help with Florida elder care questions about Medicaid eligibility, VA benefits, and facility selection. Please ask a specific question. (Error: {str(e)})",
                    "action_items": [],
                    "warnings": [],
                    "confidence": 50,
                }
        
        for output in agent_outputs:
            if output.get("agent") == "eligibility":
                medicaid = output.get("medicaid", {})
                va = output.get("va_aa", {})
                patient_name = context.get("patient_name", "your parent") if context else "your parent"
                
                summary_parts.append(
                    SummarizerAgent.format_eligibility_summary(medicaid, va, patient_name)
                )
                
                if not medicaid.get("eligible") and medicaid.get("over_by", 0) > 0:
                    action_items.append({
                        "action": f"Review spend-down options to reduce assets by ${medicaid['over_by']:,.0f}",
                        "priority": "this_week",
                    })
                
                if va.get("eligible"):
                    action_items.append({
                        "action": "Apply for VA Aid & Attendance benefits",
                        "priority": "this_week",
                        "phone": "1-800-827-1000",
                    })
            
            elif output.get("agent") == "facility":
                facilities = output.get("facilities", [])
                patient_income = context.get("total_income", 0) if context else 0
                va_benefit = context.get("va_benefit", 0) if context else 0
                
                summary_parts.append(
                    SummarizerAgent.format_facility_summary(facilities, patient_income, va_benefit)
                )
                
                if facilities:
                    action_items.append({
                        "action": f"Schedule tours at top facilities: {facilities[0].get('name', '')}",
                        "priority": "this_week",
                        "phone": facilities[0].get("phone"),
                    })
            
            elif output.get("agent") == "legal":
                if output.get("guidance") == "DO_NOT_PAY":
                    warnings.append(SummarizerAgent.format_deceased_debt_warning())
                
                if output.get("spend_down_options"):
                    summary_parts.append(
                        SummarizerAgent.format_spend_down_summary(
                            output["spend_down_options"],
                            output.get("amount_needed", 0),
                        )
                    )
        
        # Add validation warnings
        if validation.get("dissent", {}).get("detected"):
            warnings.append(
                f"Note: Our agents had some disagreement about {validation['dissent'].get('topic', 'this topic')}. "
                f"We recommend consulting an elder law attorney for confirmation."
            )
        
        return {
            "summary": "\n\n".join(summary_parts) if summary_parts else "I need more information to help you.",
            "action_items": action_items,
            "warnings": warnings,
            "confidence": validation.get("final_confidence", 75),
        }
