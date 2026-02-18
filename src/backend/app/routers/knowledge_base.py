"""
Knowledge Base API router for CareNav Florida.
Built by Gregory Katz and Rick Weyenberg
Code is as-is, open source
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.knowledge_base import get_knowledge_base_service

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class QueryRequest(BaseModel):
    query: str
    n_results: int = 5
    category: Optional[str] = None


class QueryResult(BaseModel):
    id: str
    content: str
    metadata: dict
    distance: Optional[float] = None


class QueryResponse(BaseModel):
    results: list[QueryResult]
    query: str


@router.post("/query/")
async def query_knowledge_base(request: QueryRequest) -> QueryResponse:
    """Query the elder care knowledge base for relevant information."""
    kb = get_knowledge_base_service()
    
    where_filter = None
    if request.category:
        where_filter = {"category": request.category}
    
    results = kb.query(
        "florida_elder_law",
        request.query,
        n_results=request.n_results,
        where=where_filter,
    )
    
    return QueryResponse(
        results=[QueryResult(**r) for r in results],
        query=request.query,
    )


@router.get("/categories/")
async def get_categories() -> list[str]:
    """Get all available knowledge base categories."""
    return [
        "medicaid",
        "va",
        "medicare",
        "facility",
        "legal",
        "documents",
        "transition",
        "debt",
    ]


@router.get("/topics/")
async def get_topics() -> list[str]:
    """Get all available knowledge base topics."""
    return [
        "eligibility",
        "benefits",
        "financial_planning",
        "estate_planning",
        "regulations",
        "checklists",
        "quality",
        "dual_eligible",
        "estate",
    ]


@router.get("/documents/")
async def get_all_documents() -> list[dict]:
    """Get all documents in the knowledge base."""
    kb = get_knowledge_base_service()
    return kb.get_all_documents()


@router.get("/export/azure-search/")
async def export_for_azure_search() -> list[dict]:
    """Export knowledge base in Azure AI Search compatible format.
    
    This endpoint returns documents formatted for Azure AI Search bulk upload.
    The format includes:
    - @search.action: "upload"
    - id: unique document identifier
    - content: full document text
    - category: document category
    - priority: document priority
    - topic: document topic
    
    To migrate to Azure AI Search:
    1. Create an Azure AI Search index with fields: id, content, category, priority, topic
    2. Use the Azure Search REST API or SDK to upload these documents
    3. Configure semantic search for the content field
    """
    kb = get_knowledge_base_service()
    return kb.export_for_azure_search()


@router.post("/reload/")
async def reload_knowledge_base():
    """Reload the knowledge base with all documents."""
    kb = get_knowledge_base_service()
    kb.load_knowledge_base()
    return {"status": "reloaded", "message": "Knowledge base reloaded successfully"}


class DocumentSummary(BaseModel):
    id: str
    category: str
    topic: str
    priority: str
    content_preview: str


@router.get("/summary/")
async def get_knowledge_base_summary() -> dict:
    """Get a summary of the knowledge base contents."""
    kb = get_knowledge_base_service()
    documents = kb.get_all_documents()
    
    categories = {}
    topics = {}
    
    summaries = []
    for doc in documents:
        cat = doc["metadata"].get("category", "general")
        topic = doc["metadata"].get("topic", "general")
        priority = doc["metadata"].get("priority", "medium")
        
        categories[cat] = categories.get(cat, 0) + 1
        topics[topic] = topics.get(topic, 0) + 1
        
        summaries.append(DocumentSummary(
            id=doc["id"],
            category=cat,
            topic=topic,
            priority=priority,
            content_preview=doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
        ))
    
    return {
        "total_documents": len(documents),
        "categories": categories,
        "topics": topics,
        "documents": [s.model_dump() for s in summaries],
    }
