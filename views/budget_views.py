from flask import render_template, request, session
from . import views_bp
from use_cases.budget import BudgetUseCases
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager


def _get_session():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager.get_session()


@views_bp.route('/budget')
def budget():
    session_db = _get_session()
    try:
        uc = BudgetUseCases(session_db)
        structures = uc.list_budget_structures()
        categories = []
        execution_data = []
        total_budget = 0
        total_actual = 0
        total_variance = 0
        variance_pct = 0

        if structures:
            structure = structures[0]
            cat_result = uc.list_budget_categories(structure.id)
            if cat_result:
                categories = cat_result if isinstance(cat_result, list) else []

            version = uc.get_active_budget_version(structure.fiscal_year)
            if version:
                plans = uc.list_budget_plans(version.id)
                for plan in (plans or []):
                    for line in (plan.lines or []):
                        annual = sum(
                            Decimal(str(v)) for v in (line.amounts or {}).values()
                        ) if line.amounts else 0
                        total_budget += annual

                        gl_code = line.gl_account_code
                        actual = uc._get_gl_actual(gl_code)
                        total_actual += actual
                        variance = annual - actual
                        total_variance += variance

                        cat_name = line.name
                        execution_data.append({
                            'category_name': cat_name,
                            'budget_amount': annual,
                            'actual_amount': actual,
                            'variance': variance,
                            'variance_pct': round(float(variance / annual * 100), 1) if annual else 0,
                        })

        if total_budget:
            variance_pct = round(float(total_variance / total_budget * 100), 1)

        return render_template('budget/dashboard.html',
            period=session.get('period'),
            total_budget=total_budget,
            total_actual=total_actual,
            total_variance=total_variance,
            variance_pct=variance_pct,
            execution_data=execution_data,
        )
    finally:
        session_db.close()
