from fastapi import APIRouter, HTTPException
from app.core.database import db
from app.models.schemas import BotSettingResponse, BotSettingUpdate, RAGConfigUpdate, PromptUpdate
from app.services.rag_service import rag_service

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/bot", response_model=list[BotSettingResponse])
async def get_bot_settings():
    """Получение настроек бота"""
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("SELECT key, value, description, updated_at FROM bot_settings ORDER BY key")
        return [
            BotSettingResponse(
                key=row['key'],
                value=row['value'],
                description=row['description'],
                updated_at=row['updated_at']
            )
            for row in rows
        ]


@router.put("/bot/{key}")
async def update_bot_setting(key: str, setting: BotSettingUpdate):
    """Обновление настройки бота"""
    async with db.pool.acquire() as conn:
        await conn.execute("""
            UPDATE bot_settings
            SET value = $1, updated_at = CURRENT_TIMESTAMP
            WHERE key = $2
        """, setting.value, key)
        
        row = await conn.fetchrow("SELECT key, value, description, updated_at FROM bot_settings WHERE key = $1", key)
        if not row:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        return BotSettingResponse(
            key=row['key'],
            value=row['value'],
            description=row['description'],
            updated_at=row['updated_at']
        )

@router.get("/rag/config")
async def get_rag_config():
    """Получение текущей конфигурации RAG"""
    try:
        return await rag_service.get_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rag/config")
async def update_rag_config(config: RAGConfigUpdate):
    """Обновление конфигурации RAG"""
    try:
        config_dict = config.dict(exclude_none=True)
        result = await rag_service.update_config(config_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rag/prompt")
async def get_rag_prompt():
    """Получение текущего промпта RAG"""
    try:
        return await rag_service.get_prompt()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rag/prompt")
async def update_rag_prompt(prompt: PromptUpdate):
    """Обновление промпта RAG"""
    try:
        result = await rag_service.update_prompt(prompt.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

