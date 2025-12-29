# app.py

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from config import Config, FLASK_ENV

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    # In development, ensure tables exist so the dev server can start without running init_db.py manually
    try:
        if FLASK_ENV == 'development':
            with app.app_context():
                db.create_all()
    except Exception:
        # If DB not reachable or create_all fails, let the app continue so errors surface in requests
        pass

    # ---------------- Blueprints ----------------
    from routes.teacher_routes import teacher_bp
    from routes.admin_routes import admin_bp
    from routes.analytics_routes import analytics_bp
    from auth import auth_bp
    from routes.subject_routes import subject_bp


    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(subject_bp)

    # ---------------- Health ----------------
    @app.route("/")
    def index():
        return {"status": "Backend running"}, 200

    return app
