"""Интеграционные тесты рецензий и их модерации (вариант 1 ТЗ)."""
import pytest

from tests.conftest import query_one

pytestmark = pytest.mark.integration

STATUS_SQL = """
    SELECT rs.name FROM reviews r JOIN review_statuses rs ON rs.id = r.status_id
    WHERE r.id = %s
"""


def test_user_adds_review_with_pending_status(as_user, db_conn):
    response = as_user.post("/book/2/review/add", data={"rating": "4", "text": "Сильная книга"})
    assert response.status_code == 302
    row = query_one(db_conn, """
        SELECT r.rating, rs.name FROM reviews r JOIN review_statuses rs ON rs.id = r.status_id
        WHERE r.book_id = 2 AND r.user_id = 3
    """)
    assert row == (4, "pending")
    assert "Сильная книга" not in as_user.get("/book/2").get_data(as_text=True).split("Рецензии")[1] \
        or "На рассмотрении" in as_user.get("/my-reviews").get_data(as_text=True)


def test_user_cannot_review_same_book_twice(as_user, db_conn):
    as_user.post("/book/1/review/add", data={"rating": "1", "text": "Повторная рецензия"})
    assert query_one(db_conn, "SELECT COUNT(*) FROM reviews WHERE book_id = 1 AND user_id = 3")[0] == 1


def test_review_with_invalid_rating_is_rejected(as_user, db_conn):
    response = as_user.post("/book/2/review/add", data={"rating": "7", "text": "Текст"})
    assert "При сохранении данных возникла ошибка" in response.get_data(as_text=True)
    assert query_one(db_conn, "SELECT COUNT(*) FROM reviews WHERE book_id = 2")[0] == 0


def test_my_reviews_shows_statuses(as_user):
    page = as_user.get("/my-reviews").get_data(as_text=True)
    assert "Одобрена" in page
    assert "На рассмотрении" in page


def test_moderation_list_contains_pending_reviews(as_moderator):
    page = as_moderator.get("/moderation").get_data(as_text=True)
    assert "Горе вайбкодер и незаменимый клодик" in page
    assert "Убийство в Восточном экспрессе" in page


def test_moderator_approves_review(as_moderator, db_conn, client):
    response = as_moderator.post("/moderation/2/approve", follow_redirects=True)
    assert "Рецензия одобрена." in response.get_data(as_text=True)
    assert query_one(db_conn, STATUS_SQL, (2,))[0] == "approved"
    assert "Отличная книга для детей и взрослых." in client.get("/book/4").get_data(as_text=True)


def test_moderator_rejects_review(as_moderator, db_conn):
    response = as_moderator.post("/moderation/3/reject", follow_redirects=True)
    assert "Рецензия отклонена." in response.get_data(as_text=True)
    assert query_one(db_conn, STATUS_SQL, (3,))[0] == "rejected"


def test_already_moderated_review_cannot_be_changed(as_moderator, db_conn):
    response = as_moderator.post("/moderation/1/reject", follow_redirects=True)
    assert "Рецензия не найдена или уже рассмотрена." in response.get_data(as_text=True)
    assert query_one(db_conn, STATUS_SQL, (1,))[0] == "approved"
