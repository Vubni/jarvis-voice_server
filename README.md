# Jarvis Voice Assistant (Серверная часть)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![aiohttp](https://img.shields.io/badge/aiohttp-Async%20HTTP-2C5FAA?logo=aiohttp&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

Серверная часть голосового ассистента Jarvis, предоставляющая REST API для обработки голосовых команд, управления пользователями и интеграции с AI-моделями.

## Описание

Сервер обрабатывает запросы от клиентского приложения (C++/Qt6), выполняет следующие функции:

1. **Аутентификация и авторизация** — регистрация, вход, управление токенами доступа
2. **Обработка команд** — анализ голосовых команд через OpenAI API и генерация ответов
3. **Управление сессиями** — создание персональных сессий для каждого пользователя
4. **Кэширование команд** — сохранение часто используемых команд для ускорения работы
5. **Отправка email** — уведомления пользователей (восстановление пароля и т.д.)

## Структура проекта

```
server/
├── server.py              # Главный файл запуска сервера
├── config.py              # Конфигурация (переменные окружения, логирование)
├── core.py                # Основные утилиты (авторизация, валидация)
├── requirements.txt       # Зависимости Python
│
├── api/                   # API эндпоинты
│   ├── auth.py           # Аутентификация (регистрация, вход, восстановление пароля)
│   ├── profile.py        # Профиль пользователя
│   ├── commands.py       # Обработка команд
│   └── validate.py       # Валидация запросов
│
├── ai/                    # Интеграция с AI
│   ├── ai.py             # Класс для работы с OpenAI API
│   └── prompts.py        # Промпты для AI-моделей
│
├── database/              # Работа с базой данных
│   ├── database.py       # Класс для подключения к PostgreSQL
│   └── functions.py      # Функции работы с БД
│
├── functions/             # Бизнес-логика
│   ├── commands.py       # Обработка команд пользователя
│   ├── profile.py        # Логика работы с профилем
│   └── mail.py           # Отправка email
│
├── docs/                  # Документация API
│   └── schems.py         # Схемы для Swagger
│
├── data/                  # Шаблоны и статические файлы
│   └── edit_password.html # HTML-шаблон для восстановления пароля
│
└── logs/                  # Логи приложения
    ├── all_logs.log      # Все логи
    └── errors.log        # Только ошибки
```

## Технологии

- **Python 3.8+** — основной язык
- **aiohttp** — асинхронный HTTP-сервер
- **PostgreSQL** — база данных
- **OpenAI API** — обработка естественного языка
- **asyncpg** — асинхронный драйвер для PostgreSQL
- **aiosmtplib** — асинхронная отправка email
- **pydantic** — валидация данных
- **aiohttp-apispec** — Swagger документация

## Установка и настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# OpenAI API
API_KEY=your_openai_api_key_here

# База данных PostgreSQL
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_DB=your_db_name

# Email для отправки уведомлений
EMAIL_HOSTNAME=smtp.example.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_password

# Настройки сервера (опционально)
INSTANCE_HOST=localhost
PORT=8080
```

**ВАЖНО:** Файл `.env` уже добавлен в `.gitignore` и не будет попадать в репозиторий.

### 3. Настройка базы данных

Убедитесь, что PostgreSQL запущен и создана база данных:

```sql
CREATE DATABASE jarvis;
```

База данных инициализируется автоматически при первом запуске сервера.

### 4. Запуск сервера

```bash
python server.py
```

Сервер будет доступен по адресу `http://localhost:8080` (или по указанному в переменных окружения).

## API Endpoints

### Аутентификация

- `POST /auth/register` — регистрация нового пользователя
- `POST /auth/auth` — авторизация (получение токена)
- `POST /auth/forgot_password` — запрос на восстановление пароля
- `GET /auth/forgot_password/confirm?confirm={code}` — подтверждение смены пароля

### Профиль

- `GET /profile/info` — получение информации о профиле (требует авторизации)
- `POST /profile/check_token` — проверка активности токена (требует авторизации)

### Команды

- `POST /commands/create_session` — создание сессии для пользователя (требует авторизации)
- `POST /commands/command_processing` — обработка голосовой команды (требует авторизации)
- `POST /commands/clear_cache` — очистка кэша команд (требует авторизации)

### Документация API

Swagger документация доступна по адресу: `http://localhost:8080/doc`

## Безопасность

✅ **Проверено на утечки ключей доступа:**

1. Все секретные ключи (API_KEY, пароли БД, email пароли) загружаются из переменных окружения
2. Пароли и токены не попадают в ответы об ошибках валидации
3. Чувствительные данные не логируются
4. Используется Bearer токен авторизация
5. Токены автоматически удаляются через месяц неактивности

## Работа с API

### Пример регистрации

```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "login": "username",
    "password": "secure_password"
  }'
```

### Пример авторизации

```bash
curl -X POST http://localhost:8080/auth/auth \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "password": "secure_password"
  }'
```

Ответ:
```json
{
  "token": "your_bearer_token_here"
}
```

### Пример обработки команды

```bash
curl -X POST http://localhost:8080/commands/command_processing \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_bearer_token_here" \
  -d '{
    "text_ru": "Джарвис, открой браузер",
    "text_en": "Jarvis, open browser",
    "save_cache": true
  }'
```

## Логирование

Логи сохраняются в директории `logs/`:
- `all_logs.log` — все события (ротация при достижении 5MB)
- `errors.log` — только ошибки (ротация при достижении 5MB)

Логи автоматически ротируются, сохраняется до 3 резервных копий.

## Особенности реализации

- **Асинхронность** — все операции выполняются асинхронно для высокой производительности
- **Автоматическое переподключение к БД** — до 30 попыток с задержкой 1 секунда
- **Кэширование команд** — часто используемые команды сохраняются в БД для ускорения
- **Валидация email** — проверка через DNS MX записи
- **CORS** — поддержка кросс-доменных запросов
- **Swagger** — автоматическая генерация API документации

## Требования

- Python 3.8 или выше
- PostgreSQL 12 или выше
- Доступ к интернету (для OpenAI API и отправки email)

## Планируемые улучшения

- Система подписок
- Расширенная аналитика использования
- Поддержка нескольких языков
- WebSocket для real-time обновлений
- Rate limiting для защиты от злоупотреблений

## Лицензия

MIT License
