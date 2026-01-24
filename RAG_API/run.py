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

from RAG_API.app.core.config import PORT, DEBUG

if __name__ == "__main__":
    uvicorn.run(
        "RAG_API.app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG
    )

