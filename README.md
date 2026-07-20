# AI API Backend & Chat Application

Полнофункциональное веб-приложение для общения с языковыми моделями (LLM) в реальном времени с поддержкой истории чатов, настройки системных промптов, аутентификации (JWT) и стриминга ответов (Server-Sent Events).

---

## 🏗 Архитектура проекта

Приложение построено по классической трехзвенной архитектуре:

```text
+-----------------------+         REST API / SSE         +------------------------+
|   Frontend (React)    | <----------------------------> |   Backend (FastAPI)    |
|   - Tailwind CSS      |                                |   - SQLAlchemy (Core/  |
|   - Vite              |                                |     ORM)               |
+-----------------------+                                +------------------------+
                                                                    |
                                                                    v
                                                        +------------------------+
                                                        |  Хранилище & Провайдер |
                                                        |  - SQLite / PostgreSQL |
                                                        |  - OpenRouter API      |
                                                        +------------------------+
```
Frontend: SPA на React с использованием Vite и Tailwind CSS
---
Реализует интерфейс управления чатами (создание, переименование, удаление), динамическое обновление системного промпта и потоковый вывод токенов (streaming).

Backend: Асинхронное REST/SSE API на базе FastAPI (Python). Отвечает за бизнес-логику, авторизацию по JWT, взаимодействие с базой данных и проксирование запросов к LLM.

База данных: Реляционное хранилище на базе SQLAlchemy с поддержкой асинхронных сессий.

LLM Провайдер: Интеграция с внешними языковыми моделями через OpenRouter API.

⚙️ Настройка конфигурации
---
Для запуска приложения необходимо настроить переменные окружения.

Скопируйте шаблон конфигурации:
```text
Bash
cp .env.template .env
```

Заполните параметры в файле .env, используя следующий образец:
---
```text
# llm settings
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=google/gemma-4-26b-a4b-it
LLM_API_KEY=super_secret_llm_api_key

# db settings
DB__FILENAME=ai_api_backend_db

# jwt settings
AUTH__JWT_SECRET=secret
AUTH__JWT_REFRESH_SECRET=refresh_secret
AUTH__JWT_EXPIRES_MIN=20
AUTH__JWT_REFRESH_EXPIRES_MIN=60

# server settings
SERVER__PORT=5055
```
🚀 Локальный запуск через Docker
---
1. Создай общую папку (например, ai_project_run) и перейди в неё в терминале.
2. Клонируй оба репозитория в эту директорию:
```text

git clone https://github.com/VadimZharsky/ai_api_backend.git
git clone https://github.com/VadimZharsky/ai_frontend.git
```
3. Создай файл docker-compose.yml на уровень выше (в корне созданной родительской папки):
```text
version: "3.9"

services:

  ai_api_backend:
    container_name: ai_api_backend
    build:
      context: ./ai_api_backend
      dockerfile: Dockerfile
    ports:
      - "5055:5055"
    command: sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 5055"
    restart: always
    env_file:
      - ./ai_api_backend/.env
    volumes:
      - .:/ai_api_backend_db/

  ai_api_frontend:
    container_name: ai_api_frontend
    build:
      context: ./ai_frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    restart: always
    depends_on:
      - ai_api_backend
```
Итоговая структура папок:
---
```text
ai_project_run/
├── ai_api_backend/     <-- репозиторий бэкенда
├── ai_frontend/        <-- репозиторий фронтенда
└── docker-compose.yml  <-- файл оркестрации
```
Запусти проект
---
```text
Bash
docker-compose up --build
```