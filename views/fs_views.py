from flask import render_template, request, session
from . import views_bp
from use_cases.fs import FSUseCases
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from domain import FinancialStatementType, FSStatus


def _get_session():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager.get_session()


@views_bp.route('/fs')
def fs():
    session_db = _get_session()
    try:
        uc = FSUseCases(session_db)
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page

        statements = uc.list_statements(
            period=request.args.get('period'),
            statement_type=None,
            status=None,
            entity_id=None,
            limit=per_page,
            offset=offset,
        )

        return render_template('fs/list.html',
            period=session.get('period'),
            statements=statements,
            statement_types=FinancialStatementType,
            page=page,
            per_page=per_page,
        )
    finally:
        session_db.close()
