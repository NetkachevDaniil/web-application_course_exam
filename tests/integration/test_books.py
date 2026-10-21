"""Интеграционные тесты добавления, редактирования и удаления книг."""
import io

import pytest

from cover_utils import make_cover_png
from tests.conftest import query_one

pytestmark = pytest.mark.integration


def book_form(**overrides):
    data = {
        "title": "Пикник на обочине",
        "short_description": "Повесть братьев Стругацких.",
        "year": "1972",
        "publisher": "Молодая гвардия",
        "author": "Аркадий и Борис Стругацкие",
        "pages": "224",
        "genre_ids": ["1", "8"],
    }
    data.update(overrides)
    return data


def test_admin_adds_book_with_cover(as_admin, db_conn):
    data = book_form(cover=(io.BytesIO(make_cover_png(99)), "picnic.png"))
    response = as_admin.post("/book/add", data=data, content_type="multipart/form-data")
    assert response.status_code == 302
    row = query_one(db_conn, "SELECT id, year, pages FROM books WHERE title = %s", ("Пикник на обочине",))
    assert row[1:] == (1972, 224)
    cover = query_one(db_conn, "SELECT mime_type, filename FROM covers WHERE book_id = %s", (row[0],))
    assert cover[0] == "image/png"
    assert cover[1].endswith(".png")
    genres = query_one(db_conn, "SELECT COUNT(*) FROM book_genres WHERE book_id = %s", (row[0],))
    assert genres[0] == 2


def test_add_book_with_invalid_year_is_rejected(as_admin, db_conn):
    data = book_form(year="20266", cover=(io.BytesIO(make_cover_png(5)), "c.png"))
    response = as_admin.post("/book/add", data=data, content_type="multipart/form-data")
    assert "При сохранении данных возникла ошибка" in response.get_data(as_text=True)
    assert query_one(db_conn, "SELECT COUNT(*) FROM books")[0] == 12


def test_add_book_description_is_sanitized(as_admin, db_conn):
    data = book_form(short_description="<script>alert(1)</script>Описание",
                     cover=(io.BytesIO(make_cover_png(7)), "c.png"))
    as_admin.post("/book/add", data=data, content_type="multipart/form-data")
    row = query_one(db_conn, "SELECT short_description FROM books WHERE title = %s", ("Пикник на обочине",))
    assert row[0] == "alert(1)Описание"


def test_moderator_edits_book_title(as_moderator, db_conn):
    data = book_form(title="Игра престолов (ред.)", year="1996")
    response = as_moderator.post("/book/10/edit", data=data)
    assert response.status_code == 302
    title = query_one(db_conn, "SELECT title FROM books WHERE id = 10")[0]
    assert title == "Игра престолов (ред.)"


def test_admin_deletes_book_with_reviews(as_admin, db_conn):
    response = as_admin.post("/book/1/delete", follow_redirects=True)
    assert "Запись успешно удалена" in response.get_data(as_text=True)
    assert query_one(db_conn, "SELECT COUNT(*) FROM books WHERE id = 1")[0] == 0
    assert query_one(db_conn, "SELECT COUNT(*) FROM reviews WHERE book_id = 1")[0] == 0
