from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from time import time
from sqlalchemy import text

load_dotenv()

from infrastructure.database import SmartACCTDatabaseManager, SmartACCTDatabaseConfig
from presentation import init_app as init_babel
from presentation.coa_routes import coa_bp
from presentation.tax_routes import tax_bp
from presentation.gl_routes import gl_bp
from presentation.cash_routes import cash_bp

_start_time = time()


def _check_db(db_manager) -> dict:
    try:
        session = db_manager.get_session()
        session.execute(text("SELECT 1"))
        session.close()
        return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JSON_AS_ASCII"] = False
    app.config["BABEL_DEFAULT_LOCALE"] = "vi"
    app.config["BABEL_DEFAULT_DOMAIN"] = "messages"

    init_babel(app)

    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    app.db_manager = db_manager

    app.register_blueprint(coa_bp, url_prefix="/api/v1/coa")
    app.register_blueprint(tax_bp, url_prefix="/api/v1/tax")
    app.register_blueprint(gl_bp, url_prefix="/api/v1/gl")
    app.register_blueprint(cash_bp, url_prefix="/api/v1/cash")

    @app.route("/api/v1/health")
    def health():
        db_status = _check_db(app.db_manager)
        return jsonify({
            "status": "ok" if db_status["status"] == "connected" else "degraded",
            "app": "SmartACCT",
            "version": "1.0.0",
            "uptime_seconds": int(time() - _start_time),
            "database": db_status,
        })

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if hasattr(app, "db_manager"):
            app.db_manager.close()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
