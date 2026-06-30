from typing import Optional
from decimal import Decimal
from flask import Blueprint, current_app

inv_bp = Blueprint("inv", __name__, url_prefix="/api/v1/inv")


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


def _json_category(c) -> dict:
    return {
        "id": c.id, "code": c.code, "name": c.name,
        "description": c.description,
        "parent_id": c.parent_id,
        "inventory_type": c.inventory_type.value if hasattr(c.inventory_type, 'value') else c.inventory_type,
        "valuation_method": c.valuation_method.value if hasattr(c.valuation_method, 'value') else c.valuation_method,
        "gl_inventory_account": c.gl_inventory_account,
        "gl_receipt_account": c.gl_receipt_account,
        "gl_issue_account": c.gl_issue_account,
        "gl_sales_account": c.gl_sales_account,
        "gl_cost_of_sales": c.gl_cost_of_sales,
        "gl_return_account": c.gl_return_account,
        "is_active": c.is_active,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _json_warehouse(w) -> dict:
    return {
        "id": w.id, "code": w.code, "name": w.name,
        "address": w.address, "contact_person": w.contact_person,
        "contact_phone": w.contact_phone,
        "is_active": w.is_active, "allow_negative_stock": w.allow_negative_stock,
        "check_method": w.check_method.value if hasattr(w.check_method, 'value') else w.check_method,
        "gl_inventory_account": w.gl_inventory_account,
        "notes": w.notes,
        "created_at": w.created_at.isoformat() if w.created_at else None,
    }


def _json_item(i) -> dict:
    return {
        "id": i.id, "code": i.code, "name": i.name,
        "category_id": i.category_id, "default_warehouse_id": i.default_warehouse_id,
        "inventory_type": i.inventory_type.value if hasattr(i.inventory_type, 'value') else i.inventory_type,
        "status": i.status.value if hasattr(i.status, 'value') else i.status,
        "valuation_method": i.valuation_method.value if i.valuation_method and hasattr(i.valuation_method, 'value') else i.valuation_method,
        "unit": i.unit, "unit_price": str(i.unit_price),
        "cost_price": str(i.cost_price), "selling_price": str(i.selling_price),
        "min_stock": str(i.min_stock), "max_stock": str(i.max_stock),
        "reorder_point": str(i.reorder_point), "reorder_quantity": str(i.reorder_quantity),
        "current_stock": str(i.current_stock), "reserved_stock": str(i.reserved_stock),
        "available_stock": str(i.available_stock),
        "batch_tracking": i.batch_tracking, "serial_tracking": i.serial_tracking,
        "expiry_tracking": i.expiry_tracking,
        "weight": str(i.weight) if i.weight else None,
        "volume": str(i.volume) if i.volume else None,
        "hs_code": i.hs_code, "barcode": i.barcode,
        "tax_rate": str(i.tax_rate),
        "description": i.description,
        "created_by": i.created_by,
        "created_at": i.created_at.isoformat() if i.created_at else None,
        "updated_at": i.updated_at.isoformat() if i.updated_at else None,
    }


def _json_batch(b) -> dict:
    return {
        "id": b.id, "item_id": b.item_id, "warehouse_id": b.warehouse_id,
        "batch_code": b.batch_code,
        "manufacturing_date": b.manufacturing_date.isoformat() if b.manufacturing_date else None,
        "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
        "received_date": b.received_date.isoformat() if b.received_date else None,
        "quantity": str(b.quantity), "remaining_quantity": str(b.remaining_quantity),
        "unit_cost": str(b.unit_cost), "total_cost": str(b.total_cost),
        "status": b.status.value if hasattr(b.status, 'value') else b.status,
        "supplier_batch": b.supplier_batch,
        "notes": b.notes,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


def _json_serial(s) -> dict:
    return {
        "id": s.id, "item_id": s.item_id, "batch_id": s.batch_id,
        "warehouse_id": s.warehouse_id, "serial_code": s.serial_code,
        "status": s.status.value if hasattr(s.status, 'value') else s.status,
        "receipt_date": s.receipt_date.isoformat() if s.receipt_date else None,
        "issue_date": s.issue_date.isoformat() if s.issue_date else None,
        "notes": s.notes,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def _json_receipt(r) -> dict:
    return {
        "id": r.id, "receipt_code": r.receipt_code,
        "receipt_date": r.receipt_date.isoformat() if r.receipt_date else None,
        "warehouse_id": r.warehouse_id,
        "supplier_id": r.supplier_id,
        "supplier_invoice_ref": r.supplier_invoice_ref,
        "reference_doc": r.reference_doc, "description": r.description,
        "is_posted": r.is_posted,
        "posted_at": r.posted_at.isoformat() if r.posted_at else None,
        "gl_journal_ref": r.gl_journal_ref,
        "created_by": r.created_by,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "lines": [_json_receipt_line(l) for l in r.lines] if r.lines else [],
    }


def _json_receipt_line(l) -> dict:
    return {
        "id": l.id, "receipt_id": l.receipt_id, "item_id": l.item_id,
        "warehouse_id": l.warehouse_id, "batch_id": l.batch_id,
        "quantity": str(l.quantity), "unit_price": str(l.unit_price),
        "total_amount": str(l.total_amount),
        "tax_amount": str(l.tax_amount), "discount_amount": str(l.discount_amount),
        "line_order": l.line_order, "notes": l.notes,
    }


def _json_issue(r) -> dict:
    return {
        "id": r.id, "issue_code": r.issue_code,
        "issue_date": r.issue_date.isoformat() if r.issue_date else None,
        "warehouse_id": r.warehouse_id,
        "department_id": r.department_id, "customer_id": r.customer_id,
        "recipient_name": r.recipient_name,
        "reference_doc": r.reference_doc, "description": r.description,
        "is_posted": r.is_posted,
        "posted_at": r.posted_at.isoformat() if r.posted_at else None,
        "gl_journal_ref": r.gl_journal_ref,
        "created_by": r.created_by,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "lines": [_json_issue_line(l) for l in r.lines] if r.lines else [],
    }


def _json_issue_line(l) -> dict:
    return {
        "id": l.id, "issue_id": l.issue_id, "item_id": l.item_id,
        "warehouse_id": l.warehouse_id, "batch_id": l.batch_id,
        "quantity": str(l.quantity), "unit_price": str(l.unit_price),
        "total_amount": str(l.total_amount),
        "tax_amount": str(l.tax_amount), "discount_amount": str(l.discount_amount),
        "line_order": l.line_order,
        "cost_price": str(l.cost_price), "cost_amount": str(l.cost_amount),
        "notes": l.notes,
    }


def _json_transfer(t) -> dict:
    return {
        "id": t.id, "transfer_code": t.transfer_code,
        "transfer_date": t.transfer_date.isoformat() if t.transfer_date else None,
        "from_warehouse_id": t.from_warehouse_id, "to_warehouse_id": t.to_warehouse_id,
        "status": t.status.value if hasattr(t.status, 'value') else t.status,
        "reference_doc": t.reference_doc, "description": t.description,
        "is_posted": t.is_posted,
        "posted_at": t.posted_at.isoformat() if t.posted_at else None,
        "gl_journal_ref": t.gl_journal_ref,
        "created_by": t.created_by,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "lines": [_json_transfer_line(l) for l in t.lines] if t.lines else [],
    }


def _json_transfer_line(l) -> dict:
    return {
        "id": l.id, "transfer_id": l.transfer_id, "item_id": l.item_id,
        "quantity": str(l.quantity), "unit_price": str(l.unit_price),
        "total_amount": str(l.total_amount),
        "line_order": l.line_order, "notes": l.notes,
    }


def _json_stock_card(c) -> dict:
    return {
        "id": c.id, "item_id": c.item_id, "warehouse_id": c.warehouse_id,
        "period": c.period,
        "opening_quantity": str(c.opening_quantity), "opening_value": str(c.opening_value),
        "receipt_quantity": str(c.receipt_quantity), "receipt_value": str(c.receipt_value),
        "issue_quantity": str(c.issue_quantity), "issue_value": str(c.issue_value),
        "closing_quantity": str(c.closing_quantity), "closing_value": str(c.closing_value),
        "unit_cost": str(c.unit_cost),
    }


def _json_check(c) -> dict:
    return {
        "id": c.id, "check_code": c.check_code,
        "check_date": c.check_date.isoformat() if c.check_date else None,
        "warehouse_id": c.warehouse_id,
        "status": c.status.value if hasattr(c.status, 'value') else c.status,
        "reference_doc": c.reference_doc, "notes": c.notes,
        "created_by": c.created_by, "approved_by": c.approved_by,
        "approved_at": c.approved_at.isoformat() if c.approved_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "lines": [_json_check_line(l) for l in c.lines] if c.lines else [],
    }


def _json_check_line(l) -> dict:
    return {
        "id": l.id, "check_id": l.check_id, "item_id": l.item_id,
        "warehouse_id": l.warehouse_id, "batch_id": l.batch_id,
        "book_quantity": str(l.book_quantity), "physical_quantity": str(l.physical_quantity),
        "difference_quantity": str(l.difference_quantity),
        "unit_price": str(l.unit_price), "difference_value": str(l.difference_value),
        "reason": l.reason, "resolution": l.resolution,
    }


def _json_adjustment(a) -> dict:
    return {
        "id": a.id, "adjustment_code": a.adjustment_code,
        "adjustment_date": a.adjustment_date.isoformat() if a.adjustment_date else None,
        "warehouse_id": a.warehouse_id,
        "adjustment_type": a.adjustment_type.value if hasattr(a.adjustment_type, 'value') else a.adjustment_type,
        "reason": a.reason, "reference_doc": a.reference_doc,
        "is_posted": a.is_posted,
        "posted_at": a.posted_at.isoformat() if a.posted_at else None,
        "gl_journal_ref": a.gl_journal_ref,
        "created_by": a.created_by,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "lines": [_json_adjustment_line(l) for l in a.lines] if a.lines else [],
    }


def _json_adjustment_line(l) -> dict:
    return {
        "id": l.id, "adjustment_id": l.adjustment_id, "item_id": l.item_id,
        "warehouse_id": l.warehouse_id, "batch_id": l.batch_id,
        "quantity_change": str(l.quantity_change),
        "unit_price": str(l.unit_price), "total_amount": str(l.total_amount),
        "line_order": l.line_order, "notes": l.notes,
    }
