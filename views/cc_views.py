from flask import render_template, request, session
from . import views_bp
from use_cases.cc import CCUseCases
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager


def _get_session():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager.get_session()


@views_bp.route('/ccdc')
def ccdc():
    session_db = _get_session()
    try:
        uc = CCUseCases(session_db)
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status')

        items_result = uc.list_items(category_id=category_id, status=status)
        items = items_result.get_data() if hasattr(items_result, 'get_data') else []

        categories_result = uc.list_categories()
        categories = categories_result.get_data() if hasattr(categories_result, 'get_data') else []

        return render_template('cc/items.html',
            period=session.get('period'),
            items=items,
            categories=categories,
            selected_category=category_id,
            selected_status=status,
        )
    finally:
        session_db.close()
