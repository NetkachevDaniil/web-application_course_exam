import math

from flask import Blueprint, render_template, request

import config
from app.db import get_cursor, is_admin, is_admin_or_moderator

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    cursor = get_cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM books")
    total = cursor.fetchone()["cnt"]
    total_pages = max(1, math.ceil(total / config.BOOKS_PER_PAGE))
    page = max(1, min(page, total_pages))
    offset = (page - 1) * config.BOOKS_PER_PAGE

    cursor.execute(
        """
        SELECT b.*,
               GROUP_CONCAT(DISTINCT g.name ORDER BY g.name SEPARATOR ', ') AS genres,
               COALESCE(AVG(CASE WHEN rs.name = 'approved' THEN r.rating END), 0) AS avg_rating,
               COUNT(DISTINCT CASE WHEN rs.name = 'approved' THEN r.id END) AS review_count
        FROM books b
        LEFT JOIN book_genres bg ON bg.book_id = b.id
        LEFT JOIN genres g ON g.id = bg.genre_id
        LEFT JOIN reviews r ON r.book_id = b.id
        LEFT JOIN review_statuses rs ON rs.id = r.status_id
        GROUP BY b.id
        ORDER BY b.year DESC, b.id DESC
        LIMIT %s OFFSET %s
        """,
        (config.BOOKS_PER_PAGE, offset),
    )
    books = cursor.fetchall()
    cursor.close()

    for book in books:
        book["avg_rating"] = round(float(book["avg_rating"] or 0), 1)

    return render_template(
        "index.html",
        books=books,
        page=page,
        total_pages=total_pages,
        is_admin=is_admin(),
        is_admin_or_moderator=is_admin_or_moderator(),
    )
