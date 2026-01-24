from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.core.database import db
from app.models.schemas import UsersListResponse, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UsersListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None
):
    """Получение списка пользователей"""
    async with db.pool.acquire() as conn:
        # Базовый запрос
        query = """
            SELECT 
                u.user_id,
                u.username,
                u.first_name,
                u.last_name,
                u.phone_number,
                u.created_at,
                u.updated_at,
                COUNT(DISTINCT c.id) as conversations_count,
                COUNT(DISTINCT r.id) as registrations_count
            FROM users u
            LEFT JOIN conversations c ON u.user_id = c.user_id
            LEFT JOIN registrations r ON u.user_id = r.user_id
        """
        
        params = []
        if search:
            query += " WHERE u.first_name ILIKE $1 OR u.username ILIKE $1 OR u.phone_number ILIKE $1"
            params.append(f"%{search}%")
        
        query += " GROUP BY u.user_id"
        query += " ORDER BY u.created_at DESC"
        query += f" LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, skip])
        
        rows = await conn.fetch(query, *params)
        
        # Общее количество
        count_query = "SELECT COUNT(*) FROM users"
        if search:
            count_query += " WHERE first_name ILIKE $1 OR username ILIKE $1 OR phone_number ILIKE $1"
            total = await conn.fetchval(count_query, f"%{search}%")
        else:
            total = await conn.fetchval(count_query)
        
        users = []
        for row in rows:
            telegram_link = f"https://t.me/{row['username']}" if row['username'] else f"tg://user?id={row['user_id']}"
            users.append(UserResponse(
                user_id=row['user_id'],
                username=row['username'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone_number=row['phone_number'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                telegram_link=telegram_link,
                conversations_count=row['conversations_count'] or 0,
                registrations_count=row['registrations_count'] or 0
            ))
        
        return UsersListResponse(users=users, total=total)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Получение информации о пользователе"""
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT 
                u.*,
                COUNT(DISTINCT c.id) as conversations_count,
                COUNT(DISTINCT r.id) as registrations_count
            FROM users u
            LEFT JOIN conversations c ON u.user_id = c.user_id
            LEFT JOIN registrations r ON u.user_id = r.user_id
            WHERE u.user_id = $1
            GROUP BY u.user_id
        """, user_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        telegram_link = f"https://t.me/{row['username']}" if row['username'] else f"tg://user?id={row['user_id']}"
        
        return UserResponse(
            user_id=row['user_id'],
            username=row['username'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            phone_number=row['phone_number'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            telegram_link=telegram_link,
            conversations_count=row['conversations_count'] or 0,
            registrations_count=row['registrations_count'] or 0
        )

