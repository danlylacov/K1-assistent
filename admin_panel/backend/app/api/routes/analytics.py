from fastapi import APIRouter
from app.core.database import db
from app.models.schemas import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics():
    """Получение аналитики"""
    async with db.pool.acquire() as conn:
        # Общая статистика
        stats = await conn.fetchrow("""
            SELECT 
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM conversations) as total_conversations,
                (SELECT COUNT(*) FROM registrations) as total_registrations,
                (SELECT AVG(avg_similarity) FROM conversations WHERE avg_similarity IS NOT NULL) as avg_similarity
        """)
        
        # Диалоги по дням (последние 30 дней)
        conversations_by_day = await conn.fetch("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*)::int as count
            FROM conversations
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        
        # Топ вопросов
        top_questions = await conn.fetch("""
            SELECT 
                question,
                COUNT(*) as count,
                AVG(avg_similarity) as avg_similarity
            FROM conversations
            GROUP BY question
            ORDER BY count DESC
            LIMIT 10
        """)
        
        # Распределение релевантности
        similarity_dist = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN avg_similarity >= 0.7 THEN 'high'
                    WHEN avg_similarity >= 0.5 THEN 'medium'
                    WHEN avg_similarity >= 0.3 THEN 'low'
                    ELSE 'very_low'
                END as category,
                COUNT(*) as count
            FROM conversations
            WHERE avg_similarity IS NOT NULL
            GROUP BY category
        """)
        
        return AnalyticsResponse(
            total_users=stats['total_users'] or 0,
            total_conversations=stats['total_conversations'] or 0,
            total_registrations=stats['total_registrations'] or 0,
            avg_similarity=float(stats['avg_similarity'] or 0),
            conversations_by_day=[
                {"date": row['date'].isoformat() if row['date'] else None, "count": int(row['count'])}
                for row in conversations_by_day
            ],
            top_questions=[
                {
                    "question": row['question'],
                    "count": row['count'],
                    "avg_similarity": float(row['avg_similarity'] or 0)
                }
                for row in top_questions
            ],
            similarity_distribution={
                row['category']: row['count']
                for row in similarity_dist
            }
        )

