import asyncio
import os
import logging
from typing import Optional, Dict
from RAG_API.rag.rag_pipeline import RAGPipeline
from RAG_API.rag.config import RAGConfig, DEFAULT_CONFIG
from RAG_API.rag.giga_chat import LLMProvider
from RAG_API.app.core.prompt import load_prompt

logger = logging.getLogger(__name__)


class RAGService:
    """Сервис для работы с RAG системой"""
    
    def __init__(self):
        self.rag_pipeline: Optional[RAGPipeline] = None
        self.llm_provider: Optional[LLMProvider] = None
        self.config: RAGConfig = DEFAULT_CONFIG
    
    def initialize(self):
        """Инициализация RAG pipeline и LLM provider"""
        logger.info("🔄 Инициализация RAG pipeline...")
        self.rag_pipeline = RAGPipeline(self.config)
        
        # Предзагружаем модель embedding, чтобы первый запрос был быстрее
        # Делаем тестовый encode для гарантированной загрузки модели
        logger.info("📥 Предзагрузка модели embedding (это может занять ~1 минуту)...")
        try:
            # Явно загружаем модель через обращение к свойству model
            # Это триггерит ленивую загрузку модели
            _ = self.rag_pipeline.embedding_service.model
            # Делаем тестовый encode для гарантированной загрузки всех компонентов модели
            _ = self.rag_pipeline.embedding_service.encode_query("test")
            logger.info("✅ Модель embedding загружена и готова к использованию")
        except Exception as e:
            logger.error(f"⚠️  Предзагрузка модели не удалась: {e}", exc_info=True)
        
        # LLM опционален: включается только если заданы креды
        # Проверяем переменную окружения напрямую
        gigachat_creds = os.getenv("GIGACHAT_CREDENTIALS", "").strip()
        logger.info(f"Проверка GIGACHAT_CREDENTIALS: {'задана' if gigachat_creds else 'не задана'} (длина: {len(gigachat_creds)})")
        
        if gigachat_creds:
            try:
                logger.info("🤖 Инициализация LLM provider...")
                self.llm_provider = LLMProvider()
                logger.info("✅ LLM provider инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка при инициализации LLM provider: {e}", exc_info=True)
                self.llm_provider = None
        else:
            self.llm_provider = None
            logger.info("ℹ️  LLM provider пропущен (GIGACHAT_CREDENTIALS не задан)")
        
        logger.info("✅ RAG pipeline инициализирован")
    
    def update_config(self, new_config: RAGConfig):
        """Обновление конфигурации"""
        self.config = new_config
        self.rag_pipeline = RAGPipeline(self.config)
    
    async def query(self, question: str, n_results: int = 3) -> Dict:
        """Выполняет запрос к RAG системе"""
        # Инициализируем, если еще не инициализировано
        if not self.rag_pipeline:
            print("⚠️  RAG pipeline не инициализирован, выполняю инициализацию...", flush=True)
            logger.warning("RAG pipeline не инициализирован, выполняю инициализацию...")
            self.initialize()
            print(f"✅ После инициализации: LLM provider = {self.llm_provider is not None}", flush=True)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.rag_pipeline.query,
            question,
            n_results,
            True
        )
        
        # Генерируем ответ через LLM
        print(f"🔍 Проверка LLM: provider={self.llm_provider is not None}, has_answer={bool(result.get('answer'))}", flush=True)
        if self.llm_provider and result.get("answer"):
            print("🤖 Использование LLM для генерации ответа...", flush=True)
            logger.info("Использование LLM для генерации ответа")
            prompt = load_prompt()
            
            def _call_llm():
                return self.llm_provider.answer(
                    question,
                    result["answer"],
                    system_prompt=prompt
                )
            
            try:
                llm_answer = await loop.run_in_executor(None, _call_llm)
                result["llm_answer"] = llm_answer
                result["answer"] = llm_answer
                print("✅ LLM ответ успешно сгенерирован", flush=True)
                logger.info("LLM ответ успешно сгенерирован")
            except Exception as e:
                print(f"❌ Ошибка при генерации LLM ответа: {e}", flush=True)
                logger.error(f"Ошибка при генерации LLM ответа: {e}", exc_info=True)
                # Оставляем оригинальный ответ, если LLM не сработал
        else:
            if not self.llm_provider:
                print(f"⚠️  LLM provider не инициализирован (is None: {self.llm_provider is None})", flush=True)
                logger.warning("LLM provider не инициализирован, используется оригинальный ответ")
            elif not result.get("answer"):
                print("⚠️  Нет контекста для генерации ответа", flush=True)
                logger.warning("Нет контекста для генерации ответа")
        
        return result
    
    async def ingest_document(self, document_path: str) -> int:
        """Загружает документ в базу знаний"""
        if not self.rag_pipeline:
            raise RuntimeError("RAG pipeline not initialized")
        
        loop = asyncio.get_event_loop()
        count = await loop.run_in_executor(
            None,
            self.rag_pipeline.ingest_document,
            document_path
        )
        return count
    
    async def delete_document(self, doc_id: str) -> int:
        """Удаляет документ из базы знаний"""
        if not self.rag_pipeline:
            raise RuntimeError("RAG pipeline not initialized")
        
        loop = asyncio.get_event_loop()
        
        def _delete_doc():
            collection = self.rag_pipeline.vector_store.collection
            all_data = collection.get()
            
            ids_to_delete = []
            for i, metadata in enumerate(all_data.get("metadatas", [])):
                if metadata.get("document") == doc_id:
                    ids_to_delete.append(all_data["ids"][i])
            
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                return len(ids_to_delete)
            return None
        
        deleted_count = await loop.run_in_executor(None, _delete_doc)
        return deleted_count
    
    async def get_all_documents(self) -> Dict:
        """Получает список всех документов в базе знаний"""
        if not self.rag_pipeline:
            raise RuntimeError("RAG pipeline not initialized")
        
        loop = asyncio.get_event_loop()
        
        def _get_documents():
            collection = self.rag_pipeline.vector_store.collection
            all_data = collection.get()
            
            # Подсчитываем количество чанков для каждого документа
            doc_counts = {}
            for metadata in all_data.get("metadatas", []):
                doc_id = metadata.get("document", "unknown")
                doc_counts[doc_id] = doc_counts.get(doc_id, 0) + 1
            
            # Формируем список документов
            documents = [
                {"document_id": doc_id, "chunks_count": count}
                for doc_id, count in doc_counts.items()
            ]
            
            return {
                "documents": documents,
                "total_documents": len(documents),
                "total_chunks": sum(doc_counts.values())
            }
        
        result = await loop.run_in_executor(None, _get_documents)
        return result


# Глобальный экземпляр сервиса
rag_service = RAGService()

