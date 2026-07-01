from flask import request
from flask_babel import Babel, gettext


babel = Babel()


def get_locale():
    """Cascade locale resolution: ?lang= → JWT locale → Accept-Language → vi."""
    from flask import current_app
    lang = request.args.get("lang")
    if lang:
        return lang

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            import jwt
            token = auth_header[7:]
            secret = current_app.config.get("JWT_SECRET_KEY") or ""
            if secret:
                payload = jwt.decode(token, secret, algorithms=["HS256"])
            else:
                payload = jwt.decode(token, options={"verify_signature": False})
            locale = payload.get("locale")
            if locale in ("vi", "en"):
                return locale
        except Exception:
            pass

    return request.accept_languages.best_match(["vi", "en"]) or "vi"


def resolve_error(error) -> str:
    """Resolve an error (VASValidationError, str, Exception) to a localized message.
    Falls back to raw msgid if Flask app context (Babel) is unavailable.
    """
    from domain import VASValidationError
    try:
        if isinstance(error, VASValidationError):
            if error.params:
                return gettext(error.msgid, **error.params)
            return gettext(error.msgid)
        return gettext(str(error))
    except Exception:
        if isinstance(error, Exception):
            return str(error)
        return str(error)


def init_app(app):
    from presentation.ap import ap_bp
    app.register_blueprint(ap_bp)
    from presentation.fa import fa_bp
    app.register_blueprint(fa_bp)
    babel.init_app(app, default_locale="vi", default_domain="messages", locale_selector=get_locale)
    app.jinja_env.globals["get_locale"] = get_locale
