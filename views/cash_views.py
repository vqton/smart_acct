from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date
from . import views_bp
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from infrastructure.repositories.cash_repository import CashRepository
from use_cases.cash import CashUseCases


def _get_db():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager


def _get_uc():
    db = _get_db()
    return CashUseCases(db.get_session())


@views_bp.route('/cash/receipts')
def cash_receipts():
    uc = _get_uc()
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    receipts = []
    try:
        raw = uc.list_receipts(status=status or None)
        has_more = len(raw) > per_page
        receipts = raw[:per_page]
    except Exception as e:
        flash(f"Error loading cash receipts: {e}", 'danger')
        receipts = []
        has_more = False

    return render_template('cash/receipts.html',
        receipts=receipts,
        status=status,
        page=page,
        has_more=has_more,
    )


@views_bp.route('/cash/payments')
def cash_payments():
    uc = _get_uc()
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    payments = []
    try:
        raw = uc.list_payments(status=status or None)
        has_more = len(raw) > per_page
        payments = raw[:per_page]
    except Exception as e:
        flash(f"Error loading cash payments: {e}", 'danger')
        payments = []
        has_more = False

    return render_template('cash/payments.html',
        payments=payments,
        status=status,
        page=page,
        has_more=has_more,
    )


@views_bp.route('/cash/bank')
def cash_bank():
    uc = _get_uc()
    status = request.args.get('status', '')

    accounts = []
    try:
        result = uc.list_bank_accounts(status=status or None)
        if result.is_success():
            accounts = result.get_data()
    except Exception as e:
        flash(f"Error loading bank accounts: {e}", 'danger')

    return render_template('cash/bank.html',
        accounts=accounts,
        status=status,
    )


@views_bp.route('/cash/petty')
def cash_petty():
    uc = _get_uc()
    funds = []
    advances = []
    try:
        result = uc.list_petty_cash_funds()
        if result.is_success():
            funds = result.get_data()
        advances = uc.repo.list_advances()
    except Exception as e:
        flash(f"Error loading petty cash data: {e}", 'danger')

    return render_template('cash/petty.html',
        funds=funds,
        advances=advances,
    )
