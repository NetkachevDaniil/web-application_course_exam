"""Инициализация БД на хостинге (Render и т.п.) — только таблицы, без DROP DATABASE."""
import sys

import psycopg2

from init_db import BASE, connect, drop_tables, init_full


def main():
    try:
        conn = connect()
    except psycopg2.Error as exc:
        print("Ошибка подключения к PostgreSQL:", exc)
        print("Проверьте DATABASE_URL или переменные POSTGRES_*")
        sys.exit(1)

    cursor = conn.cursor()
    drop_tables(cursor)
    init_full(cursor)
    conn.commit()
    cursor.close()
    conn.close()
    print("База данных создана.")
    print("Логины: admin, moderator, user1 | пароль: password123")


if __name__ == "__main__":
    main()
