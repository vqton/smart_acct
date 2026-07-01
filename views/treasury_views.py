from flask import render_template, request, session
from . import views_bp
from use_cases.treasury import TreasuryUseCases
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from decimal import Decimal


def _get_session():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager.get_session()


@views_bp.route('/treasury')
def treasury():
    session_db = _get_session()
    try:
        uc = TreasuryUseCases(session_db)
        position_result = uc.get_consolidated_cash_position()
        investments_result = uc.list_investments()
        loans_result = uc.list_loans()
        fx_result = uc.calculate_fx_exposure()
        ic_result = uc.list_ic_loans()

        position = position_result.get_data() if position_result and hasattr(position_result, 'get_data') and not getattr(position_result, 'is_failure', lambda: True)() else {}
        investments = investments_result.get_data() if investments_result and hasattr(investments_result, 'get_data') and not getattr(investments_result, 'is_failure', lambda: True)() else []
        loans = loans_result.get_data() if loans_result and hasattr(loans_result, 'get_data') and not getattr(loans_result, 'is_failure', lambda: True)() else []
        fx_exposures = fx_result.get_data() if fx_result and hasattr(fx_result, 'get_data') and not getattr(fx_result, 'is_failure', lambda: True)() else []
        ic_loans = ic_result.get_data() if ic_result and hasattr(ic_result, 'get_data') and not getattr(ic_result, 'is_failure', lambda: True)() else []

        if isinstance(investments, dict) and 'investments' in investments:
            investments = investments['investments']
        if isinstance(loans, dict) and 'loans' in loans:
            loans = loans['loans']
        if isinstance(ic_loans, dict) and 'ic_loans' in ic_loans:
            ic_loans = ic_loans['ic_loans']
        if isinstance(fx_exposures, dict) and 'fx_exposures' in fx_exposures:
            fx_exposures = fx_exposures['fx_exposures']

        total_cash = Decimal(str(getattr(position, 'cash_balance', position.get('cash_balance', 0)) if isinstance(position, dict) else getattr(position, 'cash_balance', 0)))
        total_deposits = Decimal(str(getattr(position, 'bank_balance', position.get('bank_balance', 0)) if isinstance(position, dict) else getattr(position, 'bank_balance', 0)))
        total_investments = sum(Decimal(str(i.get('total_cost', i.principal if hasattr(i, 'principal') else 0))) for i in investments) if investments else 0
        total_loans = sum(Decimal(str(l.get('principal', l.principal if hasattr(l, 'principal') else 0))) for l in loans) if loans else 0
        net_position = total_cash + total_deposits + total_investments - total_loans

        return render_template('treasury/dashboard.html',
            period=session.get('period'),
            total_cash=total_cash,
            total_deposits=total_deposits,
            total_investments=total_investments,
            total_loans=total_loans,
            net_position=net_position,
            investments=investments,
            loans=loans,
            fx_exposures=fx_exposures,
            ic_loans=ic_loans,
        )
    finally:
        session_db.close()
