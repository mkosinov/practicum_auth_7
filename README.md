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

## Запуск проекта в контейнерах Docker
В папках присуствуют docker-compose.yaml файлы каждого из сервисов + соответствующий env.example.
/admin_panel
/auth
/movies

Все проекты объединены общим docker-compose в корневой папке.

### 1. Создать .env файлы из env.example (в папках сервисов)

### 2. Запустить проект в корневой папке:
```bash
docker compose up
```

### 3. Адреса API интерфейсов по умолчанию:
Auth - http://localhost/auth/docs/
Movies - http://localhost:8000/api/openapi/
Admin panel - http://localhost:8002/admin/


### 4. Схема проекта:

![Схема проекта](https://)
