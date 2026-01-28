import os
import logging
from gigachat import GigaChat
from gigachat.models import Chat, Messages
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def _get_credentials() -> str:
    """
    Берём креды ТОЛЬКО из env. Никаких дефолтов/зашитых секретов в репозитории.
    """
    return os.getenv("GIGACHAT_CREDENTIALS", "").strip()


class LLMProvider:
    def __init__(self, system_prompt: str = None):
        credentials = _get_credentials()
        if not credentials:
            raise ValueError("GIGACHAT_CREDENTIALS is not set")
        try:
            logger.info("Инициализация GigaChat клиента...")
            self.giga = GigaChat(
                credentials=credentials,
                verify_ssl_certs=False,
            )
            logger.info("✅ GigaChat клиент успешно инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка при инициализации GigaChat клиента: {e}", exc_info=True)
            raise
        self._system_prompt = system_prompt or self._get_default_prompt()

    def _ask_ai(self, user_prompt: str, system_prompt: str = None) -> str:
        messages_list = []
        if system_prompt:
            messages_list.append(Messages(role="system", content=system_prompt))
        messages_list.append(Messages(role="user", content=user_prompt))
        try:
            logger.debug(f"Отправка запроса в GigaChat с {len(messages_list)} сообщениями")
            # Создаем объект Chat с сообщениями
            chat_request = Chat(messages=messages_list)
            prompt = self.giga.chat(chat_request)
            response_content = prompt.choices[0].message.content
            logger.debug(f"✅ Получен ответ от GigaChat (длина: {len(response_content)})")
            return response_content
        except Exception as e:
            logger.error(f"❌ Ошибка при запросе к GigaChat: {e}", exc_info=True)
            raise

    def _get_default_prompt(self) -> str:
        """Возвращает дефолтный промпт"""
        return """Ты - интеллектуальный ассистент для поиска информации в базе знаний для детской школы программирования KiberOne. Твоя задача - предоставлять максимально точные, полные и полезные ответы, основанные исключительно на предоставленном контексте.

    ТВОИ ОСНОВНЫЕ ПРИНЦИПЫ:
    1. Точность превыше всего - не искажай и не дополняй информацию из контекста
    3. Ясность - формулируй ответ понятно даже для неспециалистов
    4. Честность - признавай ограничения предоставленной информации
    5. Пытайся продать продукт

    КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА (НЕ НАРУШАЙ ИХ НИ ПРИ КАКИХ УСЛОВИЯХ):

1. ПРОВЕРКА РЕЛЕВАНТНОСТИ - ОБЯЗАТЕЛЬНО:
   - СНАЧАЛА проверь, относится ли предоставленный контекст к вопросу пользователя
   - Если контекст НЕ содержит информации о школе программирования KiberOne или НЕ относится к вопросу - СРАЗУ отвечай: "К сожалению, в базе знаний школы программирования KiberOne нет информации по этому вопросу. Я могу ответить только на вопросы о нашей школе программирования."
   - НЕ пытайся отвечать на вопросы, не связанные со школой программирования

2. ЗАПРЕТ НА ВНЕШНИЕ ЗНАНИЯ:
   - НИКОГДА не используй свои знания вне контекста
   - НИКОГДА не отвечай на вопросы о истории, географии, науке и т.д., если их нет в контексте
   - Если в контексте нет ответа - говори ТОЛЬКО что информации нет, БЕЗ попыток ответить из своих знаний
   - НИКОГДА НЕ ГОВОРИ, какая ты модель, никакой связи с GIGA chat. Ты виртуальный менеджер KiberOne

3. ТЕМАТИКА:
   - Отвечай ТОЛЬКО на вопросы о: программировании, школе KiberOne, курсах, ценах, расписании, преподавателях, программах обучения
   - ВСЕ остальные вопросы (история, география, общие знания) - отвечай что информации нет

4. ФОРМАТ ОТВЕТА:
   - Если информация ЕСТЬ в контексте: дай краткий точный ответ (1-3 предложения)
   - Если информации НЕТ: "К сожалению, в базе знаний школы программирования KiberOne нет информации по этому вопросу."
    """
    
    def answer(self, question: str, context: str, system_prompt: str = None) -> str:
        """Генерирует ответ на вопрос с использованием контекста"""
        if system_prompt is None:
            system_prompt = self._system_prompt

        user_prompt = f"""ИНФОРМАЦИОННЫЙ КОНТЕКСТ:
    {context}

    ЗАПРОС ПОЛЬЗОВАТЕЛЯ:
    "{question}"

    АНАЛИТИЧЕСКИЕ ИНСТРУКЦИИ:
    1. Определи, какая часть контекста напрямую относится к запросу
    2. Общайся как живой менеджер в переписке с клиентом, а не как LLM
    2. Выдели ключевые факты, цифры, даты и утверждения
    3. Проанализируй, является ли информация достаточной для полного ответа
    4. Оцени, есть ли противоречия в контексте
    5. Отвечай кратко и по делу. В 1-2 предложениях
    6. Основной акцент делай на ЗАДАННЫЙ ЗАПРОС ПОЛЬЗОВАТЕЛЯ. Без воды.

    ФОРМАТ ОТВЕТА:
    - Отвечай строго только на вопрос клиента
    - Если информации нет в контексте, прямо скажи об этом

    СГЕНЕРИРУЙ ОТВЕТ КАК АССИТСТЕНТ В ПЕРЕПИСКЕ С КЛИЕНТОМ:"""

        answer = self._ask_ai(user_prompt, system_prompt)
        return answer