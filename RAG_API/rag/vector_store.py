from typing import List, Dict, Optional
import chromadb
from pathlib import Path
import numpy as np
from RAG_API.rag.config import RetrievalConfig


class VectorStore:
    """Класс для работы с векторной базой данных"""

    def __init__(self, db_path: str = None, collection_name: str = "k1_about", config: RetrievalConfig = None):
        # Используем абсолютный путь из конфигурации, если не указан
        if db_path is None:
            try:
                from RAG_API.app.core.config import CHROMA_DB_PATH
                db_path = str(CHROMA_DB_PATH)
            except ImportError:
                # Fallback на относительный путь
                db_path = str(Path(__file__).parent.parent.parent / "chroma_db")
        
        # Убеждаемся, что путь абсолютный
        db_path = str(Path(db_path).resolve())
        Path(db_path).mkdir(parents=True, exist_ok=True)
        
        # Оптимизация ChromaDB для ограниченной памяти
        # Используем настройки для экономии памяти
        try:
            # Пытаемся использовать оптимизированные настройки
            settings = chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
            self.client = chromadb.PersistentClient(path=db_path, settings=settings)
        except Exception:
            # Fallback на стандартный клиент если настройки не поддерживаются
            self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        if config is None:
            from RAG_API.rag.config import DEFAULT_CONFIG
            config = DEFAULT_CONFIG.retrieval
        self.config = config
        self._collection = None

    @property
    def collection(self):
        """Ленивая загрузка коллекции"""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "RAG Knowledge Base"}
            )
        return self._collection

    def upload_documents(
            self,
            documents: List[str],
            embeddings: np.ndarray,
            chunks: List[Dict],
            replace_all: bool = True,
            batch_size: int = 100  # Загружаем батчами для экономии памяти
    ):
        """Загружает документы в векторную БД батчами для оптимизации памяти
        
        Args:
            documents: Список текстов документов
            embeddings: Массив эмбеддингов
            chunks: Список чанков с метаданными
            replace_all: Если True, удаляет всю коллекцию перед добавлением (по умолчанию True)
            batch_size: Размер батча для загрузки (по умолчанию 100)
        """
        import gc
        
        if replace_all:
            try:
                self.client.delete_collection(self.collection_name)
                self._collection = None  # Сбрасываем кэш
            except:
                pass

        self.collection

        # Загружаем батчами для экономии памяти
        total_docs = len(documents)
        for batch_start in range(0, total_docs, batch_size):
            batch_end = min(batch_start + batch_size, total_docs)
            batch_docs = documents[batch_start:batch_end]
            batch_embeddings = embeddings[batch_start:batch_end]
            batch_chunks = chunks[batch_start:batch_end]
            
            metadatas = []
            ids = []
            for i, chunk in enumerate(batch_chunks):
                metadata = chunk.get("metadata", {})
                metadata["document"] = Path(chunk["source"]).name
                metadata["chunk_id"] = chunk.get("chunk_id", batch_start + i)
                metadatas.append(metadata)
                ids.append(f"doc_{batch_start + i}")

            # Загрузка батча в БД
            self.collection.add(
                documents=batch_docs,
                embeddings=batch_embeddings.tolist(),
                metadatas=metadatas,
                ids=ids,
            )
            
            # Очистка памяти после каждого батча
            del batch_docs, batch_embeddings, batch_chunks, metadatas, ids
            if batch_start % (batch_size * 4) == 0:
                gc.collect()

        return self.collection.count()

    def search(
            self,
            query_embeddings: List[List[float]],
            n_results: int = None,
            where: Optional[Dict] = None,
            where_document: Optional[Dict] = None,
    ) -> Dict:
        """Поиск в векторной БД"""
        if n_results is None:
            n_results = self.config.n_results

        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"],
        )

    def get_collection_stats(self) -> Dict:
        """Получает статистику коллекции"""
        return {
            "name": self.collection.name,
            "count": self.collection.count(),
        }
