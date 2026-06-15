import math

from flask import Blueprint, flash, redirect, render_template, request, url_for

import config
from app.db import get_cursor, get_db
from app.decorators import roles_required
from app.utils import sanitize_markdown

moderation_bp = Blueprint("moderation", __name__)


@moderation_bp.route("/moderation")
@roles_required("moderator", "administrator")
def list_pending():
    page = request.args.get("page", 1, type=int)
    cursor = get_cursor()
    cursor.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM reviews r
        JOIN review_statuses rs ON rs.id = r.status_id
        WHERE rs.name = 'pending'
        """
    )
    total = cursor.fetchone()["cnt"]
    total_pages = max(1, math.ceil(total / config.REVIEWS_PER_PAGE))
    page = max(1, min(page, total_pages))
    offset = (page - 1) * config.REVIEWS_PER_PAGE

    cursor.execute(
        """
        SELECT r.id, r.created_at, b.title AS book_title,
               u.last_name, u.first_name, u.middle_name
        FROM reviews r
        JOIN books b ON b.id = r.book_id
        JOIN users u ON u.id = r.user_id
        JOIN review_statuses rs ON rs.id = r.status_id
        WHERE rs.name = 'pending'
        ORDER BY r.created_at ASC
        LIMIT %s OFFSET %s
        """,
        (config.REVIEWS_PER_PAGE, offset),
    )
    reviews = cursor.fetchall()
    cursor.close()

    return render_template(
        "moderation_list.html",
        reviews=reviews,
        page=page,
        total_pages=total_pages,
    )


@moderation_bp.route("/moderation/<int:review_id>")
@roles_required("moderator", "administrator")
def view(review_id):
    cursor = get_cursor()
    cursor.execute(
        """
        SELECT r.*, b.title AS book_title, b.id AS book_id,
               u.last_name, u.first_name, u.middle_name,
               rs.name AS status_name
        FROM reviews r
        JOIN books b ON b.id = r.book_id
        JOIN users u ON u.id = r.user_id
        JOIN review_statuses rs ON rs.id = r.status_id
        WHERE r.id = %s
        """,
        (review_id,),
    )
    review = cursor.fetchone()
    cursor.close()

    if not review:
        return redirect(url_for("moderation.list_pending"))

    review["text_html"] = sanitize_markdown(review["text"])
    return render_template("moderation_review.html", review=review)


@moderation_bp.route("/moderation/<int:review_id>/approve", methods=["POST"])
@roles_required("moderator", "administrator")
def approve(review_id):
    return _change_status(review_id, "approved")


@moderation_bp.route("/moderation/<int:review_id>/reject", methods=["POST"])
@roles_required("moderator", "administrator")
def reject(review_id):
    return _change_status(review_id, "rejected")


def _change_status(review_id, new_status):
    db = get_db()
    cursor = get_cursor()
    try:
        cursor.execute("SELECT id FROM review_statuses WHERE name = %s", (new_status,))
        status = cursor.fetchone()
        if not status:
            flash("Статус не найден.", "danger")
            return redirect(url_for("moderation.list_pending"))

        cursor.execute(
            """
            UPDATE reviews
            SET status_id = %s
            WHERE id = %s
              AND status_id = (SELECT id FROM review_statuses WHERE name = 'pending')
            """,
            (status["id"], review_id),
        )
        if cursor.rowcount:
            db.commit()
            label = "одобрена" if new_status == "approved" else "отклонена"
            flash(f"Рецензия {label}.", "success")
        else:
            db.rollback()
            flash("Рецензия не найдена или уже рассмотрена.", "warning")
    except Exception:
        db.rollback()
        flash("Ошибка при изменении статуса рецензии.", "danger")
    finally:
        cursor.close()

    return redirect(url_for("moderation.list_pending"))
