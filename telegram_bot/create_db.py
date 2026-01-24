#!/usr/bin/env python3
"""
Скрипт для создания базы данных
"""
import asyncio
import asyncpg
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


async def create_database():
    """Создание базы данных"""
    try:
        # Подключаемся к базе postgres для создания новой БД
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        
        # Проверяем, существует ли база данных
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", DB_NAME
        )
        
        if not exists:
            await conn.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✅ База данных {DB_NAME} создана")
        else:
            print(f"ℹ️  База данных {DB_NAME} уже существует")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(create_database())

