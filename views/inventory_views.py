from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date
from . import views_bp
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from infrastructure.repositories.inventory_repository import InventoryRepository
from use_cases.inventory import InventoryUseCases
from domain import InventoryStatus


def _get_db():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager


def _get_uc():
    db = _get_db()
    return InventoryUseCases(db.get_session())


@views_bp.route('/inv/items')
def inv_items():
    uc = _get_uc()
    status = request.args.get('status', '')
    category_id = request.args.get('category_id', '', type=int)
    search = request.args.get('search', '')

    items = []
    try:
        st = None
        if status == 'active':
            st = 'active'
        elif status == 'inactive':
            st = 'inactive'
        elif status == 'discontinued':
            st = 'discontinued'

        items = uc.list_items(
            category_id=category_id or None,
            status=st,
            search=search or None,
        )
    except Exception as e:
        flash(f"Error loading inventory items: {e}", 'danger')

    categories = []
    try:
        categories = uc.list_categories(inventory_type=None)
    except Exception:
        pass

    return render_template('inventory/items.html',
        items=items,
        status=status,
        category_id=category_id or '',
        search=search,
        categories=categories,
    )


@views_bp.route('/inv/receipts')
def inv_receipts():
    uc = _get_uc()
    period = request.args.get('period', session.get('period', ''))
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))

    receipts = []
    has_more = False
    try:
        posted = None
        if status == 'posted':
            posted = True
        elif status == 'draft':
            posted = False

        date_from = None
        date_to = None
        if period and '-' in period:
            parts = period.split('-')
            date_from = date(int(parts[0]), int(parts[1]), 1)
            if int(parts[1]) == 12:
                date_to = date(int(parts[0]) + 1, 1, 1)
            else:
                date_to = date(int(parts[0]), int(parts[1]) + 1, 1)

        raw, total = uc.list_receipts(
            is_posted=posted,
            date_from=date_from,
            date_to=date_to,
            skip=(page - 1) * 50,
            limit=51,
        )
        has_more = len(raw) > 50
        receipts = raw[:50]
    except Exception as e:
        flash(f"Error loading receipts: {e}", 'danger')

    return render_template('inventory/receipts.html',
        receipts=receipts,
        period=period,
        status=status,
        page=page,
        has_more=has_more,
    )


@views_bp.route('/inv/issues')
def inv_issues():
    uc = _get_uc()
    period = request.args.get('period', session.get('period', ''))
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))

    issues = []
    has_more = False
    try:
        posted = None
        if status == 'posted':
            posted = True
        elif status == 'draft':
            posted = False

        date_from = None
        date_to = None
        if period and '-' in period:
            parts = period.split('-')
            date_from = date(int(parts[0]), int(parts[1]), 1)
            if int(parts[1]) == 12:
                date_to = date(int(parts[0]) + 1, 1, 1)
            else:
                date_to = date(int(parts[0]), int(parts[1]) + 1, 1)

        raw, total = uc.list_issues(
            is_posted=posted,
            date_from=date_from,
            date_to=date_to,
            skip=(page - 1) * 50,
            limit=51,
        )
        has_more = len(raw) > 50
        issues = raw[:50]
    except Exception as e:
        flash(f"Error loading issues: {e}", 'danger')

    return render_template('inventory/issues.html',
        issues=issues,
        period=period,
        status=status,
        page=page,
        has_more=has_more,
    )


@views_bp.route('/inv/stock-cards')
def inv_stock_cards():
    uc = _get_uc()
    item_id = request.args.get('item_id', '', type=int)
    warehouse_id = request.args.get('warehouse_id', '', type=int)
    period = request.args.get('period', session.get('period', ''))

    cards = []
    try:
        cards = uc.list_stock_cards(
            item_id=item_id or None,
            warehouse_id=warehouse_id or None,
            period_from=period or None,
            period_to=period or None,
        )
    except Exception as e:
        flash(f"Error loading stock cards: {e}", 'danger')

    items = []
    warehouses = []
    try:
        items = uc.list_items()
        warehouses = uc.list_warehouses()
    except Exception:
        pass

    return render_template('inventory/stock_cards.html',
        cards=cards,
        item_id=item_id or '',
        warehouse_id=warehouse_id or '',
        period=period,
        items=items,
        warehouses=warehouses,
    )
