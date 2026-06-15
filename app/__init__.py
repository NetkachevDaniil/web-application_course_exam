from flask import Flask
from flask_login import LoginManager

import config
from app.db import init_app as init_db
from app.models import User
from init_db import bootstrap_if_empty
from app.routes.auth import auth_bp
from app.routes.books import books_bp
from app.routes.main import main_bp
from app.routes.moderation import moderation_bp
from app.routes.reviews import reviews_bp
from app.utils import rating_label, status_label


def create_app():
    app = Flask(
        __name__,
        root_path=str(config.BASE_DIR),
        template_folder="templates",
        static_folder="static",
    )
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

    init_db(app)
    bootstrap_if_empty()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.load_by_id(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(moderation_bp)

    @app.context_processor
    def inject_globals():
        return {
            "AUTHOR_INFO": config.AUTHOR_INFO,
            "rating_label": rating_label,
            "status_label": status_label,
        }

    return app
