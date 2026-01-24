import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from RAG_API.app.core.config import PORT, DEBUG
from RAG_API.app.services.rag_service import rag_service
from RAG_API.app.api.routes import documents, config
from RAG_API.app.api.routes import query, health

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    import logging
    import sys
    logger = logging.getLogger(__name__)
    
    # Инициализация
    print("🚀 Запуск lifespan, инициализация RAG сервиса...", flush=True)
    logger.info("🚀 Запуск lifespan, инициализация RAG сервиса...")
    rag_service.initialize()
    print(f"✅ RAG сервис инициализирован. LLM provider: {rag_service.llm_provider is not None}", flush=True)
    logger.info(f"✅ RAG сервис инициализирован в lifespan. LLM provider: {rag_service.llm_provider is not None}")
    
    yield
    
    # Очистка (если нужна)
    print("🛑 Завершение работы приложения", flush=True)
    logger.info("🛑 Завершение работы приложения")


app = FastAPI(
    title="K1 RAG API",
    description="API для RAG системы школы программирования KiberOne",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем роутеры
app.include_router(query.router)
app.include_router(documents.router)
app.include_router(config.router)
app.include_router(health.router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG
    )

