from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from RAG_API.app.models.schemas import ConfigUpdate, PromptUpdate
from RAG_API.app.core.prompt import load_prompt, save_prompt
from RAG_API.app.services.rag_service import rag_service

router = APIRouter(prefix="/config", tags=["config"])


@router.put("/prompt")
async def update_prompt(request: PromptUpdate):
    """Обновление системного промпта"""
    try:
        save_prompt(request.prompt)
        return JSONResponse({
            "status": "success",
            "message": "Промпт обновлен"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении промпта: {str(e)}")


@router.get("/prompt")
async def get_prompt():
    """Получение текущего промпта"""
    prompt = load_prompt()
    return JSONResponse({"prompt": prompt})


@router.put("/settings")
async def update_settings(config: ConfigUpdate):
    """Обновление базовых настроек"""
    try:
        current_config = rag_service.config
        
        # Обновляем конфигурацию
        if config.chunk_size is not None:
            current_config.chunking.chunk_size = config.chunk_size
        if config.chunk_overlap is not None:
            current_config.chunking.chunk_overlap = config.chunk_overlap
        if config.n_results is not None:
            current_config.retrieval.n_results = config.n_results
        if config.use_reranking is not None:
            current_config.retrieval.use_reranking = config.use_reranking
        if config.min_similarity_threshold is not None:
            current_config.retrieval.min_similarity_threshold = config.min_similarity_threshold
        
        # Обновляем сервис
        rag_service.update_config(current_config)
        
        return JSONResponse({
            "status": "success",
            "message": "Настройки обновлены",
            "config": {
                "chunk_size": current_config.chunking.chunk_size,
                "chunk_overlap": current_config.chunking.chunk_overlap,
                "n_results": current_config.retrieval.n_results,
                "use_reranking": current_config.retrieval.use_reranking,
                "min_similarity_threshold": current_config.retrieval.min_similarity_threshold
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении настроек: {str(e)}")


@router.get("/settings")
async def get_settings():
    """Получение текущих настроек"""
    config = rag_service.config
    return JSONResponse({
        "chunk_size": config.chunking.chunk_size,
        "chunk_overlap": config.chunking.chunk_overlap,
        "n_results": config.retrieval.n_results,
        "use_reranking": config.retrieval.use_reranking,
        "min_similarity_threshold": config.retrieval.min_similarity_threshold
    })

