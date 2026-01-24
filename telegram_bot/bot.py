import asyncio
import sys
import aiohttp
from pathlib import Path

# Добавляем родительскую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import BOT_TOKEN, RAG_API_URL
from database import db


# Состояния для FSM
class RegistrationStates(StatesGroup):
    waiting_for_phone = State()


# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Приветственное сообщение
WELCOME_MESSAGE = """
👋 Привет! Я виртуальный ассистент школы программирования KiberOne!

🤖 Что я умею:
• Отвечать на вопросы о нашей школе
• Рассказать о программах обучения
• Помочь с информацией о ценах и расписании
• Записать вас на занятие

Просто задайте мне любой вопрос о школе KiberOne, и я постараюсь помочь! 😊
"""


def get_main_keyboard():
    """Создает главную клавиатуру"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📝 Записаться на занятие"))
    builder.add(KeyboardButton(text="❓ Задать вопрос"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Сохраняем пользователя в БД
    await db.create_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Отправляем приветствие
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=get_main_keyboard()
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
📚 Доступные команды:

/start - Начать работу с ботом
/help - Показать эту справку
/question - Задать вопрос

💡 Вы также можете использовать кнопки меню для навигации.
    """
    await message.answer(help_text, reply_markup=get_main_keyboard())


@dp.message(lambda message: message.text == "📝 Записаться на занятие")
async def registration_start(message: types.Message, state: FSMContext):
    """Начало процесса записи на занятие"""
    await message.answer(
        "📞 Для записи на занятие мне нужен ваш номер телефона.\n\n"
        "Пожалуйста, отправьте номер телефона или нажмите кнопку ниже:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@dp.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    """Обработка номера телефона"""
    phone_number = None
    
    # Проверяем, отправлен ли контакт
    if message.contact:
        phone_number = message.contact.phone_number
    elif message.text:
        # Проверяем, что это похоже на номер телефона
        phone_text = message.text.strip()
        if any(char.isdigit() for char in phone_text):
            phone_number = phone_text
        else:
            await message.answer(
                "❌ Пожалуйста, отправьте корректный номер телефона.\n"
                "Или используйте кнопку для отправки контакта."
            )
            return
    
    if phone_number:
        # Сохраняем запись в БД
        await db.save_registration(message.from_user.id, phone_number)
        
        await message.answer(
            f"✅ Спасибо! Ваш номер телефона ({phone_number}) сохранен.\n\n"
            "Мы свяжемся с вами в ближайшее время для подтверждения записи! 😊",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
    else:
        await message.answer(
            "❌ Не удалось распознать номер телефона.\n"
            "Пожалуйста, попробуйте еще раз или используйте кнопку для отправки контакта."
        )


@dp.message(lambda message: message.text == "❓ Задать вопрос")
async def ask_question_prompt(message: types.Message):
    """Подсказка для вопроса"""
    await message.answer(
        "💬 Задайте ваш вопрос о школе KiberOne:\n\n"
        "Например:\n"
        "• Сколько стоит обучение?\n"
        "• Какие программы есть?\n"
        "• Где находится школа?",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message()
async def handle_question(message: types.Message):
    """Обработка вопросов пользователя"""
    question = message.text.strip()
    
    # Пропускаем команды и кнопки
    if question.startswith("/") or question in ["📝 Записаться на занятие", "❓ Задать вопрос"]:
        return
    
    # Отправляем индикатор печати
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Отправляем запрос к RAG API
        # Таймаут увеличен до 90 секунд на случай загрузки модели при первом запросе
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{RAG_API_URL}/query",
                json={"question": question, "n_results": 3},
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data.get("answer", "К сожалению, не удалось получить ответ.")
                    similarity_scores = data.get("similarity_scores", [])
                    avg_similarity = data.get("avg_similarity", 0.0)
                    
                    # Сохраняем диалог в БД
                    await db.save_conversation(
                        user_id=message.from_user.id,
                        question=question,
                        answer=answer,
                        similarity_scores=similarity_scores if similarity_scores else None,
                        avg_similarity=avg_similarity
                    )
                    
                    # Отправляем ответ
                    await message.answer(
                        answer,
                        reply_markup=get_main_keyboard()
                    )
                else:
                    error_text = await response.text()
                    await message.answer(
                        f"❌ Ошибка при обращении к API: {response.status}\n{error_text}",
                        reply_markup=get_main_keyboard()
                    )
    
    except asyncio.TimeoutError:
        await message.answer(
            "⏱️ Превышено время ожидания ответа. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
    except aiohttp.ClientError as e:
        await message.answer(
            f"❌ Ошибка подключения к серверу: {str(e)}\n\n"
            "Проверьте, что RAG API запущен и доступен.",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка: {str(e)}",
            reply_markup=get_main_keyboard()
        )


async def on_startup():
    """Действия при запуске бота"""
    print("🤖 Бот запускается...")
    await db.connect()
    print("✅ Подключение к базе данных установлено")


async def on_shutdown():
    """Действия при остановке бота"""
    print("🛑 Бот останавливается...")
    await db.disconnect()
    print("✅ Отключение от базы данных")


async def main():
    """Главная функция"""
    # Регистрируем обработчики startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запускаем бота
    print("🚀 Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

