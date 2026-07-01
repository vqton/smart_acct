from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date
from . import views_bp
from infrastructure.database import SmartACCTDatabaseConfig, SmartACCTDatabaseManager
from infrastructure.repositories.payroll_repository import PayrollRepository
from use_cases.payroll import PayrollUseCases
from domain import EmployeeStatus, PayrollRunStatus


def _get_db():
    db_config = SmartACCTDatabaseConfig()
    db_manager = SmartACCTDatabaseManager(db_config)
    db_manager.initialize()
    return db_manager


def _get_uc():
    db = _get_db()
    return PayrollUseCases(db.get_session())


@views_bp.route('/payroll/employees')
def payroll_employees():
    uc = _get_uc()
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))

    employees = []
    has_more = False
    try:
        filters = {}
        if status == 'active':
            filters['status'] = EmployeeStatus.ACTIVE
        elif status == 'inactive':
            filters['status'] = EmployeeStatus.INACTIVE
        elif status == 'terminated':
            filters['status'] = EmployeeStatus.TERMINATED
        if search:
            filters['search'] = search

        result = uc.list_employees(filters=filters or None, page=page, per_page=50)
        if result.is_success():
            data = result.get_data()
            if isinstance(data, dict):
                employees = data.get('employees', data.get('items', []))
            elif isinstance(data, list):
                employees = data
    except Exception as e:
        flash(f"Error loading employees: {e}", 'danger')

    return render_template('payroll/employees.html',
        employees=employees,
        status=status,
        search=search,
        page=page,
        has_more=has_more,
    )


@views_bp.route('/payroll/runs')
def payroll_runs():
    uc = _get_uc()
    period = request.args.get('period', session.get('period', ''))

    runs = []
    try:
        filters = {}
        if period:
            parts = period.split('-')
            if len(parts) == 2:
                filters['month'] = int(parts[1])
                filters['year'] = int(parts[0])
        result = uc.list_payroll_runs(filters=filters or None)
        if result.is_success():
            data = result.get_data()
            if isinstance(data, list):
                runs = data
    except Exception as e:
        flash(f"Error loading payroll runs: {e}", 'danger')

    return render_template('payroll/runs.html',
        runs=runs,
        period=period,
    )


@views_bp.route('/payroll/pit')
def payroll_pit():
    uc = _get_uc()
    period = request.args.get('period', session.get('period', ''))

    declarations = []
    try:
        filters = {}
        if period:
            parts = period.split('-')
            if len(parts) == 2:
                filters['month'] = int(parts[1])
                filters['year'] = int(parts[0])
        result = uc.list_pit_declarations(filters=filters or None)
        if result.is_success():
            data = result.get_data()
            if isinstance(data, list):
                declarations = data
    except Exception as e:
        flash(f"Error loading PIT declarations: {e}", 'danger')

    return render_template('payroll/pit.html',
        declarations=declarations,
        period=period,
    )
