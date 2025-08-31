from flask import Flask
from flask_cors import CORS
from .config import Settings
from .routes.analyze import analyze_bp
from .routes.report import report_bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB uploads

    settings = Settings()
    app.config["SETTINGS"] = settings

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(analyze_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok", "ai": {"openai_configured": bool(settings.OPENAI_API_KEY)}}

    return app