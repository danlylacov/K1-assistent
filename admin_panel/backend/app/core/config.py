import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env из корня admin_panel
# config.py находится в admin_panel/backend/app/core/
# Нужно подняться на 3 уровня вверх до admin_panel/
BASE_DIR = Path(__file__).parent.parent.parent.parent  # admin_panel/
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    # Пробуем найти .env в родительских директориях
    for parent in [BASE_DIR.parent, BASE_DIR.parent.parent]:
        parent_env = parent / ".env"
        if parent_env.exists():
            load_dotenv(parent_env, override=True)
            break
# Также пробуем загрузить из текущей директории
load_dotenv(override=False)  # Не перезаписываем, если уже загружено

# Базовые настройки
BASE_DIR = Path(__file__).parent.parent.parent.parent
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("ADMIN_PORT", 8001))

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

# RAG API
RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8000")

# PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "k1_bot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# CORS
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

# JWT (для будущей аутентификации)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа

