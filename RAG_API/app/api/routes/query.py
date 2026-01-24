from fastapi import APIRouter, HTTPException
from RAG_API.app.models.schemas import QueryRequest, QueryResponse
from RAG_API.app.services.rag_service import rag_service

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Запрос к RAG системе"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Проверяем и инициализируем сервис, если он не инициализирован
    if not rag_service.rag_pipeline:
        logger.warning("RAG pipeline не инициализирован, выполняю инициализацию...")
        rag_service.initialize()
        logger.info(f"После инициализации: LLM provider = {rag_service.llm_provider is not None}")
    
    try:
        result = await rag_service.query(
            request.question,
            request.n_results or 3
        )
        
        # Логируем, используется ли LLM
        if "llm_answer" in result:
            logger.info("Ответ сгенерирован через LLM")
        else:
            logger.warning(f"LLM не использован. LLM provider: {rag_service.llm_provider is not None}, has answer: {bool(result.get('answer'))}")
        
        return QueryResponse(
            question=result["question"],
            answer=result.get("llm_answer", result.get("answer", "")),
            similarity_scores=result.get("similarity_scores", []),
            avg_similarity=result.get("avg_similarity", 0.0),
            num_results=result.get("num_results", 0)
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка при выполнении запроса: {str(e)}")

