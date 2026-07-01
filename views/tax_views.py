from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date
from . import views_bp
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from infrastructure.repositories.tax_repository import TaxRepository
from use_cases.tax import TaxUseCases
from domain import TaxType, DeclarationStatus, InvoiceStatus


def _get_db():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager


def _get_uc():
    db = _get_db()
    return TaxUseCases(db.get_session())


@views_bp.route('/tax/vat')
def tax_vat():
    uc = _get_uc()
    tax_type = request.args.get('tax_type', '')
    status = request.args.get('status', '')
    period = request.args.get('period', '')

    declarations = []
    try:
        tt = None
        if tax_type == 'vat_deduction':
            tt = TaxType.VAT_DEDUCTION
        elif tax_type == 'vat_direct':
            tt = TaxType.VAT_DIRECT

        st = None
        if status == 'draft':
            st = DeclarationStatus.DRAFT
        elif status == 'submitted':
            st = DeclarationStatus.SUBMITTED
        elif status == 'accepted':
            st = DeclarationStatus.ACCEPTED
        elif status == 'rejected':
            st = DeclarationStatus.REJECTED

        declarations = uc.list_declarations(
            tax_type=tt,
            status=st,
            declaration_type=None,
        )
    except Exception as e:
        flash(f"Error loading VAT declarations: {e}", 'danger')

    return render_template('tax/vat.html',
        declarations=declarations,
        tax_type=tax_type,
        status=status,
        period=period,
    )


@views_bp.route('/tax/einvoice')
def tax_einvoice():
    uc = _get_uc()
    status = request.args.get('status', '')

    invoices = []
    try:
        st = None
        if status == 'draft':
            st = InvoiceStatus.DRAFT
        elif status == 'issued':
            st = InvoiceStatus.ISSUED
        elif status == 'cancelled':
            st = InvoiceStatus.CANCELLED

        invoices = uc.list_invoices(status=st)
    except Exception as e:
        flash(f"Error loading e-invoices: {e}", 'danger')

    return render_template('tax/einvoice.html',
        invoices=invoices,
        status=status,
    )
