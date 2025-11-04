import os
import sys, traceback, logging
import re
from datetime import timedelta
from flask import Flask, jsonify, send_from_directory, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import logging
from pythonjsonlogger import jsonlogger
from sqlalchemy import inspect  # NEW: for table introspection
from src.routes.notify_test import bp as notify_test_bp

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import models (ensure these are imported BEFORE create_all)
from src.models.user import User, InvestorData, db
from src.models.document import Document
from src.models.announcement import Announcement
from src.models.support import SupportRequest, SupportMessage
from src.models.admin import Admin, AdminSession
from src.models.magic_link import MagicLinkToken

# Import routes
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.investor import investor_bp
from src.routes.documents_simple import documents_bp
from src.routes.announcements import announcements_bp
from src.routes.support import support_bp
from src.routes.admin_auth import admin_auth_bp
from src.routes.admin_clients import admin_clients_bp
from src.routes.admin_compliance import admin_compliance_bp
from src.routes.admin_reports import admin_reports_bp
from src.routes.admin_setup import admin_setup_bp
from src.routes.admin_notifications import bp as notify_bp
from src.routes.health_email import bp as health_email_bp
from src.routes.health_email_dry import bp as health_email_dry_bp


def create_app():

    # Load environment variables
    load_dotenv()

    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))

    # Structured JSON logging
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # ------------------------ Core config ------------------------
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secretkey-change-in-production")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    # ------------------------ Database config ------------------------
    database_url = os.getenv("DATABASE_URL")

    # NEW: normalize scheme for SQLAlchemy if Render gives postgres://
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url:
        # Use PostgreSQL on Render
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        # Add SSL mode if not present
        if "sslmode=" not in database_url:
            sep = "&" if "?" in database_url else "?"
            app.config["SQLALCHEMY_DATABASE_URI"] = f"{database_url}{sep}sslmode=require"
    else:
        # Use SQLite for local development
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Database engine options for production
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 300,
    }
    
    # Add connect_args only for PostgreSQL
    if database_url:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"]["connect_args"] = {"sslmode": "require"}

    # Email configuration (for Flask-Mail compatibility, though we use SendGrid)
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

    # Init extensions
    db.init_app(app)
    JWTManager(app)
    Mail(app)

    # ------------------------ CORS (prod-ready) ------------------------
    allowed = os.getenv("CORS_ALLOWED_ORIGINS")
    if allowed:
        ALLOWED_ORIGINS = [o.strip() for o in allowed.split(",") if o.strip()]
    else:
        ALLOWED_ORIGINS = [
            "https://quantumgrowthinvestments.com",
            "https://www.quantumgrowthinvestments.com",
            "https://qgi.capital",
            "https://www.qgi.capital",
            "https://admin.quantumgrowthinvestments.com",
            "https://portal.quantumgrowthinvestments.com",
            "https://qgi-admin-qgi-admins-projects.onrender.com",  # Render admin URL
            "http://localhost:5173",  # Added for local development
            "http://localhost:5174",  # Admin local development
            "http://localhost:3000",  # Added for local development
        ]

    CORS(
        app,
        resources={r"/*": {
            "origins": ALLOWED_ORIGINS,
            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "expose_headers": ["Content-Type", "Authorization"]
        }},
    )

    # Handle OPTIONS preflights quickly
    @app.before_request
    def _cors_preflight():
        if request.method == "OPTIONS":
            resp = make_response("", 204)
            origin = request.headers.get('Origin')
            if origin in ALLOWED_ORIGINS:
                resp.headers['Access-Control-Allow-Origin'] = origin
                resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
                resp.headers['Access-Control-Allow-Credentials'] = 'true'
            return resp

    # ------------------------ Health & root (define early) ------------------------
    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy", "service": "qgi-backend"})

    @app.route("/")
    def root():
        return jsonify({"message": "QGI Backend API", "status": "running"})

    # ------------------------ Blueprints ------------------------
    app.register_blueprint(notify_bp)                         # admin notifications utility
    app.register_blueprint(notify_test_bp)                    # test endpoints
    app.register_blueprint(health_email_bp)                   # GET /health/email
    app.register_blueprint(health_email_dry_bp)               # GET /health/email/dry
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(investor_bp, url_prefix="/api/investor")
    app.register_blueprint(documents_bp, url_prefix="/api/documents")
    app.register_blueprint(announcements_bp, url_prefix="/api/announcements")
    app.register_blueprint(support_bp, url_prefix="/api/support")
    
    # Admin routes
    app.register_blueprint(admin_auth_bp, url_prefix="/api/admin/auth")
    app.register_blueprint(admin_clients_bp, url_prefix="/api/admin")
    app.register_blueprint(admin_compliance_bp, url_prefix="/api/admin")
    app.register_blueprint(admin_reports_bp, url_prefix="/api/admin")
    app.register_blueprint(admin_setup_bp, url_prefix="/api/admin")

    # ------------------------ Optional static serving (dev only) ------------------------
    if os.getenv("SERVE_STATIC_FROM_API") == "1":
        @app.route("/static/<path:filename>")
        def static_files(filename):
            static_folder_path = app.static_folder
            if static_folder_path and os.path.exists(os.path.join(static_folder_path, filename)):
                return send_from_directory(static_folder_path, filename)
            return jsonify({"error": "Not found", "path": f"/static/{filename}"}), 404

        @app.route("/app", defaults={"path": ""})
        @app.route("/app/<path:path>")
        def serve_app(path):
            index_path = os.path.join(app.static_folder or "", "index.html")
            if os.path.exists(index_path):
                return send_from_directory(app.static_folder, "index.html")
            return jsonify({"message": "QGI Backend API", "status": "running"})

    # ------------------------ API 404 handler ------------------------
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "path": request.path}), 404

    # ------------------------ DB init + visibility logs ------------------------
    with app.app_context():
        print("DB URL in use:", app.config["SQLALCHEMY_DATABASE_URI"])
        try:
            before_tables = inspect(db.engine).get_table_names()
        except Exception as e:
            before_tables = [f"(inspect error: {e})"]
        print("Tables BEFORE create_all():", before_tables)

        db.create_all()

        try:
            after_tables = inspect(db.engine).get_table_names()
        except Exception as e:
            after_tables = [f"(inspect error: {e})"]
        print("Tables AFTER create_all():", after_tables)
        
        # Auto-fix admin permissions on startup
        try:
            from src.utils.auto_fix_permissions import auto_fix_admin_permissions
            auto_fix_admin_permissions(app)
        except Exception as e:
            print(f"Warning: Could not auto-fix admin permissions: {e}")

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5001))
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"  # set FLASK_DEBUG=1 locally if needed
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

