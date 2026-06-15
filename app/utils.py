import hashlib
import re

import bleach
import markdown
from werkzeug.utils import secure_filename

import config

# Теги, которые разрешены при выводе HTML
ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS | {
    "p", "br", "h1", "h2", "h3", "h4", "h5", "h6",
    "pre", "code", "blockquote", "hr", "img",
    "table", "thead", "tbody", "tr", "th", "td",
})

ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "img": ["src", "alt", "title"],
    "a": ["href", "title", "rel"],
}


def sanitize_text(text):
    """Очистка текста перед сохранением в БД (по заданию — через Bleach)."""
    if not text:
        return ""
    return bleach.clean(text, tags=[], attributes={}, strip=True)


def sanitize_markdown(text):
    """Markdown -> HTML + очистка опасных тегов для вывода на странице."""
    if not text:
        return ""
    html = markdown.markdown(text, extensions=["extra", "nl2br"])
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS


def compute_md5(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()


def get_mime_type(filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    return types.get(ext, "application/octet-stream")


def save_cover_file(cover_id, file_bytes, original_filename):
    config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    ext = secure_filename(original_filename).rsplit(".", 1)[-1].lower()
    filename = f"{cover_id}.{ext}"
    filepath = config.UPLOAD_FOLDER / filename
    filepath.write_bytes(file_bytes)
    return filename


def delete_cover_file(filename):
    if not filename:
        return
    filepath = config.UPLOAD_FOLDER / filename
    if filepath.exists():
        filepath.unlink()


def rating_label(rating):
    labels = {
        5: "отлично",
        4: "хорошо",
        3: "удовлетворительно",
        2: "неудовлетворительно",
        1: "плохо",
        0: "ужасно",
    }
    return labels.get(int(rating), str(rating))


def status_label(status_name):
    labels = {
        "pending": "На рассмотрении",
        "approved": "Одобрена",
        "rejected": "Отклонена",
    }
    return labels.get(status_name, status_name)


def full_name(user):
    parts = [user.get("last_name", ""), user.get("first_name", "")]
    if user.get("middle_name"):
        parts.append(user["middle_name"])
    return " ".join(p for p in parts if p)


def parse_year(value):
    if not value:
        return None
    value = str(value).strip()
    if re.match(r"^\d{4}$", value):
        return int(value)
    return None


def parse_pages(value):
    if not value:
        return None
    try:
        pages = int(value)
        return pages if pages > 0 else None
    except (TypeError, ValueError):
        return None
