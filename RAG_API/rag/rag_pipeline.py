from typing import Dict
from RAG_API.rag.config import RAGConfig, DEFAULT_CONFIG
from RAG_API.rag.document_processor import document_to_markdown, split_document
from RAG_API.rag.embedding_service import EmbeddingService
from RAG_API.rag.vector_store import VectorStore
from RAG_API.rag.query_processor import QueryProcessor
from RAG_API.rag.reranker import Reranker


class RAGPipeline:
    """Главный класс RAG пайплайна"""
    
    def __init__(self, config: RAGConfig = None):
        if config is None:
            config = DEFAULT_CONFIG
        
        self.config = config
        self.embedding_service = EmbeddingService(config.embedding)
        
        # Получаем путь к БД из конфигурации
        try:
            from RAG_API.app.core.config import CHROMA_DB_PATH
            db_path = str(CHROMA_DB_PATH)
        except ImportError:
            # Fallback на относительный путь
            from pathlib import Path
            db_path = str(Path(__file__).parent.parent / "chroma_db")
        
        self.vector_store = VectorStore(db_path=db_path, config=config.retrieval)
        self.reranker = Reranker(self.embedding_service) if config.retrieval.use_reranking else None
        self.query_processor = QueryProcessor(
            self.embedding_service,
            self.vector_store,
            self.reranker,
            config.retrieval
        )
    
    def ingest_document(self, document_path: str) -> int:
        """Загружает документ в векторную БД с оптимизацией памяти"""
        import gc
        
        # 1. Конвертация в текст
        document = document_to_markdown(document_path)
        
        # 2. Разбиение на чанки с метаданными
        chunks = split_document(document, self.config.chunking)
        print(f"Документ разбит на {len(chunks)} чанков")
        
        # Очистка памяти после разбиения
        del document
        gc.collect()
        
        # 3. Создание эмбеддингов (уже оптимизировано в encode_batch)
        documents_text = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_service.encode_batch(documents_text)
        print(f"Создано {len(embeddings)} эмбеддингов")
        
        # 4. Загрузка в векторную БД
        count = self.vector_store.upload_documents(documents_text, embeddings, chunks)
        print(f"Загружено {count} документов в векторную БД")
        
        # Финальная очистка памяти
        del documents_text, embeddings
        gc.collect()
        
        return count
    
    def query(
        self, 
        question: str, 
        n_results: int = None,
        return_full_context: bool = True
    ) -> Dict:
        """Выполняет запрос к RAG системе"""
        if n_results is None:
            n_results = self.config.retrieval.n_results
        
        # Поиск релевантных чанков
        results = self.query_processor.search(question, n_results=n_results)
        
        if not results:
            return {
                "question": question,
                "answer": "К сожалению, не найдено релевантной информации.",
                "sources": [],
                "similarity_scores": []
            }
        
        # Форматирование результатов
        sources = []
        similarities = []
        
        for i, result in enumerate(results):
            similarity = result.get("similarity", 1.0 / (1.0 + result["distance"]))
            sources.append({
                "content": result["document"],
                "metadata": result.get("metadata", {}),
                "similarity": similarity,
                "rank": i + 1
            })
            similarities.append(similarity)

        if return_full_context and len(sources) > 0:
            context_parts = [src["content"] for src in sources[:3]]
            answer = "\n\n".join(context_parts)
        else:
            answer = sources[0]["content"] if sources else ""
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "similarity_scores": similarities,
            "avg_similarity": sum(similarities) / len(similarities) if similarities else 0.0,
            "num_results": len(results)
        }
    
    def format_response(self, result: Dict, show_sources: bool = True) -> str:
        """Форматирует ответ для пользователя"""
        output = f"Ответ LLM: {result['llm_answer']}\n\n"
        output += f"Вопрос: {result['question']}\n\n"
        output += f"Ответ:\n{result['answer']}\n\n"
        output += "-" * 80
        
        if show_sources and result['sources']:
            output += f"\n\nИсточники (релевантность: {result['avg_similarity']:.3f}):\n"
            for i, source in enumerate(result['sources'][:3], 1):
                output += f"\n{i}. Релевантность: {source['similarity']:.3f}\n"
                output += f"   {source['content'][:200]}...\n"
        
        return output



