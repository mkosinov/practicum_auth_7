# проектное задание - перенос данных из sqlite3 в postgres

Содержимое .env файла:
- BATCH_SIZE - количество строк для чтения из sqlite3
- DB_PATH - путь к БД sqlite3
Далее настройки подключения к Postrges:
- DB_NAME - название БД
- DB_USER - пользователь
- DB_PASSWORD - пароль пользователя
- DB_HOST - адрес
- DB_PORT - порт
- DB_SCHEMA - название схемы с таблицами

load_data.py - основной скрипт переноса данных
transferDC.py - содержит объявление датаклассов
/tests/check_consistency/tests.py - тесты результата переноса данных