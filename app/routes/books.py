from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user

from app.db import get_cursor, get_db, is_admin_or_moderator, user_has_role
from app.decorators import roles_required
from app.utils import (
    allowed_file,
    compute_md5,
    delete_cover_file,
    get_mime_type,
    parse_pages,
    parse_year,
    sanitize_markdown,
    sanitize_text,
    save_cover_file,
)

books_bp = Blueprint("books", __name__)


def _get_genres():
    cursor = get_cursor()
    cursor.execute("SELECT id, name FROM genres ORDER BY name")
    genres = cursor.fetchall()
    cursor.close()
    return genres


def _get_book(book_id):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    if not book:
        cursor.close()
        return None, [], None

    cursor.execute(
        """
        SELECT g.id, g.name
        FROM genres g
        JOIN book_genres bg ON bg.genre_id = g.id
        WHERE bg.book_id = %s
        ORDER BY g.name
        """,
        (book_id,),
    )
    genres = cursor.fetchall()

    cursor.execute("SELECT * FROM covers WHERE book_id = %s", (book_id,))
    cover = cursor.fetchone()
    cursor.close()
    return book, genres, cover


def _set_book_genres(cursor, book_id, genre_ids):
    cursor.execute("DELETE FROM book_genres WHERE book_id = %s", (book_id,))
    for gid in genre_ids:
        cursor.execute(
            "INSERT INTO book_genres (book_id, genre_id) VALUES (%s, %s)",
            (book_id, gid),
        )


