from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date, datetime
from . import views_bp
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from infrastructure.repositories.gl_repository import GLRepository
from use_cases.gl import GLUseCases
from domain import JournalType


def _get_db():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager


@views_bp.route('/gl/journal')
def gl_journal():
    db = _get_db()
    session_db = db.get_session()
    repo = GLRepository(session_db)
    period = request.args.get('period', session.get('period', ''))
    journal_type = request.args.get('journal_type', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    entries = []
    try:
        is_posted = None
        if status == 'posted':
            is_posted = True
        elif status == 'draft':
            is_posted = False

        raw = repo.list_entries(
            period=period or None,
            is_posted=is_posted,
            limit=per_page + 1,
            offset=offset,
        )
        has_more = len(raw) > per_page
        entries = raw[:per_page]
    except Exception as e:
        flash(f"Error loading journal entries: {e}", 'danger')
        entries = []

    journal_types = [jt.value for jt in JournalType]

    return render_template('gl/journal_list.html',
        entries=entries,
        period=period,
        journal_type=journal_type,
        status=status,
        search=search,
        page=page,
        has_more=has_more,
        journal_types=journal_types,
    )


@views_bp.route('/gl/ledger')
def gl_ledger():
    db = _get_db()
    session_db = db.get_session()
    repo = GLRepository(session_db)
    period = request.args.get('period', session.get('period', ''))
    account_code = request.args.get('account_code', '')

    lines = []
    account_name = ''
    try:
        if account_code and period:
            account_name = ''
            from infrastructure.models.coa_models import COAModel
            from sqlalchemy import select
            acct = session_db.execute(
                select(COAModel).where(COAModel.code == account_code)
            ).scalar_one_or_none()
            if acct:
                account_name = acct.name

            from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel
            from sqlalchemy import select, desc
            stmt = (
                select(
                    JournalEntryModel.journal_number,
                    JournalEntryModel.transaction_date,
                    JournalEntryModel.description,
                    JournalLineModel.debit,
                    JournalLineModel.credit,
                )
                .join(JournalLineModel, JournalEntryModel.id == JournalLineModel.journal_entry_id)
                .where(
                    JournalLineModel.account_id == account_code,
                    JournalEntryModel.period == period,
                    JournalEntryModel.is_posted == True,
                )
                .order_by(JournalEntryModel.transaction_date.asc(), JournalEntryModel.id.asc())
            )
            rows = session_db.execute(stmt).all()
            running = 0
            for r in rows:
                running += float(r.debit or 0) - float(r.credit or 0)
                lines.append({
                    "journal_number": r.journal_number,
                    "transaction_date": r.transaction_date,
                    "description": r.description,
                    "debit": r.debit,
                    "credit": r.credit,
                    "balance": running,
                })
    except Exception as e:
        flash(f"Error loading ledger: {e}", 'danger')

    return render_template('gl/ledger.html',
        lines=lines,
        period=period,
        account_code=account_code,
        account_name=account_name,
    )


@views_bp.route('/gl/trial-balance')
def gl_trial_balance():
    db = _get_db()
    session_db = db.get_session()
    repo = GLRepository(session_db)
    period = request.args.get('period', session.get('period', ''))

    data = None
    try:
        if period:
            data = repo.generate_trial_balance(period)
    except Exception as e:
        flash(f"Error generating trial balance: {e}", 'danger')

    return render_template('gl/trial_balance.html',
        data=data,
        period=period,
    )


@views_bp.route('/gl/periods')
def gl_periods():
    db = _get_db()
    session_db = db.get_session()
    repo = GLRepository(session_db)
    status = request.args.get('status', '')

    periods = []
    try:
        periods = repo.list_periods(status=status or None)
    except Exception as e:
        flash(f"Error loading periods: {e}", 'danger')

    return render_template('gl/periods.html',
        periods=periods,
        status=status,
    )


@views_bp.route('/gl/reports')
def gl_reports():
    return render_template('gl/fs_reports.html')
