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
from presentation.ar import ar_bp
from presentation.cc import cc_bp
from presentation.inventory import inv_bp
from presentation.payroll import payroll_bp
from presentation.budget import budget_bp
from presentation.costing_center import ccost_bp
from presentation.fs import fs_bp

_start_time = time()


def _check_db(db_manager) -> dict:
    try:
        session = db_manager.get_session()
        session.execute(text("SELECT 1"))
        session.close()
        return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _get_remote_addr() -> str:
    from flask import request
    return request.remote_addr or "127.0.0.1"


def _get_user_from_jwt() -> str:
    from flask import request
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return "anonymous"
    try:
        import jwt
        token = auth[7:]
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("sub") or payload.get("username", "unknown")
    except Exception:
        return "anonymous"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JSON_AS_ASCII"] = False
    app.config["BABEL_DEFAULT_LOCALE"] = "vi"
    app.config["BABEL_DEFAULT_DOMAIN"] = "messages"
    is_debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    init_babel(app)

    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    app.db_manager = db_manager

    # ── Flask-CORS ────────────────────────────────────────────────────────
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Flask-Limiter ─────────────────────────────────────────────────────
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        app=app,
        key_func=_get_user_from_jwt,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )
    @app.route("/api/v1/health")
    @limiter.exempt
    def health():
        db_status = _check_db(app.db_manager)
        return jsonify({
            "status": "ok" if db_status["status"] == "connected" else "degraded",
            "app": "SmartACCT",
            "version": "1.0.0",
            "uptime_seconds": int(time() - _start_time),
            "database": db_status,
        })

    # ── Flask-APScheduler ─────────────────────────────────────────────────
    from flask_apscheduler import APScheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.scheduler = scheduler

    app.register_blueprint(coa_bp, url_prefix="/api/v1/coa")
    app.register_blueprint(tax_bp, url_prefix="/api/v1/tax")
    app.register_blueprint(gl_bp, url_prefix="/api/v1/gl")
    app.register_blueprint(ar_bp, url_prefix="/api/v1/ar")
    app.register_blueprint(cash_bp, url_prefix="/api/v1/cash")
    app.register_blueprint(cc_bp)
    app.register_blueprint(inv_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(budget_bp)
    from presentation.treasury import trs_bp
    app.register_blueprint(trs_bp)
    app.register_blueprint(ccost_bp)
    app.register_blueprint(fs_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if hasattr(app, "db_manager"):
            app.db_manager.close()

    # ── Flask-DebugToolbar (dev only) ─────────────────────────────────────
    if is_debug:
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)

    # ── Flask-Talisman ────────────────────────────────────────────────────
    from flask_talisman import Talisman
    Talisman(app, content_security_policy=None, force_https=False)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
