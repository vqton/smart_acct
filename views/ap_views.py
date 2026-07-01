from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date
from . import views_bp
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from infrastructure.repositories.ap_repository import APRepository
from use_cases.ap import APUseCases
from domain.ap import VendorStatus, VendorType, VendorGroup, APInvoiceStatus


def _get_db():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager


def _get_uc():
    db = _get_db()
    return APUseCases(db.get_session())


@views_bp.route('/ap/vendors')
def ap_vendors():
    uc = _get_uc()
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    vendors = []
    try:
        v_status = None
        if status == 'active':
            v_status = VendorStatus.ACTIVE
        elif status == 'inactive':
            v_status = VendorStatus.INACTIVE
        elif status == 'suspended':
            v_status = VendorStatus.SUSPENDED

        raw = uc.list_vendors(
            search=search or None,
            status=v_status,
            limit=per_page + 1,
            offset=offset,
        )
        has_more = len(raw) > per_page
        vendors = raw[:per_page]
    except Exception as e:
        flash(f"Error loading vendors: {e}", 'danger')
        vendors = []
        has_more = False

    return render_template('ap/vendors.html',
        vendors=vendors,
        search=search,
        status=status,
        page=page,
        has_more=has_more,
    )


@views_bp.route('/ap/invoices')
def ap_invoices():
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
            inv_status = APInvoiceStatus(status)

        raw = uc.list_invoices(
            period=period or None,
            status=inv_status,
            limit=per_page + 1,
            offset=offset,
        )
        has_more = len(raw) > per_page
        invoices = raw[:per_page]
    except Exception as e:
        flash(f"Error loading AP invoices: {e}", 'danger')
        invoices = []
        has_more = False

    return render_template('ap/invoices.html',
        invoices=invoices,
        period=period,
        status=status,
        page=page,
        has_more=has_more,
    )


@views_bp.route('/ap/aging')
def ap_aging():
    uc = _get_uc()
    aging = []
    try:
        aging = uc.get_aging_report()
    except Exception as e:
        flash(f"Error generating AP aging report: {e}", 'danger')

    return render_template('ap/aging.html', aging=aging)
