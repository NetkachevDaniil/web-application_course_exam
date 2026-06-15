import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

AUTHOR_INFO = "Группа 241-3211, Неткачев Даниил Евгеньевич"

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "electronic_library")

UPLOAD_FOLDER = BASE_DIR / "static" / "uploads" / "covers"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

BOOKS_PER_PAGE = 10
REVIEWS_PER_PAGE = 10
