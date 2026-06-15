# Электронная библиотека

Группа 241-3211, Неткачев Даниил Евгеньевич  
Flask + PostgreSQL, вариант 1 (модерация рецензий)

## Локальный запуск

```powershell
docker compose up -d
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
py init_db.py
py run.py
```

http://127.0.0.1:5000

## Вход

| Логин | Пароль | Роль |
|-------|--------|------|
| admin | password123 | Администратор |
| moderator | password123 | Модератор |
| user1 | password123 | Пользователь |

## Render (бесплатно, без карты)

1. Залейте код на GitHub.
2. Render → **New** → **Blueprint** → ваш репозиторий.
3. Создастся Postgres (Free) + Web Service (Free).
4. После деплоя: Web Service → **Shell** → `python init_pa.py`.
5. Откройте URL сайта.

Бесплатная Postgres на Render живёт **90 дней**, потом нужно пересоздать БД или обновить план.
