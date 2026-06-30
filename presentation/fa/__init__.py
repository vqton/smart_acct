from typing import Optional
from decimal import Decimal
from flask import Blueprint, current_app

fa_bp = Blueprint("fa", __name__, url_prefix="/api/v1/fa")


def _get_session():
    if not hasattr(current_app, "db_manager"):
        raise RuntimeError("Database not initialized")
    return current_app.db_manager.get_session()


_fa_use_cases: Optional[object] = None


def _get_fa_use_cases():
    global _fa_use_cases
    if _fa_use_cases is None:
        from infrastructure.repositories.fa_repository import FARepository
        from infrastructure.database import SmartACCTDatabase
        db = SmartACCTDatabase()
        session = db.SessionLocal()
        from use_cases.fa import FAUseCases
        _fa_use_cases = FAUseCases(FARepository(session), db_manager=db)
    return _fa_use_cases


def _json_category(c) -> dict:
    return {
        "id": c.id,
        "code": c.code,
        "name": c.name,
        "asset_type": c.asset_type.value if hasattr(c.asset_type, 'value') else c.asset_type,
        "asset_classification": c.asset_classification.value if hasattr(c.asset_classification, 'value') else c.asset_classification,
        "default_depreciation_method": c.default_depreciation_method.value if hasattr(c.default_depreciation_method, 'value') else c.default_depreciation_method,
        "default_useful_life_min": c.default_useful_life_min,
        "default_useful_life_max": c.default_useful_life_max,
        "description": c.description,
        "is_active": c.is_active,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _json_asset(a) -> dict:
    return {
        "id": a.id,
        "code": a.code,
        "name": a.name,
        "category_id": a.category_id,
        "asset_type": a.asset_type.value if hasattr(a.asset_type, 'value') else a.asset_type,
        "asset_classification": a.asset_classification.value if hasattr(a.asset_classification, 'value') else a.asset_classification,
        "original_cost": str(a.original_cost),
        "accumulated_depreciation": str(a.accumulated_depreciation),
        "residual_value": str(a.residual_value),
        "carrying_amount": str(a.carrying_amount),
        "useful_life_months": a.useful_life_months,
        "depreciation_method": a.depreciation_method.value if hasattr(a.depreciation_method, 'value') else a.depreciation_method,
        "acquisition_date": a.acquisition_date.isoformat() if a.acquisition_date else None,
        "in_use_date": a.in_use_date.isoformat() if a.in_use_date else None,
        "department_id": a.department_id,
        "location": a.location,
        "status": a.status.value if hasattr(a.status, 'value') else a.status,
        "fund_source": a.fund_source.value if hasattr(a.fund_source, 'value') else a.fund_source,
        "use_type": a.use_type.value if hasattr(a.use_type, 'value') else a.use_type,
        "supplier": a.supplier,
        "invoice_ref": a.invoice_ref,
        "description": a.description,
        "created_by": a.created_by,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
    }


def _json_depreciation(d) -> dict:
    return {
        "id": d.id,
        "asset_id": d.asset_id,
        "period": d.period,
        "depreciation_amount": str(d.depreciation_amount),
        "accumulated_total": str(d.accumulated_total),
        "nbv": str(d.nbv),
        "is_posted": d.is_posted,
        "posted_at": d.posted_at.isoformat() if d.posted_at else None,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


def _json_adjustment(adj) -> dict:
    return {
        "id": adj.id,
        "asset_id": adj.asset_id,
        "adjustment_type": adj.adjustment_type.value if hasattr(adj.adjustment_type, 'value') else adj.adjustment_type,
        "amount": str(adj.amount),
        "previous_cost": str(adj.previous_cost),
        "new_cost": str(adj.new_cost),
        "reason": adj.reason,
        "document_ref": adj.document_ref,
        "effective_date": adj.effective_date.isoformat() if adj.effective_date else None,
        "appraised_by": adj.appraised_by,
        "appraisal_date": adj.appraisal_date.isoformat() if adj.appraisal_date else None,
        "created_by": adj.created_by,
        "created_at": adj.created_at.isoformat() if adj.created_at else None,
    }


def _json_disposal(d) -> dict:
    return {
        "id": d.id,
        "asset_id": d.asset_id,
        "disposal_type": d.disposal_type.value if hasattr(d.disposal_type, 'value') else d.disposal_type,
        "disposal_date": d.disposal_date.isoformat() if d.disposal_date else None,
        "proceeds": str(d.proceeds),
        "costs": str(d.costs),
        "nbv_at_disposal": str(d.nbv_at_disposal),
        "gain_loss": str(d.gain_loss),
        "buyer_info": d.buyer_info,
        "reason": d.reason,
        "approved_by": d.approved_by,
        "document_ref": d.document_ref,
        "created_by": d.created_by,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


def _json_transfer(t) -> dict:
    return {
        "id": t.id,
        "asset_id": t.asset_id,
        "from_department_id": t.from_department_id,
        "to_department_id": t.to_department_id,
        "from_location": t.from_location,
        "to_location": t.to_location,
        "effective_date": t.effective_date.isoformat() if t.effective_date else None,
        "reason": t.reason,
        "created_by": t.created_by,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def _json_inventory(inv) -> dict:
    return {
        "id": inv.id,
        "inventory_date": inv.inventory_date.isoformat() if inv.inventory_date else None,
        "department_id": inv.department_id,
        "asset_count_book": inv.asset_count_book,
        "asset_count_physical": inv.asset_count_physical,
        "surplus_count": inv.surplus_count,
        "deficit_count": inv.deficit_count,
        "status": inv.status.value if hasattr(inv.status, 'value') else inv.status,
        "notes": inv.notes,
        "created_by": inv.created_by,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "resolved_at": inv.resolved_at.isoformat() if inv.resolved_at else None,
        "lines": [_json_inventory_line(l) for l in inv.lines] if inv.lines else [],
    }


def _json_inventory_line(l) -> dict:
    return {
        "id": l.id,
        "inventory_id": l.inventory_id,
        "asset_id": l.asset_id,
        "book_quantity": l.book_quantity,
        "physical_quantity": l.physical_quantity,
        "difference": l.difference,
        "reason": l.reason,
        "resolution": l.resolution,
    }


def _json_spare_part(sp) -> dict:
    return {
        "id": sp.id,
        "asset_id": sp.asset_id,
        "code": sp.code,
        "name": sp.name,
        "quantity": sp.quantity,
        "unit": sp.unit,
        "value": str(sp.value),
    }


def _json_component(c) -> dict:
    return {
        "id": c.id,
        "asset_id": c.asset_id,
        "name": c.name,
        "original_cost": str(c.original_cost),
        "useful_life_months": c.useful_life_months,
        "depreciation_method": c.depreciation_method.value if c.depreciation_method and hasattr(c.depreciation_method, 'value') else c.depreciation_method,
    }


def _json_biological(b) -> dict:
    return {
        "id": b.id,
        "asset_id": b.asset_id,
        "biological_type": b.biological_type.value if hasattr(b.biological_type, 'value') else b.biological_type,
        "growth_stage": b.growth_stage.value if hasattr(b.growth_stage, 'value') else b.growth_stage,
        "quantity": str(b.quantity),
        "unit": b.unit,
        "planting_date": b.planting_date.isoformat() if b.planting_date else None,
        "expected_harvest_date": b.expected_harvest_date.isoformat() if b.expected_harvest_date else None,
        "provision_amount": str(b.provision_amount),
    }


def _json_biological_provision(p) -> dict:
    return {
        "id": p.id,
        "biological_asset_id": p.biological_asset_id,
        "period": p.period,
        "provision_amount": str(p.provision_amount),
        "provision_type": p.provision_type.value if hasattr(p.provision_type, 'value') else p.provision_type,
        "reason": p.reason,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


from . import routes  # noqa: E402
