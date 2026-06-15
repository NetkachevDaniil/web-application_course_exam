# Электронная библиотека

Учебный проект: АИС «Электронная библиотека» (Flask + MySQL), вариант 1 — модерация рецензий.

**Автор:** Группа 241-3211, Неткачев Даниил Евгеньевич

## Запуск (Docker + Python)

```powershell
cd D:\electronic-library
docker compose up -d
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
py init_db.py
py run.py
```

Сайт: http://127.0.0.1:5000

В `.env` для Docker: `MYSQL_PASSWORD=root`

Подробная инструкция: [DOCKER.md](DOCKER.md)

## Тестовые пользователи

| Логин | Пароль | Роль |
|-------|--------|------|
| admin | password123 | Администратор |
| moderator | password123 | Модератор |
| user1 | password123 | Пользователь |

## Структура

```
app/routes/     — страницы приложения
templates/      — HTML-шаблоны
static/         — CSS, JS, обложки
schema.sql      — структура БД
seed.sql        — начальные данные
init_db.py      — создание БД и обложек
run.py          — запуск Flask
config.py       — настройки
```

## Публикация

**GitHub Pages не подходит** — он отдаёт только статические HTML-страницы. Этот проект — серверное приложение (Python + MySQL), ему нужен хостинг с поддержкой Flask.

Для сдачи обычно указывают:
1. Ссылку на **GitHub-репозиторий** с кодом
2. Ссылку на **работающий сайт** на хостинге

Бесплатные варианты для Flask + MySQL:
- [PythonAnywhere](https://www.pythonanywhere.com/) — удобен для учебных проектов
- [Render](https://render.com/) + внешняя MySQL-база

GitHub Pages можно использовать только для страницы-описания проекта, но не для самой библиотеки.
