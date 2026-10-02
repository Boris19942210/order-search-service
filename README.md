# Order Search Service

Микросервис поиска заказов на **FastAPI + SQLite (FTS5)**, упакованный в Docker.

![Python](https://img.shields.io/badge/python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Что умеет

- Полнотекстовый поиск по номеру заказа и имени клиента (SQLite FTS5)
- Фильтрация по датам создания и статусу заказа
- Быстрый поиск на миллионах записей (индексы + FTS5)
- REST API + интерактивная документация Swagger UI
- Генератор тестовых данных (до 5 млн записей)
- Healthcheck контейнера

## Стек

- Python 3.10
- FastAPI, Uvicorn, Pydantic
- SQLite с расширением FTS5 и WAL-режимом
- Docker, Docker Compose

## Структура

```
order-search-service/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI приложение
│   ├── database.py        # подключение к SQLite + схема + FTS5
│   ├── models.py          # Pydantic-модели запроса/ответа
│   ├── search.py          # логика поиска через FTS5
│   └── generate_data.py   # генератор тестовых данных
├── data/                  # сюда ляжет orders.db (не в git)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Быстрый старт

### 1. Сборка образа

```bash
docker compose build
```

### 2. Генерация тестовых данных

По умолчанию — 100 000 записей. Чтобы было 5 млн, поправьте `command` в `docker-compose.yml` в секции `data-generator`.

```bash
docker compose --profile generator run --rm data-generator
```

### 3. Запуск сервиса

```bash
docker compose up -d search-service
```

### 4. Открыть в браузере

- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Stats: http://localhost:8000/stats

## API

### `GET /health`

Проверка живости сервиса.

```json
{"status": "ok"}
```

### `GET /stats`

Количество заказов в базе.

```json
{"orders_count": 100000}
```

### `POST /search`

Поиск заказов.

**Тело запроса:**

```json
{
  "query": "Иван",
  "date_from": "2024-01-01",
  "date_to": "2025-06-30",
  "status": ["delivered"],
  "limit": 50
}
```

- `query` — обязательное, минимум 1 символ
- `date_from`, `date_to` — опционально, формат `YYYY-MM-DD`
- `status` — опционально, массив статусов: `pending`, `processing`, `delivered`, `cancelled`
- `limit` — от 1 до 500

**Ответ:**

```json
{
  "results": [
    {
      "id": 12345,
      "order_number": "ORD-0000012345",
      "client_name": "Иван Петров",
      "created_at": "2024-03-15 14:23:11",
      "status": "delivered",
      "amount": 45230.55
    }
  ],
  "total": 8362,
  "took_ms": 4.27
}
```

## Остановка

```bash
docker compose down
```

Удалить базу данных:

```bash
# Windows
del data\orders.db

# Linux/macOS
rm data/orders.db
```

## Что можно улучшить

- Пагинация результатов (`offset`)
- PostgreSQL вместо SQLite для продакшена
- Кэширование частых запросов (Redis)
- Аутентификация через API-ключ
- Тесты (pytest)
- CI/CD через GitHub Actions

## Лицензия

MIT
