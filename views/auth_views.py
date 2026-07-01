from flask import render_template, request, redirect, url_for, session, current_app
from domain.auth import LoginRequest
from domain.common import VASValidationError

from . import views_bp


@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        try:
            from use_cases.auth import AuthUseCases
            uc = AuthUseCases(
                session_factory=current_app.db_manager.get_session,
                jwt_service=current_app.auth_jwt_service,
                casbin_service=current_app.auth_casbin_service,
                audit_service=current_app.auth_audit_service,
            )
            from infrastructure.auth import JWTService
            req = LoginRequest(username=username, password=password)
            result = uc.login(req, ip=request.remote_addr, user_agent=request.user_agent.string if request.user_agent else None)
            if result.is_success():
                data = result.get_data()
                session['user_id'] = data.get('user', {}).get('id')
                session['username'] = data.get('user', {}).get('username', username)
                session['token'] = data.get('access_token', '')
                session.modified = True
                return redirect(url_for('views.dashboard'))
        except VASValidationError:
            pass
        except Exception:
            pass
        return render_template('login.html', error='Sai tên đăng nhập hoặc mật khẩu')
    return render_template('login.html')


@views_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.login'))
