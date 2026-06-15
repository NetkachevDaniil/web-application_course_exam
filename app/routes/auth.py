from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        login_val = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.load_by_login(login_val)
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("main.index"))

        flash("Невозможно аутентифицироваться с указанными логином и паролем", "danger")
        return render_template("login.html", login_val=login_val)

    return render_template("login.html", login_val="")


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    next_page = request.args.get("next") or request.referrer
    if next_page:
        return redirect(next_page)
    return redirect(url_for("main.index"))
