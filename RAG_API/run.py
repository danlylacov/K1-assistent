#!/usr/bin/env python3
"""
Точка входа для запуска приложения
"""
import sys
import os
from pathlib import Path
import uvicorn

# Добавляем родительскую директорию в путь для импортов
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
parent_path = str(parent_dir)

# Устанавливаем PYTHONPATH
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)
os.environ['PYTHONPATH'] = parent_path

# Оптимизация памяти для Python
os.environ.setdefault('PYTHONHASHSEED', '0')
os.environ.setdefault('MALLOC_ARENA_MAX', '2')
os.environ.setdefault('OMP_NUM_THREADS', '2')

from RAG_API.app.core.config import PORT, DEBUG

if __name__ == "__main__":
    # Оптимизированные настройки для ограниченных ресурсов
    uvicorn.run(
        "RAG_API.app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG,
        workers=1,  # Один воркер для экономии памяти
        limit_concurrency=10,  # Ограничение одновременных запросов
        timeout_keep_alive=5,  # Короткий keep-alive
        log_level="info"
    )

