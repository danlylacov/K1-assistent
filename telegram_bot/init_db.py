#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""
import asyncio
from database import db


async def init_database():
    """Инициализация базы данных"""
    print("🔌 Подключение к базе данных...")
    await db.connect()
    print("✅ Таблицы созданы успешно!")
    await db.disconnect()
    print("✅ Отключение от базы данных")


if __name__ == "__main__":
    asyncio.run(init_database())

