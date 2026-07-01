from flask import render_template, request, session
from . import views_bp
from use_cases.costing_center import CostingCenterUseCases
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager


def _get_session():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager.get_session()


@views_bp.route('/costing')
def costing():
    session_db = _get_session()
    try:
        uc = CostingCenterUseCases(session_db)

        cost_centers_result = uc.list_cost_centers()
        cost_centers = cost_centers_result.get_data() if hasattr(cost_centers_result, 'get_data') else []

        allocation_runs = uc.list_allocation_runs()

        accumulated_result = uc.get_cost_accumulation()
        accumulated = accumulated_result.get_data() if accumulated_result and hasattr(accumulated_result, 'get_data') and not getattr(accumulated_result, 'is_failure', lambda: True)() else []

        variance_data = []
        for cc in cost_centers:
            var_result = uc.compute_variance(cc.id, session.get('period', '')[:7].replace('-', '') if session.get('period') else '')
            if var_result.is_success():
                var_data = var_result.get_data()
                lines = var_data if isinstance(var_data, list) else var_data.get('lines', []) if isinstance(var_data, dict) else []
                budget = sum(l.get('budget_amount', l.budget_amount if hasattr(l, 'budget_amount') else 0) for l in lines)
                actual = sum(l.get('actual_amount', l.actual_amount if hasattr(l, 'actual_amount') else 0) for l in lines)
                variance = budget - actual
                vpct = round(float(variance / budget * 100), 1) if budget else 0
                variance_data.append({
                    'cost_center_name': cc.name if hasattr(cc, 'name') else '',
                    'budget': budget,
                    'actual': actual,
                    'variance': variance,
                    'variance_pct': vpct,
                })

        return render_template('costing/list.html',
            period=session.get('period'),
            cost_centers=cost_centers,
            allocation_runs=allocation_runs,
            accumulated=accumulated,
            variance_data=variance_data,
        )
    finally:
        session_db.close()
