"""Инициализация БД на хостинге (Render и т.п.) — только таблицы, без DROP DATABASE."""
import sys

import psycopg2

from init_db import (
    BASE,
    connect,
    create_covers,
    create_reviews,
    create_users,
    drop_tables,
    run_sql_statements,
    verify_users,
)


def main():
    try:
        conn = connect()
    except psycopg2.Error as exc:
        print("Ошибка подключения к PostgreSQL:", exc)
        print("Проверьте DATABASE_URL или переменные POSTGRES_*")
        sys.exit(1)

    cursor = conn.cursor()
    drop_tables(cursor)
    run_sql_statements(cursor, (BASE / "schema.sql").read_text(encoding="utf-8"))
    run_sql_statements(cursor, (BASE / "seed.sql").read_text(encoding="utf-8"))
    create_users(cursor)
    create_reviews(cursor)
    verify_users(cursor)
    create_covers(cursor)
    conn.commit()
    cursor.close()
    conn.close()
    print("База данных создана.")
    print("Логины: admin, moderator, user1 | пароль: password123")


if __name__ == "__main__":
    main()
