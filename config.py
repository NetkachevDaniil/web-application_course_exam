import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

AUTHOR_INFO = "Группа 241-3211, Неткачев Даниил Евгеньевич"

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

DATABASE_URL = os.environ.get("DATABASE_URL", "")

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "electronic_library")

if os.environ.get("AMVERA") == "1":
    UPLOAD_FOLDER = Path("/data/uploads/covers")
else:
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads" / "covers"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

BOOKS_PER_PAGE = 10
REVIEWS_PER_PAGE = 10
