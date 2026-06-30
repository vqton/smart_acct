from typing import Optional
from decimal import Decimal
from flask import Blueprint, current_app

cc_bp = Blueprint("cc", __name__, url_prefix="/api/v1/cc")


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


_cc_use_cases: Optional[object] = None


def _get_cc_use_cases():
    global _cc_use_cases
    if _cc_use_cases is None:
        from use_cases.cc import CCUseCases
        _cc_use_cases = CCUseCases(_get_session())
    return _cc_use_cases


def _json_category(c) -> dict:
    return {
        "id": c.id, "code": c.code, "name": c.name, "description": c.description,
        "default_allocation_method": c.default_allocation_method.value if hasattr(c.default_allocation_method, 'value') else c.default_allocation_method,
        "default_useful_life_months": c.default_useful_life_months,
        "gl_asset_account": c.gl_asset_account, "gl_alloc_account": c.gl_alloc_account,
        "gl_expense_account": c.gl_expense_account, "is_active": c.is_active,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _json_item(i) -> dict:
    return {
        "id": i.id, "code": i.code, "name": i.name, "category_id": i.category_id,
        "cc_type": i.cc_type.value if hasattr(i.cc_type, 'value') else i.cc_type,
        "status": i.status.value if hasattr(i.status, 'value') else i.status,
        "allocation_method": i.allocation_method.value if hasattr(i.allocation_method, 'value') else i.allocation_method,
        "quantity": str(i.quantity), "unit": i.unit,
        "unit_price": str(i.unit_price), "total_cost": str(i.total_cost),
        "allocated_amount": str(i.allocated_amount), "remaining_amount": str(i.remaining_amount),
        "allocation_status": i.allocation_status.value if hasattr(i.allocation_status, 'value') else i.allocation_status,
        "useful_life_months": i.useful_life_months, "allocation_start_period": i.allocation_start_period,
        "department_id": i.department_id, "employee_id": i.employee_id,
        "location": i.location, "supplier": i.supplier, "invoice_ref": i.invoice_ref,
        "purchase_date": i.purchase_date.isoformat() if i.purchase_date else None,
        "in_use_date": i.in_use_date.isoformat() if i.in_use_date else None,
        "warranty_expiry": i.warranty_expiry.isoformat() if i.warranty_expiry else None,
        "description": i.description,
        "responsibility_type": i.responsibility_type.value if hasattr(i.responsibility_type, 'value') else i.responsibility_type,
        "responsible_person": i.responsible_person,
        "created_by": i.created_by,
        "created_at": i.created_at.isoformat() if i.created_at else None,
        "updated_at": i.updated_at.isoformat() if i.updated_at else None,
    }


def _json_allocation(a) -> dict:
    return {
        "id": a.id, "item_id": a.item_id,
        "allocation_method": a.allocation_method.value if hasattr(a.allocation_method, 'value') else a.allocation_method,
        "total_amount": str(a.total_amount), "allocated_amount": str(a.allocated_amount),
        "remaining_amount": str(a.remaining_amount),
        "start_period": a.start_period, "end_period": a.end_period,
        "total_periods": a.total_periods, "amount_per_period": str(a.amount_per_period),
        "status": a.status.value if hasattr(a.status, 'value') else a.status,
        "gl_account_credit": a.gl_account_credit, "gl_account_debit": a.gl_account_debit,
        "created_by": a.created_by,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
    }


def _json_allocation_line(l) -> dict:
    return {
        "id": l.id, "allocation_id": l.allocation_id, "item_id": l.item_id,
        "period": l.period, "planned_amount": str(l.planned_amount),
        "actual_amount": str(l.actual_amount),
        "is_posted": l.is_posted, "posted_at": l.posted_at.isoformat() if l.posted_at else None,
        "gl_journal_ref": l.gl_journal_ref, "notes": l.notes,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }


def _json_transaction(t) -> dict:
    return {
        "id": t.id, "item_id": t.item_id,
        "transaction_type": t.transaction_type.value if hasattr(t.transaction_type, 'value') else t.transaction_type,
        "quantity": str(t.quantity), "unit_price": str(t.unit_price),
        "total_amount": str(t.total_amount),
        "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None,
        "period": t.period, "department_id": t.department_id, "employee_id": t.employee_id,
        "reference_doc": t.reference_doc, "description": t.description,
        "created_by": t.created_by, "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def _json_transfer(t) -> dict:
    return {
        "id": t.id, "item_id": t.item_id,
        "from_department_id": t.from_department_id, "to_department_id": t.to_department_id,
        "from_employee_id": t.from_employee_id, "to_employee_id": t.to_employee_id,
        "from_location": t.from_location, "to_location": t.to_location,
        "quantity": str(t.quantity),
        "transfer_date": t.transfer_date.isoformat() if t.transfer_date else None,
        "reason": t.reason, "created_by": t.created_by,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def _json_inventory(inv) -> dict:
    return {
        "id": inv.id,
        "inventory_date": inv.inventory_date.isoformat() if inv.inventory_date else None,
        "department_id": inv.department_id, "notes": inv.notes,
        "status": inv.status.value if hasattr(inv.status, 'value') else inv.status,
        "created_by": inv.created_by,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "resolved_at": inv.resolved_at.isoformat() if inv.resolved_at else None,
        "lines": [_json_inventory_line(l) for l in (inv.lines or [])],
    }


def _json_inventory_line(l) -> dict:
    return {
        "id": l.id, "inventory_id": l.inventory_id, "item_id": l.item_id,
        "book_quantity": str(l.book_quantity), "physical_quantity": str(l.physical_quantity),
        "difference": str(l.difference), "unit_price": str(l.unit_price),
        "difference_amount": str(l.difference_amount),
        "reason": l.reason, "resolution": l.resolution,
    }


def _json_write_off(wo) -> dict:
    return {
        "id": wo.id, "item_id": wo.item_id,
        "write_off_date": wo.write_off_date.isoformat() if wo.write_off_date else None,
        "quantity": str(wo.quantity), "remaining_value": str(wo.remaining_value),
        "reason": wo.reason, "disposal_method": wo.disposal_method,
        "proceeds": str(wo.proceeds), "loss_amount": str(wo.loss_amount),
        "approved_by": wo.approved_by, "document_ref": wo.document_ref,
        "created_by": wo.created_by, "created_at": wo.created_at.isoformat() if wo.created_at else None,
    }


def _json_spare_part(sp) -> dict:
    return {
        "id": sp.id, "item_id": sp.item_id, "code": sp.code, "name": sp.name,
        "quantity": str(sp.quantity), "unit": sp.unit, "unit_price": str(sp.unit_price),
        "total_value": str(sp.total_value), "location": sp.location, "notes": sp.notes,
    }


from . import routes  # noqa: E402
