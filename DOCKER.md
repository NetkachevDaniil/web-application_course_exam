# Docker — краткая справка

Весь стек поднимается через Docker Compose:
приложение + PostgreSQL + автоматическая инициализация БД.

---

## Первый запуск

Из корня проекта:

```powershell
docker compose -f deployments/docker-compose.yml up -d --build
```

Статус контейнеров:

```powershell
docker compose -f deployments/docker-compose.yml ps
```

Оба сервиса должны быть `Up`. БД инициализируется автоматически при первом запуске.

Откройте: http://127.0.0.1:5000

## Ежедневный запуск

```powershell
docker compose -f deployments/docker-compose.yml up -d
```

## Остановка

```powershell
docker compose -f deployments/docker-compose.yml down
```

Данные PostgreSQL хранятся в volume `postgres_data` — при остановке не удаляются.

## Полный сброс БД

```powershell
docker compose -f deployments/docker-compose.yml down -v
docker compose -f deployments/docker-compose.yml up -d --build
```

---

## Структура

```
deployments/
├── docker-compose.yml   # сервисы postgres + web
└── Dockerfile           # образ приложения (контекст сборки — корень проекта)
schemas/
├── schema.sql           # 01 — таблицы
├── seed.sql             # 02 — жанры, книги, роли
└── seed_data.sql        # 03 — пользователи, рецензии, обложки
```

- `postgres` (postgres:16) монтирует `schemas/*.sql` в `/docker-entrypoint-initdb.d/`.
- `web` (Flask + gunicorn, `main:app`) получает БД только из внутренней сети `library-net`.
- Порт `5432` наружу не публикуется.

Значения переменных окружения задаются в `.env` в корне проекта (см. `.env.example`), иначе берутся дефолты (`POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgres`, `POSTGRES_DB=electronic_library`, `SECRET_KEY=dev-secret-key`).

## Логин

| Логин | Пароль | Роль |
|-------|--------|------|
| admin | password123 | Администратор |
| moderator | password123 | Модератор |
| user1 | password123 | Пользователь |

---

## Типичные ошибки

| Что видите | Решение |
|------------|---------|
| `Cannot connect to the Docker daemon` | Запустите Docker Desktop |
| `no such host: postgres` | Контейнер `web` запущен до `postgres` — перезапустите: `docker compose -f deployments/docker-compose.yml up -d` |
| Пустой список книг после запуска | Подождите 10-15 сек — БД инициализируется при первом старте |
| Обложки не отображаются | `docker compose -f deployments/docker-compose.yml down -v` затем `up -d --build` |