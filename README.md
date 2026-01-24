# K1 Assistant - Виртуальный ассистент школы программирования KiberOne

Интеллектуальный чат-бот на базе RAG (Retrieval-Augmented Generation) для автоматизации ответов на вопросы о школе программирования KiberOne.

## Содержание

- [Описание проекта](#описание-проекта)
- [Технологии](#технологии)
- [Архитектура](#архитектура)
- [Модули системы](#модули-системы)
- [Установка и запуск](#установка-и-запуск)
- [Конфигурация](#конфигурация)

## Описание проекта

K1 Assistant — это комплексная система виртуального ассистента, которая использует технологии RAG для предоставления точных и релевантных ответов на вопросы пользователей о школе программирования KiberOne. Система включает:

- **Telegram-бот** для взаимодействия с пользователями
- **RAG API** для обработки запросов и генерации ответов
- **Админ-панель** для управления контентом и аналитики
- **Векторная база данных** для хранения знаний

## Технологии

### Backend

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?style=for-the-badge&logo=docker&logoColor=white)

### AI/ML

![GigaChat](https://img.shields.io/badge/GigaChat-0.1.12-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.18-FFA500?style=for-the-badge&logo=chromadb&logoColor=white)
![Sentence Transformers](https://img.shields.io/badge/Sentence_Transformers-2.2.2-4CAF50?style=for-the-badge&logo=huggingface&logoColor=white)
![Transformers](https://img.shields.io/badge/Transformers-4.30-FFD700?style=for-the-badge&logo=huggingface&logoColor=white)

### Frontend

![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Axios](https://img.shields.io/badge/Axios-1.6-5A29E4?style=for-the-badge&logo=axios&logoColor=white)

### Telegram

![Aiogram](https://img.shields.io/badge/Aiogram-3.3-0088CC?style=for-the-badge&logo=telegram&logoColor=white)

### Дополнительные библиотеки

- **asyncpg** — асинхронный драйвер PostgreSQL
- **aiohttp** — асинхронный HTTP клиент
- **pydantic** — валидация данных
- **langchain-text-splitters** — разбиение документов
- **python-docx** — обработка Word документов
- **markitdown** — конвертация Markdown

## Архитектура

Система построена по микросервисной архитектуре и состоит из следующих компонентов:

**Пользователи** взаимодействуют с системой через **Telegram Bot**, который обрабатывает сообщения и отправляет запросы в **RAG API Service** для получения ответов.

**Admin Panel Backend** предоставляет REST API для управления системой и взаимодействует с **PostgreSQL Database** для хранения структурированных данных.

**RAG API Service** является ядром системы и использует:
- **ChromaDB** для хранения векторных представлений документов
- **GigaChat API** для генерации ответов на основе найденного контекста
- **Embedding Model** (Sentence Transformers) для создания векторных представлений текста

**RAG Pipeline** работает следующим образом:
1. Документы загружаются и обрабатываются **Document Processor**, который разбивает их на семантические чанки
2. **Embedding Service** генерирует векторные представления для каждого чанка
3. Векторы сохраняются в **ChromaDB** (Vector Store)
4. При запросе пользователя **Query Processor** выполняет семантический поиск релевантных фрагментов
5. Найденный контекст вместе с вопросом передается в **GigaChat LLM** для генерации финального ответа

## Модули системы

### 1. Telegram Bot (`telegram_bot/`)

**Назначение:** Основной интерфейс взаимодействия с пользователями через Telegram.

**Основные функции:**
- Прием и обработка сообщений от пользователей
- Регистрация пользователей (сбор контактных данных)
- Отправка запросов в RAG API для получения ответов
- Сохранение истории диалогов в PostgreSQL
- Управление состояниями через FSM (Finite State Machine)

**Технологии:**
- `aiogram 3.3.0` — фреймворк для Telegram ботов
- `asyncpg` — асинхронная работа с PostgreSQL
- `aiohttp` — HTTP клиент для запросов к RAG API

**Ключевые файлы:**
- `bot.py` — основная логика бота
- `database.py` — работа с базой данных
- `config.py` — конфигурация

---

### 2. RAG API (`RAG_API/`)

**Назначение:** Ядро системы — обработка запросов, поиск релевантной информации и генерация ответов с использованием RAG технологии.

**Основные функции:**
- Загрузка и обработка документов (DOCX, TXT, MD)
- Разбиение документов на семантические чанки
- Генерация векторных представлений (embeddings)
- Хранение векторов в ChromaDB
- Семантический поиск релевантных фрагментов
- Генерация ответов через GigaChat LLM
- Управление конфигурацией RAG системы

**Компоненты:**

#### `rag/` — RAG Pipeline
- `rag_pipeline.py` — основной пайплайн обработки
- `document_processor.py` — обработка и разбиение документов
- `embedding_service.py` — генерация векторных представлений
- `vector_store.py` — работа с ChromaDB
- `query_processor.py` — обработка запросов пользователей
- `giga_chat.py` — интеграция с GigaChat API
- `reranker.py` — ранжирование результатов поиска
- `config.py` — конфигурация RAG системы

#### `app/` — FastAPI приложение
- `main.py` — точка входа приложения
- `api/routes/` — REST API endpoints:
  - `query.py` — обработка запросов
  - `documents.py` — управление документами
  - `config.py` — управление конфигурацией
  - `health.py` — health check
- `services/rag_service.py` — сервисный слой для RAG

**Технологии:**
- `FastAPI` — веб-фреймворк
- `ChromaDB` — векторная база данных
- `sentence-transformers` — модели для embeddings (multilingual-mpnet-base-v2)
- `gigachat` — интеграция с GigaChat LLM
- `langchain-text-splitters` — разбиение текста

---

### 3. Admin Panel Backend (`admin_panel/backend/`)

**Назначение:** Backend API для админ-панели — управление пользователями, диалогами, документами и аналитикой.

**Основные функции:**
- Управление пользователями бота
- Просмотр и управление диалогами
- Управление сообщениями
- Загрузка и управление документами базы знаний
- Настройки системы
- Аналитика и статистика
- Планировщик рассылок

**API Endpoints:**
- `/users` — управление пользователями
- `/conversations` — управление диалогами
- `/messages` — управление сообщениями
- `/documents` — управление документами
- `/settings` — настройки системы
- `/analytics` — аналитика и статистика
- `/scheduler` — планировщик рассылок

**Технологии:**
- `FastAPI` — REST API
- `asyncpg` — работа с PostgreSQL
- `aiohttp` — HTTP клиент для RAG API

---

### 4. Admin Panel Frontend (`admin_panel/frontend/`)

**Назначение:** Веб-интерфейс для администраторов системы.

**Основные функции:**
- Просмотр и управление пользователями
- Мониторинг диалогов в реальном времени
- Управление базой знаний (загрузка документов)
- Просмотр аналитики и статистики
- Настройка системы
- Управление рассылками

**Страницы:**
- `/users` — список пользователей
- `/conversations` — диалоги
- `/messages` — сообщения
- `/documents` — документы базы знаний
- `/analytics` — аналитика
- `/settings` — настройки

**Технологии:**
- `React 18` — UI библиотека
- `React Router` — маршрутизация
- `Vite` — сборщик и dev-сервер
- `Axios` — HTTP клиент
- `Recharts` — графики и визуализация
- `date-fns` — работа с датами

---

### 5. PostgreSQL Database

**Назначение:** Реляционная база данных для хранения структурированных данных.

**Хранимые данные:**
- Пользователи бота
- Диалоги и сообщения
- Метаданные документов
- Настройки системы
- Статистика и аналитика

**Технологии:**
- `PostgreSQL 16` — СУБД
- `asyncpg` — асинхронный драйвер Python

---

### 6. ChromaDB (Vector Store)

**Назначение:** Векторная база данных для хранения embeddings документов.

**Хранимые данные:**
- Векторные представления чанков документов
- Метаданные чанков (источник, позиция)
- Индексы для быстрого семантического поиска

**Технологии:**
- `ChromaDB 0.4.18` — векторная БД

## Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- Git

### Быстрый старт

1. **Клонирование репозитория:**
```bash
git clone <repository-url>
cd K1-assistent
```

2. **Создание файла `.env`:**
```bash
cp .env.example .env
# Отредактируйте .env и укажите необходимые переменные
```

3. **Запуск всех сервисов:**
```bash
docker-compose up -d
```

4. **Проверка статуса:**
```bash
docker-compose ps
```

### Переменные окружения

Основные переменные в `.env`:

```env
# PostgreSQL
DB_NAME=k1_db
DB_USER=k1_user
DB_PASSWORD=your_password
DB_HOST=postgres
DB_PORT=5432

# Telegram Bot
BOT_TOKEN=your_telegram_bot_token

# RAG API
RAG_PORT=8000
COLLECTION_NAME=k1_about
GIGACHAT_CREDENTIALS=your_gigachat_credentials

# Admin Panel
ADMIN_BACKEND_PORT=8001
ADMIN_FRONTEND_PORT=5173

# Timezone
TZ=Europe/Moscow
```

## Мониторинг и логи

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f rag_api
docker-compose logs -f telegram_bot
docker-compose logs -f admin_backend
```

### Health Checks

- RAG API: `http://localhost:8000/health`
- Admin Backend: `http://localhost:8001/docs`
- Admin Frontend: `http://localhost:5173`

## Разработка

### Структура проекта

```
K1-assistent/
├── telegram_bot/          # Telegram бот
│   ├── bot.py
│   ├── database.py
│   └── requirements.txt
├── RAG_API/               # RAG API сервис
│   ├── app/               # FastAPI приложение
│   ├── rag/               # RAG pipeline
│   └── requirements.txt
├── admin_panel/
│   ├── backend/           # Admin API
│   └── frontend/          # React приложение
├── docker-compose.yml     # Docker Compose конфигурация
└── .env                   # Переменные окружения
```

### Локальная разработка

Для разработки без Docker:

1. Установите зависимости:
```bash
cd RAG_API && pip install -r requirements.txt
cd ../telegram_bot && pip install -r requirements.txt
cd ../admin_panel/backend && pip install -r requirements.txt
cd ../frontend && npm install
```

2. Запустите PostgreSQL локально или используйте Docker:
```bash
docker-compose up -d postgres
```

3. Запустите сервисы:
```bash
# RAG API
cd RAG_API && python run.py

# Telegram Bot
cd telegram_bot && python bot.py

# Admin Backend
cd admin_panel/backend && python run.py

# Admin Frontend
cd admin_panel/frontend && npm run dev
```

## Лицензия

Проект разработан для школы программирования KiberOne.

## Контакты

Для вопросов и предложений обращайтесь к команде разработки.

---

**Версия:** 1.0.0  
**Последнее обновление:** 2024

