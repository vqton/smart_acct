from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date
from . import views_bp
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from infrastructure.repositories.fa_repository import FARepository
from use_cases.fa import FAUseCases
from domain import AssetStatus, AssetType


def _get_db():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager


def _get_uc():
    db = _get_db()
    return FAUseCases(db.get_session())


@views_bp.route('/fa/assets')
def fa_assets():
    uc = _get_uc()
    status = request.args.get('status', '')
    category_id = request.args.get('category_id', '', type=int)

    assets = []
    try:
        st = None
        if status == 'active':
            st = AssetStatus.ACTIVE
        elif status == 'fully_depreciated':
            st = AssetStatus.FULLY_DEPRECIATED
        elif status == 'disposed':
            st = AssetStatus.DISPOSED
        elif status == 'suspended':
            st = AssetStatus.SUSPENDED

        result = uc.list_assets(
            category_id=category_id or None,
            status=st,
        )
        assets = result.get_data() if result.is_success() else []
    except Exception as e:
        flash(f"Error loading fixed assets: {e}", 'danger')

    categories = []
    try:
        cat_result = uc.list_categories()
        categories = cat_result.get_data() if cat_result.is_success() else []
    except Exception:
        pass

    return render_template('fa/assets.html',
        assets=assets,
        status=status,
        category_id=category_id or '',
        categories=categories,
    )


@views_bp.route('/fa/categories')
def fa_categories():
    uc = _get_uc()

    categories = []
    try:
        result = uc.list_categories()
        categories = result.get_data() if result.is_success() else []
    except Exception as e:
        flash(f"Error loading FA categories: {e}", 'danger')

    return render_template('fa/categories.html', categories=categories)


@views_bp.route('/fa/depreciation')
def fa_depreciation():
    uc = _get_uc()
    period = request.args.get('period', session.get('period', ''))

    records = []
    try:
        if period:
            result = uc.get_depreciation_for_period(period)
            records = result.get_data() if result.is_success() else []
    except Exception as e:
        flash(f"Error loading depreciation records: {e}", 'danger')

    return render_template('fa/depreciation.html',
        records=records,
        period=period,
    )
