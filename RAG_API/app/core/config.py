import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Пути
BASE_DIR = Path(__file__).parent.parent.parent
PROMPT_FILE = BASE_DIR / ".prompt.txt"
UPLOAD_DIR = BASE_DIR / "uploads"
CHROMA_DB_PATH = BASE_DIR / os.getenv("CHROMA_DB_PATH", "chroma_db")

# Создаем директории если их нет
UPLOAD_DIR.mkdir(exist_ok=True)
CHROMA_DB_PATH.mkdir(exist_ok=True)

# Настройки сервера
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# GigaChat
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS", "")

# ChromaDB
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "k1_about")

