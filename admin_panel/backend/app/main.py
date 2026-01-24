import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.core.config import CORS_ORIGINS, PORT
from app.core.database import db
from app.api.routes import (
    users, conversations, messages, documents, settings, analytics
)
from app.api.routes.scheduler import scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация
    await db.connect()
    await scheduler.load_scheduled_broadcasts()
    print("✅ Admin panel initialized")
    
    yield
    
    # Очистка
    await db.disconnect()
    print("✅ Admin panel shutdown")


app = FastAPI(
    title="K1 Admin Panel API",
    description="Админ-панель для управления ботом KiberOne",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры (роутеры уже имеют свои префиксы)
# Прокси во фронтенде переписывает /api/* на /*, поэтому префикс не нужен
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(documents.router)
app.include_router(settings.router)
app.include_router(analytics.router)


@app.get("/")
async def root(request: Request):
    """
    Если открыть backend в браузере — покажем ссылку на UI.
    Для клиентов/скриптов по-прежнему возвращаем JSON.
    """
    accept = (request.headers.get("accept") or "").lower()
    if "text/html" in accept:
        return HTMLResponse(
            """
            <!doctype html>
            <html lang="ru">
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>K1 Admin Panel</title>
              </head>
              <body style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; padding: 24px;">
                <h2>K1 Admin Panel</h2>
                <p><b>UI:</b> <a href="http://localhost:5173">http://localhost:5173</a></p>
                <p><b>API Docs:</b> <a href="/docs">/docs</a></p>
                <p style="color:#666">Если UI не открывается — проверьте, что Vite запущен.</p>
              </body>
            </html>
            """.strip()
        )
    return {"message": "K1 Admin Panel API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)

