import asyncpg
from typing import Optional
from app.core.config import DATABASE_URL


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
        await self.create_admin_tables()
    
    async def disconnect(self):
        """Отключение от базы данных"""
        if self.pool:
            await self.pool.close()
    
    async def create_admin_tables(self):
        """Создание дополнительных таблиц для админки"""
        async with self.pool.acquire() as conn:
            # Базовые таблицы (чтобы админка работала даже если бот ещё не запущен)
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

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS registrations (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    phone_number VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)

            # Таблица для приветственных сообщений
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(255) UNIQUE NOT NULL,
                    value TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица для рассылок
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS broadcasts (
                    id SERIAL PRIMARY KEY,
                    message TEXT NOT NULL,
                    target_user_ids BIGINT[],
                    attachment_path TEXT,
                    attachment_type VARCHAR(50),
                    attachment_name TEXT,
                    scheduled_at TIMESTAMP,
                    sent_at TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(255)
                )
            """)
            
            # Таблица для отправленных сообщений админом
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS admin_messages (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    message TEXT NOT NULL,
                    attachment_path TEXT,
                    attachment_type VARCHAR(50),
                    attachment_name TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_by VARCHAR(255),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)

            # Миграции для существующих таблиц (если создавались без полей вложений)
            await conn.execute("ALTER TABLE broadcasts ADD COLUMN IF NOT EXISTS attachment_path TEXT")
            await conn.execute("ALTER TABLE broadcasts ADD COLUMN IF NOT EXISTS attachment_type VARCHAR(50)")
            await conn.execute("ALTER TABLE broadcasts ADD COLUMN IF NOT EXISTS attachment_name TEXT")
            await conn.execute("ALTER TABLE admin_messages ADD COLUMN IF NOT EXISTS attachment_path TEXT")
            await conn.execute("ALTER TABLE admin_messages ADD COLUMN IF NOT EXISTS attachment_type VARCHAR(50)")
            await conn.execute("ALTER TABLE admin_messages ADD COLUMN IF NOT EXISTS attachment_name TEXT")
            
            # Инициализация дефолтных настроек
            await conn.execute("""
                INSERT INTO bot_settings (key, value, description)
                VALUES 
                    ('welcome_message', 'Привет! Я виртуальный ассистент KiberOne.', 'Приветственное сообщение при /start'),
                    ('help_message', 'Я могу ответить на вопросы о школе KiberOne.', 'Сообщение помощи')
                ON CONFLICT (key) DO NOTHING
            """)


# Глобальный экземпляр
db = Database()

