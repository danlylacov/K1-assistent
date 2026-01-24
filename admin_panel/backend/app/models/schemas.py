from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# Документы
class DocumentInfo(BaseModel):
    document_id: str
    chunks_count: int


class DocumentsListResponse(BaseModel):
    documents: List[DocumentInfo]
    total_documents: int
    total_chunks: int


# Пользователи
class UserResponse(BaseModel):
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    telegram_link: str = Field(..., description="Ссылка на Telegram пользователя")
    conversations_count: int = 0
    registrations_count: int = 0


class UsersListResponse(BaseModel):
    users: List[UserResponse]
    total: int


# Сообщения
class ConversationResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str]
    user_username: Optional[str]
    question: str
    answer: str
    avg_similarity: Optional[float]
    created_at: datetime


class ConversationsListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int


# Отправка сообщений
class SendMessageRequest(BaseModel):
    user_id: int
    message: str = Field(..., min_length=1, max_length=4096)


class BroadcastRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    user_ids: Optional[List[int]] = None  # Если None - рассылка всем
    scheduled_at: Optional[datetime] = None  # Если None - мгновенная рассылка


class BroadcastResponse(BaseModel):
    id: int
    message: str
    status: str
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    created_at: datetime


# Настройки бота
class BotSettingResponse(BaseModel):
    key: str
    value: str
    description: Optional[str]
    updated_at: datetime


class BotSettingUpdate(BaseModel):
    value: str


# Настройки RAG
class RAGConfigUpdate(BaseModel):
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    n_results: Optional[int] = None
    use_reranking: Optional[bool] = None
    min_similarity_threshold: Optional[float] = None


class PromptUpdate(BaseModel):
    prompt: str = Field(..., min_length=1)


# Аналитика
class AnalyticsResponse(BaseModel):
    total_users: int
    total_conversations: int
    total_registrations: int
    avg_similarity: float
    conversations_by_day: List[dict]
    top_questions: List[dict]
    similarity_distribution: dict

