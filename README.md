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

