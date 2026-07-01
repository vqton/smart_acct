from flask import render_template, request, redirect, url_for, jsonify
from . import views_bp
from use_cases.coa import COAUseCases
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager

def _get_uc():
    db = SmartACCTDatabaseManager(SmartACCTDatabaseConfig())
    db.initialize()
    return COAUseCases(db.get_session())

@views_bp.route('/coa')
def coa():
    uc = _get_uc()
    accounts = uc.list_accounts()
    return render_template('coa/list.html', accounts=accounts)
