from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date
from . import views_bp
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from infrastructure.repositories.ar_repository import ARRepository
from use_cases.ar import ARUseCases
from domain import CustomerStatus, CustomerType, CustomerGroup, ARInvoiceStatus


def _get_db():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager


def _get_uc():
    db = _get_db()
    return ARUseCases(db.get_session())


@views_bp.route('/ar/customers')
def ar_customers():
    uc = _get_uc()
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    customers = []
    try:
        cust_status = None
        if status == 'active':
            cust_status = CustomerStatus.ACTIVE
        elif status == 'inactive':
            cust_status = CustomerStatus.INACTIVE
        elif status == 'suspended':
            cust_status = CustomerStatus.SUSPENDED

        raw = uc.list_customers(
            search=search or None,
            status=cust_status,
            limit=per_page + 1,
            offset=offset,
        )
        has_more = len(raw) > per_page
        customers = raw[:per_page]
    except Exception as e:
        flash(f"Error loading customers: {e}", 'danger')
        customers = []
        has_more = False

    return render_template('ar/customers.html',
        customers=customers,
        search=search,
        status=status,
        page=page,
        has_more=has_more,
    )


@views_bp.route('/ar/invoices')
def ar_invoices():
    uc = _get_uc()
    period = request.args.get('period', session.get('period', ''))
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    invoices = []
    try:
        inv_status = None
        if status:
            inv_status = ARInvoiceStatus(status)

        raw = uc.list_invoices(
            period=period or None,
            status=inv_status,
            limit=per_page + 1,
            offset=offset,
        )
        has_more = len(raw) > per_page
        invoices = raw[:per_page]
    except Exception as e:
        flash(f"Error loading invoices: {e}", 'danger')
        invoices = []
        has_more = False

    return render_template('ar/invoices.html',
        invoices=invoices,
        period=period,
        status=status,
        page=page,
        has_more=has_more,
    )


@views_bp.route('/ar/aging')
def ar_aging():
    uc = _get_uc()
    aging = []
    try:
        aging = uc.get_aging_report()
    except Exception as e:
        flash(f"Error generating aging report: {e}", 'danger')

    return render_template('ar/aging.html', aging=aging)
