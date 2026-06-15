from flask_login import UserMixin
from werkzeug.security import check_password_hash

from app.utils import full_name


class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.login = row["login"]
        self.last_name = row["last_name"]
        self.first_name = row["first_name"]
        self.middle_name = row.get("middle_name")
        self.role_id = row["role_id"]
        self.role_name = row["role_name"]
        self.password_hash = row.get("password_hash")

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def display_name(self):
        return full_name({
            "last_name": self.last_name,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
        })

    @staticmethod
    def load_by_id(user_id):
        from app.db import get_cursor
        cursor = get_cursor()
        cursor.execute(
            """
            SELECT u.*, r.name AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.id = %s
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        return User(row) if row else None

    @staticmethod
    def load_by_login(login):
        from app.db import get_cursor
        cursor = get_cursor()
        cursor.execute(
            """
            SELECT u.*, r.name AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.login = %s
            """,
            (login,),
        )
        row = cursor.fetchone()
        cursor.close()
        return User(row) if row else None
