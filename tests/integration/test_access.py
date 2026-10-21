"""Интеграционные тесты разграничения прав доступа (декоратор roles_required)."""
import pytest

pytestmark = pytest.mark.integration


def test_guest_is_redirected_to_login_on_add_book(client):
    response = client.get("/book/add", follow_redirects=True)
    page = response.get_data(as_text=True)
    assert "== ВХОД ==" in page
    assert "необходимо пройти процедуру аутентификации" in page


def test_user_cannot_edit_book(as_user):
    response = as_user.get("/book/1/edit", follow_redirects=True)
    assert "У вас недостаточно прав для выполнения данного действия" in response.get_data(as_text=True)


def test_user_cannot_open_moderation(as_user):
    response = as_user.get("/moderation", follow_redirects=True)
    assert "недостаточно прав" in response.get_data(as_text=True)


def test_moderator_cannot_delete_book(as_moderator, db_conn):
    as_moderator.post("/book/1/delete")
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM books WHERE id = 1")
        assert cur.fetchone()[0] == 1


def test_admin_sees_management_buttons(as_admin):
    page = as_admin.get("/").get_data(as_text=True)
    assert "Редактирование" in page
    assert "Удалить" in page
    assert "+ Добавить книгу" in page
