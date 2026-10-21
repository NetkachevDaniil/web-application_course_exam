"""Интеграционные тесты каталога и страницы книги."""
import hashlib

import pytest

pytestmark = pytest.mark.integration


def test_index_shows_first_page_of_books(client):
    page = client.get("/").get_data(as_text=True)
    assert "Каталог книг" in page
    assert page.count("Просмотр") == 10
    assert "Горе вайбкодер и незаменимый клодик" in page


def test_index_second_page_contains_rest_of_books(client):
    page = client.get("/?page=2").get_data(as_text=True)
    assert page.count("Просмотр") == 2
    assert "Анна Каренина" in page
    assert "Преступление и наказание" in page


def test_index_shows_average_rating_of_approved_reviews(client):
    page = client.get("/").get_data(as_text=True)
    row = page.split("<td>1984</td>")[1].split("</tr>")[0]
    assert "<td>5.0</td>" in row
    assert "<td>1</td>" in row


def test_book_view_renders_markdown_description(client):
    page = client.get("/book/1").get_data(as_text=True)
    assert "<strong>Антиутопия</strong>" in page
    assert "Джордж Оруэлл" in page
    assert "Шедевр" in page


def test_book_view_unknown_book_redirects_to_index(client):
    response = client.get("/book/9999")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_cover_is_generated_when_file_is_missing(client):
    response = client.get("/covers/1.png")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert hashlib.md5(response.data, usedforsecurity=False).hexdigest() == "296f5ff741ea2c3d25fd48f6e49b78de"
