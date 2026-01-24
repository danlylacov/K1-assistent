import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from app.services.telegram_service import telegram_service
from app.core.database import db


class BroadcastScheduler:
    """Планировщик рассылок"""
    
    def __init__(self):
        self.scheduled_tasks: Dict[int, asyncio.Task] = {}
    
    def schedule_broadcast(
        self,
        broadcast_id: int,
        scheduled_at: datetime,
        user_ids: List[int],
        message: str,
        attachment_path: str | None = None,
        attachment_type: str | None = None,
        attachment_name: str | None = None,
    ):
        """Планирование рассылки"""
        async def send_scheduled_broadcast():
            # Ждем до времени рассылки
            now = datetime.now()
            if scheduled_at > now:
                wait_seconds = (scheduled_at - now).total_seconds()
                await asyncio.sleep(wait_seconds)
            
            try:
                # Отправляем рассылку
                attachment = Path(attachment_path) if attachment_path else None
                results = await telegram_service.send_broadcast_with_attachment(
                    user_ids,
                    message,
                    attachment=attachment,
                    attachment_type=attachment_type,
                    attachment_name=attachment_name,
                )
                
                # Обновляем статус в БД
                async with db.pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE broadcasts
                        SET status = 'completed', sent_at = CURRENT_TIMESTAMP
                        WHERE id = $1
                    """, broadcast_id)
            except Exception as e:
                # Обновляем статус на ошибку
                async with db.pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE broadcasts
                        SET status = 'failed'
                        WHERE id = $1
                    """, broadcast_id)
                print(f"Error sending scheduled broadcast {broadcast_id}: {e}")
            finally:
                # Удаляем задачу из списка
                if broadcast_id in self.scheduled_tasks:
                    del self.scheduled_tasks[broadcast_id]
        
        # Создаем задачу
        task = asyncio.create_task(send_scheduled_broadcast())
        self.scheduled_tasks[broadcast_id] = task
    
    async def load_scheduled_broadcasts(self):
        """Загрузка запланированных рассылок при старте"""
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, message, target_user_ids, scheduled_at, attachment_path, attachment_type, attachment_name
                FROM broadcasts
                WHERE status = 'pending' AND scheduled_at > CURRENT_TIMESTAMP
            """)
            
            for row in rows:
                self.schedule_broadcast(
                    row['id'],
                    row['scheduled_at'],
                    row['target_user_ids'],
                    row['message'],
                    attachment_path=row.get('attachment_path'),
                    attachment_type=row.get('attachment_type'),
                    attachment_name=row.get('attachment_name'),
                )


scheduler = BroadcastScheduler()

