import os
from flask import Flask, g, jsonify
from flask_cors import CORS
from .config import Settings
from .db import SessionLocal
from .routes.health import bp as health_bp
from .routes.uploads import bp as uploads_bp
from .routes.reports import bp as reports_bp
from .routes.invoices import bp as invoices_bp


def create_app() -> Flask:
    settings = Settings()  # loads from environment

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY

    # CORS: allow frontend origin (configure VITE origin in production)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # DB session lifecycle per request
    @app.before_request
    def _create_session():
        g.db = SessionLocal()

    @app.teardown_request
    def _shutdown_session(exception=None):
        db = getattr(g, "db", None)
        if db is None:
            return
        try:
            if exception is None:
                db.commit()
            else:
                db.rollback()
        finally:
            db.close()

    # Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(uploads_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")
    app.register_blueprint(invoices_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return jsonify({"status": "ok"})

    return app


# Expose an app instance for `flask --app backend.app run`
app = create_app()
