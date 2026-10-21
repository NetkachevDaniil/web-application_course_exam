"""Юнит-тесты модуля app/utils.py (функции без обращения к БД)."""
import hashlib

import pytest

from app import utils


def test_sanitize_text_strips_html_tags():
    assert utils.sanitize_text("<b>Жирный</b> <script>alert(1)</script>текст") == "Жирный alert(1)текст"


def test_sanitize_text_empty_value():
    assert utils.sanitize_text("") == ""
    assert utils.sanitize_text(None) == ""


def test_sanitize_markdown_renders_bold_and_paragraphs():
    html = utils.sanitize_markdown("**Антиутопия** о тоталитарном обществе.")
    assert html == "<p><strong>Антиутопия</strong> о тоталитарном обществе.</p>"


def test_sanitize_markdown_removes_dangerous_tags():
    html = utils.sanitize_markdown("Текст <script>alert('xss')</script> <iframe src=x></iframe>")
    assert "<script>" not in html
    assert "<iframe" not in html


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("cover.png", True),
        ("cover.JPG", True),
        ("photo.jpeg", True),
        ("anim.gif", True),
        ("pic.webp", True),
        ("document.pdf", False),
        ("script.php", False),
        ("noextension", False),
    ],
)
def test_allowed_file(filename, expected):
    assert utils.allowed_file(filename) is expected


def test_compute_md5_matches_hashlib():
    data = b"electronic-library"
    assert utils.compute_md5(data) == hashlib.md5(data, usedforsecurity=False).hexdigest()
    assert len(utils.compute_md5(b"")) == 32


@pytest.mark.parametrize(
    "filename, mime",
    [
        ("a.png", "image/png"),
        ("a.JPG", "image/jpeg"),
        ("a.jpeg", "image/jpeg"),
        ("a.gif", "image/gif"),
        ("a.webp", "image/webp"),
        ("a.bin", "application/octet-stream"),
    ],
)
def test_get_mime_type(filename, mime):
    assert utils.get_mime_type(filename) == mime


@pytest.mark.parametrize(
    "rating, label",
    [(5, "отлично"), (4, "хорошо"), (3, "удовлетворительно"),
     (2, "неудовлетворительно"), (1, "плохо"), (0, "ужасно")],
)
def test_rating_label(rating, label):
    assert utils.rating_label(rating) == label


def test_status_label_known_and_unknown():
    assert utils.status_label("pending") == "На рассмотрении"
    assert utils.status_label("approved") == "Одобрена"
    assert utils.status_label("rejected") == "Отклонена"
    assert utils.status_label("archived") == "archived"


def test_full_name_with_and_without_middle_name():
    assert utils.full_name({"last_name": "Неткачев", "first_name": "Даниил",
                            "middle_name": "Евгеньевич"}) == "Неткачев Даниил Евгеньевич"
    assert utils.full_name({"last_name": "Петров", "first_name": "Пётр",
                            "middle_name": None}) == "Петров Пётр"


@pytest.mark.parametrize("value, expected", [("1949", 1949), (" 2026 ", 2026), (2001, 2001), ("868", 868)])
def test_parse_year_valid(value, expected):
    assert utils.parse_year(value) == expected


@pytest.mark.parametrize("value", ["", None, "99", "20266", "19a9", "год"])
def test_parse_year_invalid(value):
    assert utils.parse_year(value) is None


@pytest.mark.parametrize("value, expected", [("328", 328), (96, 96), ("0", None), ("-5", None),
                                             ("abc", None), ("", None)])
def test_parse_pages(value, expected):
    assert utils.parse_pages(value) == expected
