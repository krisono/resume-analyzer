from flask import Flask
from flask_cors import CORS
from .config import Settings
from .routes.analyze import analyze_bp
from .routes.report import report_bp
from .routes.auth import auth_bp
from .models.database import db
from .services.auth_service import auth_service

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB uploads

    settings = Settings()
    app.config["SETTINGS"] = settings

    # Database Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///resume_analyzer.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "your-secret-key-change-in-production"  # Change in production!
    
    # Initialize database
    db.init_app(app)
    
    # Initialize auth service
    auth_service.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(analyze_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    @app.get("/health")
    def health():
        return {
            "status": "ok", 
            "ai": {"openai_configured": bool(settings.OPENAI_API_KEY)},
            "features": {
                "core_analysis": True,
                "semantic_similarity": True,
                "authentication": True,
                "enhanced_ats": True,
                "entity_extraction": True,
                "analysis_history": True,
                "database": True
            }
        }
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")

    return app