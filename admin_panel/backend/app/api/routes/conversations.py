from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.core.database import db
from app.models.schemas import ConversationsListResponse, ConversationResponse

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ConversationsListResponse)
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    search: Optional[str] = None
):
    """Получение списка диалогов"""
    async with db.pool.acquire() as conn:
        query = """
            SELECT 
                c.id,
                c.user_id,
                u.first_name as user_name,
                u.username as user_username,
                c.question,
                c.answer,
                c.avg_similarity,
                c.created_at
            FROM conversations c
            LEFT JOIN users u ON c.user_id = u.user_id
            WHERE 1=1
        """
        
        params = []
        param_idx = 1
        
        if user_id:
            query += f" AND c.user_id = ${param_idx}"
            params.append(user_id)
            param_idx += 1
        
        if search:
            query += f" AND (c.question ILIKE ${param_idx} OR c.answer ILIKE ${param_idx})"
            params.append(f"%{search}%")
            param_idx += 1
        
        query += " ORDER BY c.created_at DESC"
        query += f" LIMIT ${param_idx} OFFSET ${param_idx + 1}"
        params.extend([limit, skip])
        
        rows = await conn.fetch(query, *params)
        
        # Общее количество
        count_query = "SELECT COUNT(*) FROM conversations c WHERE 1=1"
        count_params = []
        count_idx = 1
        
        if user_id:
            count_query += f" AND c.user_id = ${count_idx}"
            count_params.append(user_id)
            count_idx += 1
        
        if search:
            count_query += f" AND (c.question ILIKE ${count_idx} OR c.answer ILIKE ${count_idx})"
            count_params.append(f"%{search}%")
        
        if count_params:
            total = await conn.fetchval(count_query, *count_params)
        else:
            total = await conn.fetchval(count_query)
        
        conversations = [
            ConversationResponse(
                id=row['id'],
                user_id=row['user_id'],
                user_name=row['user_name'],
                user_username=row['user_username'],
                question=row['question'],
                answer=row['answer'],
                avg_similarity=row['avg_similarity'],
                created_at=row['created_at']
            )
            for row in rows
        ]
        
        return ConversationsListResponse(conversations=conversations, total=total)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int):
    """Получение конкретного диалога"""
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT 
                c.id,
                c.user_id,
                u.first_name as user_name,
                u.username as user_username,
                c.question,
                c.answer,
                c.avg_similarity,
                c.created_at
            FROM conversations c
            LEFT JOIN users u ON c.user_id = u.user_id
            WHERE c.id = $1
        """, conversation_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationResponse(
            id=row['id'],
            user_id=row['user_id'],
            user_name=row['user_name'],
            user_username=row['user_username'],
            question=row['question'],
            answer=row['answer'],
            avg_similarity=row['avg_similarity'],
            created_at=row['created_at']
        )

