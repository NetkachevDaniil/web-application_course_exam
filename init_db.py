import hashlib
import struct
import sys
import zlib
from pathlib import Path

import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash

import config

BASE = Path(__file__).resolve().parent
TEST_PASSWORD = "password123"

COVER_COLORS = [
    (45, 45, 80), (80, 45, 45), (45, 80, 45),
    (80, 80, 45), (45, 80, 80), (80, 45, 80),
]

TEST_USERS = (
    ("admin", "Неткачев", "Даниил", "Евгеньевич", 1),
    ("moderator", "Модеров", "Модер", "Модерович", 2),
    ("user1", "Петров", "Пётр", "Петрович", 3),
)

TEST_REVIEWS = (
    (1, 3, 5, "**Шедевр** антиутопической литературы!\n\nОбязательно к прочтению.", 2),
    (4, 3, 4, "Отличная книга для детей и взрослых.", 1),
    (5, 3, 3, "Классический детектив, но предсказуемый.", 1),
)

TABLES = (
    "reviews",
    "covers",
    "book_genres",
    "books",
    "users",
    "genres",
    "roles",
    "review_statuses",
)


def connect():
    if config.DATABASE_URL:
        url = config.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    return psycopg2.connect(
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        dbname=config.POSTGRES_DB,
    )


def run_sql_statements(cursor, sql_text):
    lines = []
    for line in sql_text.splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    for stmt in "\n".join(lines).split(";"):
        stmt = stmt.strip()
        if stmt:
            cursor.execute(stmt)


def drop_tables(cursor):
    tables = ", ".join(TABLES)
    cursor.execute(f"DROP TABLE IF EXISTS {tables} CASCADE")


def make_png(width, height, rgb):
    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    row = bytes(rgb) * width
    raw = b"".join(b"\x00" + row for _ in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def create_users(cursor):
    password_hash = generate_password_hash(TEST_PASSWORD, method="pbkdf2:sha256")
    for login, last_name, first_name, middle_name, role_id in TEST_USERS:
        cursor.execute(
            """
            INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (login, password_hash, last_name, first_name, middle_name, role_id),
        )


def create_reviews(cursor):
    for book_id, user_id, rating, text, status_id in TEST_REVIEWS:
        cursor.execute(
            """
            INSERT INTO reviews (book_id, user_id, rating, text, status_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (book_id, user_id, rating, text, status_id),
        )


def verify_users(cursor):
    for login, *_ in TEST_USERS:
        cursor.execute(
            "SELECT password_hash FROM users WHERE login = %s",
            (login,),
        )
        row = cursor.fetchone()
        if not row or not check_password_hash(row[0], TEST_PASSWORD):
            print(f"ОШИБКА: пароль для '{login}' не установлен.")
            sys.exit(1)


def create_covers(cursor):
    cursor.execute("SELECT id FROM books ORDER BY id")
    books = cursor.fetchall()
    config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    for (book_id,) in books:
        cursor.execute("SELECT id FROM covers WHERE book_id = %s", (book_id,))
        if cursor.fetchone():
            continue
        color = COVER_COLORS[book_id % len(COVER_COLORS)]
        file_bytes = make_png(200, 300, color)
        filename = f"{book_id}.png"
        (config.UPLOAD_FOLDER / filename).write_bytes(file_bytes)
        md5_hash = hashlib.md5(file_bytes).hexdigest()
        cursor.execute(
            "INSERT INTO covers (filename, mime_type, md5_hash, book_id) VALUES (%s, %s, %s, %s)",
            (filename, "image/png", md5_hash, book_id),
        )


def init_full(cursor):
    run_sql_statements(cursor, (BASE / "schema.sql").read_text(encoding="utf-8"))
    run_sql_statements(cursor, (BASE / "seed.sql").read_text(encoding="utf-8"))
    create_users(cursor)
    create_reviews(cursor)
    verify_users(cursor)
    create_covers(cursor)


def is_initialized(cursor):
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'roles'
        )
        """
    )
    if not cursor.fetchone()[0]:
        return False
    cursor.execute("SELECT COUNT(*) FROM roles")
    return cursor.fetchone()[0] > 0


def bootstrap_if_empty():
    """Создаёт БД при первом запуске (Render Free, без Shell)."""
    try:
        conn = connect()
    except psycopg2.Error:
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT pg_advisory_lock(424242)")
        if is_initialized(cursor):
            return
        init_full(cursor)
        conn.commit()
        print("База данных инициализирована автоматически.")
    except Exception as exc:
        conn.rollback()
        print("Ошибка автоинициализации БД:", exc)
    finally:
        cursor.execute("SELECT pg_advisory_unlock(424242)")
        cursor.close()
        conn.close()


def main():
    try:
        conn = connect()
    except psycopg2.Error as exc:
        print("Ошибка подключения к PostgreSQL:", exc)
        print("Проверьте Docker и файл .env (POSTGRES_PASSWORD=postgres)")
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
