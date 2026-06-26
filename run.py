from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

from infrastructure.database import SmartACCTDatabaseManager, SmartACCTDatabaseConfig
from presentation.coa_routes import coa_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JSON_AS_ASCII"] = False

    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    app.db_manager = db_manager

    app.register_blueprint(coa_bp, url_prefix="/api/v1/coa")

    @app.route("/api/v1/health")
    def health():
        return {"status": "ok", "app": "SmartACCT", "version": "1.0.0"}

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
