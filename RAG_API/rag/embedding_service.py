from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from RAG_API.rag.config import EmbeddingConfig
import gc
import os

class EmbeddingService:
    """Сервис для создания эмбеддингов"""
    
    def __init__(self, config: EmbeddingConfig = None):
        if config is None:
            from RAG_API.rag.config import DEFAULT_CONFIG
            config = DEFAULT_CONFIG.embedding
        
        self.config = config
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Ленивая загрузка модели с оптимизацией для CPU"""
        if self._model is None:
            # Для версии sentence-transformers==2.2.2 нельзя передавать model_kwargs / encode_kwargs
            # Инициализируем модель в CPU-режиме, остальные параметры задаём при encode()
            self._model = SentenceTransformer(
                self.config.model_name,
                device="cpu"
            )
            
            # Оптимизация модели для CPU
            if hasattr(self._model, 'eval'):
                self._model.eval()
        return self._model
    
    def encode(
        self, 
        texts: List[str], 
        normalize: bool = None,
        batch_size: int = None,
        show_progress: bool = False
    ) -> np.ndarray:
        """Создает эмбеддинги для списка текстов"""
        if normalize is None:
            normalize = self.config.normalize_embeddings
        if batch_size is None:
            batch_size = self.config.batch_size
        
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        """Создает эмбеддинг для запроса"""
        return self.encode([query], show_progress=False)[0]
    
    def encode_batch(self, texts: List[str], batch_size: int = None) -> np.ndarray:
        """Создает эмбеддинги батчами для больших объемов данных с оптимизацией памяти"""
        if batch_size is None:
            batch_size = self.config.batch_size
        
        # Уменьшаем batch_size если тексты очень длинные
        avg_length = sum(len(t) for t in texts[:min(10, len(texts))]) / min(10, len(texts))
        if avg_length > 1000:
            batch_size = max(4, batch_size // 2)
        
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.encode(batch, show_progress=False)
            all_embeddings.append(batch_embeddings)

            # Более агрессивная очистка памяти для ограниченных ресурсов
            if i % (batch_size * 2) == 0:
                gc.collect()
        
        result = np.vstack(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]
        # Финальная очистка
        del all_embeddings
        gc.collect()
        return result
    
    def clear_cache(self):
        """Очищает кэш модели"""
        if self._model is not None:
            del self._model
            self._model = None
        gc.collect()

