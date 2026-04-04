# SafeIncident

Простое веб-приложение для регистрации и управления инцидентами на FastAPI, SQLAlchemy, Jinja2 и Bootstrap.

## Возможности

- Просмотр списка инцидентов на главной странице
- Создание нового инцидента (`status=NEW` по умолчанию)
- Просмотр деталей инцидента
- Изменение статуса инцидента (`NEW`, `IN_PROGRESS`, `RESOLVED`, `CANCELLED`)
- Регистрация и авторизация пользователей (сессии)
- Миграции базы данных через Alembic

## Структура проекта

```text
safeincident/
backend/
    main.py
    database.py
    models.py
    schemas.py
    crud.py
    security.py
    routes/
        incidents.py

alembic/
    env.py
    script.py.mako
    versions/
        20260315_01_add_users_table.py

templates/
    base.html
    index.html
    create_incident.html
    incident_detail.html
    login.html
    register.html

static/
    style.css

alembic.ini
requirements.txt
requirements-dev.txt
Dockerfile
docker-compose.yaml
README.md
```

## Локальный запуск

1. Создайте и активируйте виртуальное окружение:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Установите зависимости:

```powershell
pip install -r requirements.txt
```

3. Выполните миграции:

```powershell
alembic upgrade head
```

4. Запустите приложение:

```powershell
uvicorn backend.main:app --reload
```

5. Откройте:

```text
http://localhost:8000
```

## Запуск через Docker Compose (PostgreSQL)

```powershell
docker compose up --build
```

Приложение: `http://localhost:8000`  
PostgreSQL: `localhost:5432` (`safeincident/safeincident`, БД `safeincident`)

## Alembic

- Текущая версия миграций:

```powershell
alembic current
```

- История миграций:

```powershell
alembic history
```

- Применить все миграции:

```powershell
alembic upgrade head
```

## Примечания

- Конфигурация БД задается через `DATABASE_URL`.
- Если `DATABASE_URL` не указан, используется SQLite: `sqlite:///./safeincident.db`.
- В Docker Compose приложение использует PostgreSQL.
