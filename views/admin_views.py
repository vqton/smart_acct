from flask import render_template, request, session
from . import views_bp
from use_cases.auth import AuthUseCases
from infrastructure.auth import JWTService, CasbinEnforcerService, AuditService
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
import os


def _get_auth_uc():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    jwt_secret = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret"))
    jwt_service = JWTService(secret_key=jwt_secret)
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct")
    casbin_model = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "casbin_model.conf")
    casbin_service = CasbinEnforcerService(model_path=casbin_model, db_url=db_url)
    audit_service = AuditService(session_factory=db_manager.get_session)
    return AuthUseCases(
        session_factory=db_manager.get_session,
        jwt_service=jwt_service,
        casbin_service=casbin_service,
        audit_service=audit_service,
    )


@views_bp.route('/admin/users')
def admin_users():
    uc = _get_auth_uc()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    result = uc.list_users(offset=offset, limit=per_page)
    data = result.get_data() if result.is_success() else {"items": [], "total": 0}
    return render_template('admin/users.html',
        period=session.get('period'),
        users=data.get("items", []),
        total=data.get("total", 0),
        page=page,
        per_page=per_page,
    )


@views_bp.route('/admin/audit')
def admin_audit():
    uc = _get_auth_uc()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    user_filter = request.args.get('user_name', '')
    result = uc.get_audit_logs(offset=offset, limit=per_page)
    data = result.get_data() if result.is_success() else {"items": [], "total": 0}
    items = data.get("items", [])
    if user_filter:
        items = [i for i in items if user_filter.lower() in (i.get("username", "") or "").lower() or user_filter.lower() in (i.get("user_name", "") or "").lower()]
    return render_template('admin/audit.html',
        period=session.get('period'),
        logs=items,
        total=len(items),
        page=page,
        per_page=per_page,
        user_filter=user_filter,
    )
