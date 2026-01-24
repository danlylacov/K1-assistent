from fastapi import APIRouter
from RAG_API.app.models.schemas import HealthResponse
from RAG_API.app.services.rag_service import rag_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    """Проверка здоровья сервиса"""
    return HealthResponse(
        status="healthy",
        pipeline_initialized=rag_service.rag_pipeline is not None,
        llm_initialized=rag_service.llm_provider is not None
    )

