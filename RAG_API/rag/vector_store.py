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
            replace_all: bool = True
    ):
        """Загружает документы в векторную БД
        
        Args:
            documents: Список текстов документов
            embeddings: Массив эмбеддингов
            chunks: Список чанков с метаданными
            replace_all: Если True, удаляет всю коллекцию перед добавлением (по умолчанию True)
        """
        if replace_all:
            try:
                self.client.delete_collection(self.collection_name)
                self._collection = None  # Сбрасываем кэш
            except:
                pass

        self.collection

        metadatas = []
        ids = []
        for i, chunk in enumerate(chunks):
            metadata = chunk.get("metadata", {})
            metadata["document"] = Path(chunk["source"]).name
            metadata["chunk_id"] = chunk.get("chunk_id", i)
            metadatas.append(metadata)
            ids.append(f"doc_{i}")

        # Загрузка в БД
        self.collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids,
        )

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
