# ASYNC_API_sprint_2
# Функциональные тесты

# Адрес репозитория:
https://github.com/mkosinov/Async_API_sprint_2

# Авторы проекта:
- Гельруд Борис (https://github.com/Izrekatel/)
- Косинов Максим (https://github.com/mkosinov)
- Холкин Сергей (https://github.com/Khosep)

## Описание проекта:
"Функциональные тесты" - автоматические тесты проекта ASYNC_API для
онлайн-кинотеатра учебного проекта Яндекс.Практикум.
Тесты создают собственные контейнеры Elasticsearch и Redis в которых проводят
проерку корректности работы API. Использована библиотека pytest.
Проект организован в docker-compose.

## Стек:
- Python
- Elasticsearch
- Redis
- Fastapi
- Git
- Docker
- Poetry
- Pre-commit
- Pydantic
- Uvicorn
- Pytest
- aiohttp

### 1. Запуск проекта в контейнерах Docker

#### 1. Создать .env файл из env.example (в корневой папке)

### 2. Войти в папку tests
```bash
cd tests
```
#### 3. Запустить Docker


#### 4. Поднимаем контейнеры:
```bash
docker compose up --abort-on-container-exit --exit-code-from tests
```

#### 5. Инфраструктура тестов:

![Инфраструктура тестов](https://pictures.s3.yandex.net/resources/S1.1_5_Functional_tests_1_1628098672.jpg)

### 2. Установка для локальной разработки

1. Установите Poetry

Для Linux, macOS, Windows (WSL):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Для Windows (Powershell):
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
Чтобы скрипты выполнялись, PowerShell может попросить у вас поменять политики.

В macOS и Windows сценарий установки предложит добавить папку с исполняемым файлом poetry в переменную PATH. Сделайте это, выполнив следующую команду:

macOS (не забудьте поменять borisgelrud на имя вашего пользователя)
```bash
export PATH="/Users/borisgelrud/.local/bin:$PATH"
```

Windows
```bash
$Env:Path += ";C:\Users\borisgelrud\AppData\Roaming\Python\Scripts"; setx PATH "$Env:Path"
```

Для проверки установки выполните следующую команду:
```bash
poetry --version
```
Опционально! Изменить местонахождение окружения в папке проекта
```bash
poetry config virtualenvs.in-project true
```

Установка автодополнений bash (опцонально)
```bash
poetry completions bash >> ~/.bash_completion
```

Создание виртуально окружения
```bash
poetry env use python3.11
```

2. Установите виртуальное окружение
Важно: poetry ставится и запускается для каждого сервиса отдельно.

Перейти в одну из папок сервиса, например:
```bash
cd tests
```

Установка зависимостей (для разработки)
```bash
poetry install
```

Запуск оболочки и активация виртуального окружения

```bash
your@device:~/your_project_pwd/your_service$ poetry shell
```

Проверка активации виртуального окружения
```bash
poetry env list
```


* Полная документация: https://python-poetry.org/docs/#installation
* Настройка для pycharm: https://www.jetbrains.com/help/pycharm/poetry.html


3. Установка pre-commit

Модуль pre-commit уже добавлен в lock, таким образом после настройки виртуального окружения, должен установится автоматически.
Проверить установку pre-commit можно командой (при активированном виртуальном окружении):
```bash
pre-commit --version
```

Если pre-commit не найден, то его нужно установить по документации https://pre-commit.com/#install

```bash
poetry add pre-commit
```

4. Установка hook

Установка осуществляется hook командой
```bash
pre-commit install --all
```

В дальнейшем при выполнении команды `git commit` будут выполняться проверки перечисленные в файле `.pre-commit-config.yaml`.
