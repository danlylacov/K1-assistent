#!/usr/bin/env python3
"""
Скрипт для просмотра содержимого базы данных
"""
import asyncio
from database import db
from config import DB_NAME


async def view_database():
    """Просмотр содержимого базы данных"""
    print("🔌 Подключение к базе данных...")
    await db.connect()
    print(f"✅ Подключено к базе данных: {DB_NAME}\n")
    
    async with db.pool.acquire() as conn:
        # 1. Пользователи
        print("=" * 80)
        print("👥 ПОЛЬЗОВАТЕЛИ")
        print("=" * 80)
        users = await conn.fetch("""
            SELECT user_id, username, first_name, last_name, phone_number, 
                   created_at, updated_at
            FROM users
            ORDER BY created_at DESC
        """)
        
        if users:
            for user in users:
                print(f"\nID: {user['user_id']}")
                print(f"  Username: @{user['username'] or 'N/A'}")
                print(f"  Имя: {user['first_name'] or 'N/A'} {user['last_name'] or ''}")
                print(f"  Телефон: {user['phone_number'] or 'не указан'}")
                print(f"  Создан: {user['created_at']}")
                print(f"  Обновлен: {user['updated_at']}")
        else:
            print("  Пользователей пока нет")
        
        # 2. Диалоги
        print("\n" + "=" * 80)
        print("💬 ДИАЛОГИ (последние 20)")
        print("=" * 80)
        conversations = await conn.fetch("""
            SELECT c.id, c.user_id, u.first_name, u.username,
                   c.question, c.answer, c.avg_similarity, c.created_at
            FROM conversations c
            LEFT JOIN users u ON c.user_id = u.user_id
            ORDER BY c.created_at DESC
            LIMIT 20
        """)
        
        if conversations:
            for conv in conversations:
                print(f"\n[{conv['created_at']}] User: {conv['first_name'] or conv['user_id']} (@{conv['username'] or 'N/A'})")
                print(f"  Вопрос: {conv['question'][:100]}{'...' if len(conv['question']) > 100 else ''}")
                print(f"  Ответ: {conv['answer'][:100]}{'...' if len(conv['answer']) > 100 else ''}")
                print(f"  Релевантность: {conv['avg_similarity']:.3f}" if conv['avg_similarity'] else "  Релевантность: N/A")
        else:
            print("  Диалогов пока нет")
        
        # 3. Записи на занятия
        print("\n" + "=" * 80)
        print("📝 ЗАПИСИ НА ЗАНЯТИЯ")
        print("=" * 80)
        registrations = await conn.fetch("""
            SELECT r.id, r.user_id, u.first_name, u.username,
                   r.phone_number, r.created_at
            FROM registrations r
            LEFT JOIN users u ON r.user_id = u.user_id
            ORDER BY r.created_at DESC
        """)
        
        if registrations:
            for reg in registrations:
                print(f"\n[{reg['created_at']}] User: {reg['first_name'] or reg['user_id']} (@{reg['username'] or 'N/A'})")
                print(f"  Телефон: {reg['phone_number']}")
        else:
            print("  Записей пока нет")
        
        # 4. Статистика
        print("\n" + "=" * 80)
        print("📊 СТАТИСТИКА")
        print("=" * 80)
        stats = await conn.fetchrow("""
            SELECT 
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM conversations) as total_conversations,
                (SELECT COUNT(*) FROM registrations) as total_registrations,
                (SELECT COUNT(DISTINCT user_id) FROM conversations) as active_users
        """)
        
        print(f"  Всего пользователей: {stats['total_users']}")
        print(f"  Всего диалогов: {stats['total_conversations']}")
        print(f"  Всего записей на занятия: {stats['total_registrations']}")
        print(f"  Активных пользователей (с вопросами): {stats['active_users']}")
    
    await db.disconnect()
    print("\n✅ Отключение от базы данных")


if __name__ == "__main__":
    asyncio.run(view_database())

