import asyncpg
from datetime import datetime
from typing import Optional, List, Dict
from config import DATABASE_URL


class Database:
    """Класс для работы с PostgreSQL"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Подключение к базе данных"""
        self.pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10
        )
        await self.create_tables()
    
    async def disconnect(self):
        """Отключение от базы данных"""
        if self.pool:
            await self.pool.close()
    
    async def create_tables(self):
        """Создание таблиц в базе данных"""
        async with self.pool.acquire() as conn:
            # Таблица пользователей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    phone_number VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица диалогов (вопросы и ответы)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    similarity_scores REAL[],
                    avg_similarity REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Таблица записей на занятия
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS registrations (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    phone_number VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
    
    async def create_or_update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ):
        """Создание или обновление пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, updated_at)
                VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    updated_at = CURRENT_TIMESTAMP
            """, user_id, username, first_name, last_name)
    
    async def save_conversation(
        self,
        user_id: int,
        question: str,
        answer: str,
        similarity_scores: Optional[List[float]] = None,
        avg_similarity: Optional[float] = None
    ):
        """Сохранение диалога (вопрос-ответ)"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO conversations (user_id, question, answer, similarity_scores, avg_similarity)
                VALUES ($1, $2, $3, $4, $5)
            """, user_id, question, answer, similarity_scores, avg_similarity)
    
    async def save_registration(self, user_id: int, phone_number: str):
        """Сохранение записи на занятие"""
        async with self.pool.acquire() as conn:
            # Обновляем номер телефона в таблице пользователей
            await conn.execute("""
                UPDATE users 
                SET phone_number = $1, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $2
            """, phone_number, user_id)
            
            # Сохраняем запись
            await conn.execute("""
                INSERT INTO registrations (user_id, phone_number)
                VALUES ($1, $2)
            """, user_id, phone_number)
    
    async def get_user_registrations(self, user_id: int) -> List[Dict]:
        """Получение всех записей пользователя"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, phone_number, created_at
                FROM registrations
                WHERE user_id = $1
                ORDER BY created_at DESC
            """, user_id)
            
            return [
                {
                    "id": row["id"],
                    "phone_number": row["phone_number"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
    
    async def get_user_conversations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Получение последних диалогов пользователя"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT question, answer, avg_similarity, created_at
                FROM conversations
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, user_id, limit)
            
            return [
                {
                    "question": row["question"],
                    "answer": row["answer"],
                    "avg_similarity": row["avg_similarity"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]


# Глобальный экземпляр базы данных
db = Database()