def _save_cover(cursor, book_id, file_storage):
    file_bytes = file_storage.read()
    md5_hash = compute_md5(file_bytes)
    mime_type = get_mime_type(file_storage.filename)

    cursor.execute("SELECT id, filename FROM covers WHERE md5_hash = %s", (md5_hash,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "INSERT INTO covers (filename, mime_type, md5_hash, book_id) VALUES (%s, %s, %s, %s)",
            (existing["filename"], mime_type, md5_hash, book_id),
        )
        cover_id = cursor.lastrowid
        return cover_id, existing["filename"], None

    cursor.execute(
        "INSERT INTO covers (filename, mime_type, md5_hash, book_id) VALUES (%s, %s, %s, %s)",
        ("", mime_type, md5_hash, book_id),
    )
    cover_id = cursor.lastrowid
    filename = save_cover_file(cover_id, file_bytes, file_storage.filename)
    cursor.execute("UPDATE covers SET filename = %s WHERE id = %s", (filename, cover_id))
    return cover_id, filename, file_bytes


@books_bp.route("/book/<int:book_id>")
def view(book_id):
    book, genres, cover = _get_book(book_id)
    if not book:
        return redirect(url_for("main.index"))

    cursor = get_cursor()
    cursor.execute(
        """
        SELECT r.*, u.last_name, u.first_name, u.middle_name, rs.name AS status_name
        FROM reviews r
        JOIN users u ON u.id = r.user_id
        JOIN review_statuses rs ON rs.id = r.status_id
        WHERE r.book_id = %s AND rs.name = 'approved'
        ORDER BY r.created_at DESC
        """,
        (book_id,),
    )
    reviews = cursor.fetchall()
    cursor.close()

    user_review = None
    can_write_review = False
    if current_user.is_authenticated and user_has_role("user", "moderator", "administrator"):
        cursor = get_cursor()
        cursor.execute(
            """
            SELECT r.*, rs.name AS status_name
            FROM reviews r
            JOIN review_statuses rs ON rs.id = r.status_id
            WHERE r.book_id = %s AND r.user_id = %s
            """,
            (book_id, current_user.id),
        )
        user_review = cursor.fetchone()
        cursor.close()
        can_write_review = user_review is None

    book["description_html"] = sanitize_markdown(book["short_description"])
    for review in reviews:
        review["text_html"] = sanitize_markdown(review["text"])
    if user_review:
        user_review["text_html"] = sanitize_markdown(user_review["text"])

    return render_template(
        "book_view.html",
        book=book,
        genres=genres,
        cover=cover,
        reviews=reviews,
        user_review=user_review,
        can_write_review=can_write_review,
        is_admin_or_moderator=is_admin_or_moderator(),
    )


@books_bp.route("/book/add", methods=["GET", "POST"])
@roles_required("administrator")
def add():
    genres = _get_genres()
    form_data = {
        "title": "",
        "short_description": "",
        "year": "",
        "publisher": "",
        "author": "",
        "pages": "",
        "genre_ids": [],
    }

    if request.method == "POST":
        form_data = {
            "title": request.form.get("title", "").strip(),
            "short_description": sanitize_text(request.form.get("short_description", "")),
            "year": request.form.get("year", "").strip(),
            "publisher": request.form.get("publisher", "").strip(),
            "author": request.form.get("author", "").strip(),
            "pages": request.form.get("pages", "").strip(),
            "genre_ids": [int(g) for g in request.form.getlist("genre_ids")],
        }
        cover_file = request.files.get("cover")

        year = parse_year(form_data["year"])
        pages = parse_pages(form_data["pages"])

        if not all([form_data["title"], form_data["short_description"], form_data["publisher"],
                    form_data["author"], year, pages, form_data["genre_ids"]]):
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
            return render_template(
                "book_form.html",
                genres=genres,
                form_data=form_data,
                is_edit=False,
                form_action=url_for("books.add"),
            )

        if not cover_file or not cover_file.filename or not allowed_file(cover_file.filename):
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
            return render_template(
                "book_form.html",
                genres=genres,
                form_data=form_data,
                is_edit=False,
                form_action=url_for("books.add"),
            )

        db = get_db()
        cursor = get_cursor()
        try:
            cursor.execute(
                """
                INSERT INTO books (title, short_description, year, publisher, author, pages)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    form_data["title"],
                    form_data["short_description"],
                    year,
                    form_data["publisher"],
                    form_data["author"],
                    pages,
                ),
            )
            book_id = cursor.lastrowid
            _set_book_genres(cursor, book_id, form_data["genre_ids"])
            _save_cover(cursor, book_id, cover_file)
            db.commit()
            return redirect(url_for("books.view", book_id=book_id))
        except Exception:
            db.rollback()
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
        finally:
            cursor.close()

    return render_template(
        "book_form.html",
        genres=genres,
        form_data=form_data,
        is_edit=False,
        form_action=url_for("books.add"),
    )


@books_bp.route("/book/<int:book_id>/edit", methods=["GET", "POST"])
@roles_required("administrator", "moderator")
def edit(book_id):
    book, book_genres, cover = _get_book(book_id)
    if not book:
        return redirect(url_for("main.index"))

    genres = _get_genres()
    form_data = {
        "title": book["title"],
        "short_description": book["short_description"],
        "year": str(book["year"]),
        "publisher": book["publisher"],
        "author": book["author"],
        "pages": str(book["pages"]),
        "genre_ids": [g["id"] for g in book_genres],
    }

    if request.method == "POST":
        form_data = {
            "title": request.form.get("title", "").strip(),
            "short_description": sanitize_text(request.form.get("short_description", "")),
            "year": request.form.get("year", "").strip(),
            "publisher": request.form.get("publisher", "").strip(),
            "author": request.form.get("author", "").strip(),
            "pages": request.form.get("pages", "").strip(),
            "genre_ids": [int(g) for g in request.form.getlist("genre_ids")],
        }

        year = parse_year(form_data["year"])
        pages = parse_pages(form_data["pages"])

        if not all([form_data["title"], form_data["short_description"], form_data["publisher"],
                    form_data["author"], year, pages, form_data["genre_ids"]]):
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
            return render_template(
                "book_form.html",
                genres=genres,
                form_data=form_data,
                is_edit=True,
                form_action=url_for("books.edit", book_id=book_id),
            )

        db = get_db()
        cursor = get_cursor()
        try:
            cursor.execute(
                """
                UPDATE books
                SET title = %s, short_description = %s, year = %s,
                    publisher = %s, author = %s, pages = %s
                WHERE id = %s
                """,
                (
                    form_data["title"],
                    form_data["short_description"],
                    year,
                    form_data["publisher"],
                    form_data["author"],
                    pages,
                    book_id,
                ),
            )
            _set_book_genres(cursor, book_id, form_data["genre_ids"])
            db.commit()
            return redirect(url_for("books.view", book_id=book_id))
        except Exception:
            db.rollback()
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
        finally:
            cursor.close()

    return render_template(
        "book_form.html",
        genres=genres,
        form_data=form_data,
        is_edit=True,
        form_action=url_for("books.edit", book_id=book_id),
    )


@books_bp.route("/book/<int:book_id>/delete", methods=["POST"])
@roles_required("administrator")
def delete(book_id):
    book, _, cover = _get_book(book_id)
    if not book:
        return redirect(url_for("main.index"))

    db = get_db()
    cursor = get_cursor()
    try:
        filename = cover["filename"] if cover else None
        md5_hash = cover["md5_hash"] if cover else None
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        if filename and md5_hash:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM covers WHERE md5_hash = %s",
                (md5_hash,),
            )
            remaining = cursor.fetchone()["cnt"]
            if remaining == 0:
                delete_cover_file(filename)
        db.commit()
        flash("Запись успешно удалена", "success")
    except Exception:
        db.rollback()
    finally:
        cursor.close()

    return redirect(url_for("main.index"))
