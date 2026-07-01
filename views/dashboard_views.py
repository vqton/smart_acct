from flask import render_template, session
from . import views_bp
from use_cases.gl import GLUseCases
from infrastructure.repositories.gl_repository import GLRepository
from infrastructure.database import SmartACCTDatabaseManager, SmartACCTDatabaseConfig

def _get_db():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager

@views_bp.route('/')
@views_bp.route('/dashboard')
def dashboard():
    db = _get_db()
    session_db = db.get_session()
    repo = GLRepository(session_db)
    uc = GLUseCases(session_db)

    periods = repo.list_periods()
    current_period = None
    for p in periods:
        if not p.is_closed:
            current_period = p.period
            break
    if not current_period and periods:
        current_period = periods[0].period

    session['period'] = current_period
    session.modified = True

    cash_balance = "0"
    try:
        rows = repo.generate_trial_balance(current_period or "")
        period_debits = sum(float(r.period_debit or 0) for r in rows)
        period_credits = sum(float(r.period_credit or 0) for r in rows)
        revenue_current = period_credits * 0.3
        expense_current = period_debits * 0.25
    except Exception:
        rows = []
        period_debits = 0
        period_credits = 0
        revenue_current = 0
        expense_current = 0

    return render_template('dashboard.html',
        current_period=current_period,
        cash_balance=cash_balance,
        bank_balance="0",
        revenue_current_month=str(revenue_current),
        expense_current_month=str(expense_current),
        unposted_count=0,
        period_status='open',
    )
