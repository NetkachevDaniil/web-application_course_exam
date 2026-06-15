from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.db import get_cursor, get_db
from app.decorators import roles_required
from app.utils import sanitize_markdown, sanitize_text

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/book/<int:book_id>/review/add", methods=["GET", "POST"])
@roles_required("user", "moderator", "administrator")
def add(book_id):
    cursor = get_cursor()
    cursor.execute("SELECT id, title FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    if not book:
        cursor.close()
        return redirect(url_for("main.index"))

    cursor.execute(
        "SELECT id FROM reviews WHERE book_id = %s AND user_id = %s",
        (book_id, current_user.id),
    )
    if cursor.fetchone():
        cursor.close()
        return redirect(url_for("books.view", book_id=book_id))

    cursor.close()
    form_data = {"rating": "5", "text": ""}

    if request.method == "POST":
        form_data = {
            "rating": request.form.get("rating", "5"),
            "text": sanitize_text(request.form.get("text", "")),
        }
        try:
            rating = int(form_data["rating"])
            if rating not in (0, 1, 2, 3, 4, 5):
                raise ValueError
        except (TypeError, ValueError):
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
            return render_template("review_form.html", book=book, form_data=form_data)

        if not form_data["text"].strip():
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
            return render_template("review_form.html", book=book, form_data=form_data)

        db = get_db()
        cursor = get_cursor()
        try:
            cursor.execute("SELECT id FROM review_statuses WHERE name = 'pending'")
            status = cursor.fetchone()
            cursor.execute(
                """
                INSERT INTO reviews (book_id, user_id, rating, text, status_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (book_id, current_user.id, rating, form_data["text"], status["id"]),
            )
            db.commit()
            return redirect(url_for("books.view", book_id=book_id))
        except Exception:
            db.rollback()
            flash("При сохранении данных возникла ошибка. Проверьте корректность введённых данных.", "danger")
        finally:
            cursor.close()

    return render_template("review_form.html", book=book, form_data=form_data)


@reviews_bp.route("/my-reviews")
@roles_required("user")
def my_reviews():
    cursor = get_cursor()
    cursor.execute(
        """
        SELECT r.*, b.title AS book_title, rs.name AS status_name
        FROM reviews r
        JOIN books b ON b.id = r.book_id
        JOIN review_statuses rs ON rs.id = r.status_id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
        """,
        (current_user.id,),
    )
    reviews = cursor.fetchall()
    cursor.close()

    for review in reviews:
        review["text_html"] = sanitize_markdown(review["text"])

    return render_template("my_reviews.html", reviews=reviews)
