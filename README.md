# Yandex Practicum. 7 sprint. Auth

# Адрес репозитория:
https://github.com/mkosinov/

# Авторы проекта:
- Косинов Максим (https://github.com/mkosinov)
- Баранов Борис (https://github.com/bormonoff)

## Описание проекта:
Монорепозиторий с объединением предыдущих спринтов в общий docker-compose

## Стек:
- Python
- Redis
- Fastapi
- Git
- Docker
- Poetry
- Pre-commit
- Pydantic
- Uvicorn
- Pytest

### 1. Запуск проекта в контейнерах Docker

#### 1. Создать .env файл из env.example (в корневой папке)

#### 2. Запустить проект в корневой папке:
```bash
docker compose up
```

#### 3. API интерфейс доступен:
Auth - http://localhost:8001/auth/docs/
Movies - http://localhost:8000/api/openapi/
Admin panel - http://localhost:8002/admin/


#### 4. Схема проекта:

![Схема проекта](https://)
