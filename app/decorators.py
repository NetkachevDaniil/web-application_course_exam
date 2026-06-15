from functools import wraps

from flask import flash, redirect, request, url_for
from flask_login import current_user

from app.db import user_has_role


def roles_required(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Для выполнения данного действия необходимо пройти процедуру аутентификации", "warning")
                return redirect(url_for("auth.login", next=request.url))
            if not user_has_role(*role_names):
                flash("У вас недостаточно прав для выполнения данного действия", "danger")
                return redirect(url_for("main.index"))
            return f(*args, **kwargs)
        return decorated
    return decorator
