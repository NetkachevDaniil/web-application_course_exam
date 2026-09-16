# Электронная библиотека
Flask + PostgreSQL, модерация рецензий 

## Запуск

```powershell
docker compose -f deployments/docker-compose.yml up -d --build
```

При первом запуске база данных инициализируется автоматически (схема, тестовые данные, пользователи, обложки).

http://127.0.0.1:5000

## Остановка

```powershell
docker compose -f deployments/docker-compose.yml down
```

Данные сохраняются в volume `postgres_data`. Для полного сброса:

```powershell
docker compose -f deployments/docker-compose.yml down -v
docker compose -f deployments/docker-compose.yml up -d --build
```

## Переменные окружения

Задайте в файле `.env` в корне проекта (скопируйте из `.env.example`):

| Переменная | По умолчанию |
|-----------|--------------|
| POSTGRES_USER | postgres |
| POSTGRES_PASSWORD | postgres |
| POSTGRES_DB | electronic_library |
| SECRET_KEY | dev-secret-key |

> Не меняйте `POSTGRES_HOST` и `POSTGRES_PORT` — внутри compose это сервис `postgres` на порту `5432`.

## Логин

| Логин | Пароль | Роль |
|-------|--------|------|
| admin | password123 | Администратор |
| moderator | password123 | Модератор |
| user1 | password123 | Пользователь |
