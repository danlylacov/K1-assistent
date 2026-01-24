#!/usr/bin/env python3
"""
Точка входа для запуска админ-панели
"""
import uvicorn
import os
import sys
from pathlib import Path

# Загружаем .env из корня репозитория (если есть)
from dotenv import load_dotenv
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(repo_root, ".env"))

from app.core.config import PORT

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )

