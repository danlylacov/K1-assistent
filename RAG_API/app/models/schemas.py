from typing import Optional, List
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Запрос к RAG системе"""
    question: str = Field(..., description="Вопрос пользователя")
    n_results: Optional[int] = Field(3, description="Количество результатов для поиска")


class QueryResponse(BaseModel):
    """Ответ от RAG системы"""
    question: str
    answer: str
    similarity_scores: List[float]
    avg_similarity: float
    num_results: int


class ConfigUpdate(BaseModel):
    """Обновление конфигурации"""
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    n_results: Optional[int] = None
    use_reranking: Optional[bool] = None
    min_similarity_threshold: Optional[float] = None


class PromptUpdate(BaseModel):
    """Обновление промпта"""
    prompt: str = Field(..., description="Новый системный промпт")


class HealthResponse(BaseModel):
    """Ответ health check"""
    status: str
    pipeline_initialized: bool
    llm_initialized: bool


class DocumentInfo(BaseModel):
    """Информация о документе"""
    document_id: str
    chunks_count: int


class DocumentsListResponse(BaseModel):
    """Список всех документов"""
    documents: List[DocumentInfo]
    total_documents: int
    total_chunks: int

