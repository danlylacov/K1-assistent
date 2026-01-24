from datetime import datetime
from pathlib import Path
import uuid

from fastapi import APIRouter, HTTPException, Form, UploadFile, File

from app.core.database import db
from app.models.schemas import BroadcastResponse
from app.services.telegram_service import telegram_service
from app.api.routes.scheduler import scheduler

router = APIRouter(prefix="/messages", tags=["messages"])

UPLOADS_DIR = Path(__file__).parent.parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _detect_attachment_type(content_type: str | None) -> str:
    if content_type and content_type.startswith("image/"):
        return "photo"
    return "document"


@router.post("/send")
async def send_message(
    user_id: int = Form(...),
    message: str = Form(""),
    file: UploadFile | None = File(None),
):
    """Отправка сообщения конкретному пользователю (текст + опционально фото/файл)"""
    try:
        attachment_path = None
        attachment_type = None
        attachment_name = None
        attachment_bytes = None

        if file is not None:
            attachment_bytes = await file.read()
            attachment_type = _detect_attachment_type(file.content_type)
            attachment_name = file.filename

        result = await telegram_service.send_with_attachment(
            user_id,
            message,
            attachment=attachment_bytes,
            attachment_type=attachment_type,
            attachment_name=attachment_name,
        )

        async with db.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO admin_messages (user_id, message, attachment_path, attachment_type, attachment_name, sent_by)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                user_id,
                message,
                attachment_path,
                attachment_type,
                attachment_name,
                "admin",
            )

        return {
            "status": "success",
            "message_id": result.get("result", {}).get("message_id"),
            "sent_at": datetime.now(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast", response_model=BroadcastResponse)
async def create_broadcast(
    message: str = Form(...),
    scheduled_at: str | None = Form(None),
    file: UploadFile | None = File(None),
):
    """Создание рассылки (мгновенной или запланированной) (текст + опционально фото/файл)"""
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users")
        user_ids = [row["user_id"] for row in rows]

        dt_scheduled = None
        if scheduled_at:
            dt_scheduled = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))

        attachment_path = None
        attachment_type = None
        attachment_name = None
        attachment_bytes = None

        if file is not None:
            attachment_bytes = await file.read()
            attachment_type = _detect_attachment_type(file.content_type)
            attachment_name = file.filename

            # Для запланированных рассылок нужно хранить файл на диске
            if dt_scheduled is not None:
                safe_name = f"{uuid.uuid4().hex}_{attachment_name}"
                attachment_path = str(UPLOADS_DIR / safe_name)
                Path(attachment_path).write_bytes(attachment_bytes)

        broadcast_id = await conn.fetchval(
            """
            INSERT INTO broadcasts (message, target_user_ids, attachment_path, attachment_type, attachment_name, scheduled_at, status, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            message,
            user_ids,
            attachment_path,
            attachment_type,
            attachment_name,
            dt_scheduled,
            "pending",
            "admin",
        )

        if dt_scheduled is None:
            try:
                results = await telegram_service.send_broadcast_with_attachment(
                    user_ids,
                    message,
                    attachment=attachment_bytes,
                    attachment_type=attachment_type,
                    attachment_name=attachment_name,
                )

                await conn.execute(
                    """
                    UPDATE broadcasts
                    SET status = 'completed', sent_at = CURRENT_TIMESTAMP
                    WHERE id = $1
                    """,
                    broadcast_id,
                )

                return BroadcastResponse(
                    id=broadcast_id,
                    message=message,
                    status="completed",
                    scheduled_at=None,
                    sent_at=datetime.now(),
                    created_at=datetime.now(),
                )
            except Exception as e:
                await conn.execute(
                    """
                    UPDATE broadcasts
                    SET status = 'failed'
                    WHERE id = $1
                    """,
                    broadcast_id,
                )
                raise HTTPException(status_code=500, detail=f"Failed to send broadcast: {str(e)}")

        scheduler.schedule_broadcast(
            broadcast_id,
            dt_scheduled,
            user_ids,
            message,
            attachment_path=attachment_path,
            attachment_type=attachment_type,
            attachment_name=attachment_name,
        )

        return BroadcastResponse(
            id=broadcast_id,
            message=message,
            status="scheduled",
            scheduled_at=dt_scheduled,
            sent_at=None,
            created_at=datetime.now(),
        )


@router.get("/broadcasts")
async def get_broadcasts():
    """Получение списка рассылок"""
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, message, target_user_ids, attachment_type, attachment_name, scheduled_at, sent_at, status, created_at, created_by
            FROM broadcasts
            ORDER BY created_at DESC
            LIMIT 100
            """
        )

        return [
            {
                "id": row["id"],
                "message": row["message"],
                "target_count": len(row["target_user_ids"]) if row["target_user_ids"] else 0,
                "attachment_type": row.get("attachment_type"),
                "attachment_name": row.get("attachment_name"),
                "scheduled_at": row["scheduled_at"].isoformat() if row["scheduled_at"] else None,
                "sent_at": row["sent_at"].isoformat() if row["sent_at"] else None,
                "status": row["status"],
                "created_at": row["created_at"].isoformat(),
                "created_by": row["created_by"],
            }
            for row in rows
        ]

