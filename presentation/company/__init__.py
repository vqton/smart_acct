from flask import Blueprint

company_bp = Blueprint("company", __name__)

from presentation.company import routes


def serialize_company(company: dict) -> dict:
    return {
        "id": company.get("id"),
        "name": company.get("name"),
        "tax_code": company.get("tax_code"),
        "address": company.get("address"),
        "phone": company.get("phone"),
        "email": company.get("email"),
        "website": company.get("website"),
        "logo_url": company.get("logo_url"),
        "business_reg_number": company.get("business_reg_number"),
        "date_format": company.get("date_format"),
        "currency_code": company.get("currency_code"),
        "fiscal_year_start_month": company.get("fiscal_year_start_month"),
        "accounting_regime": company.get("accounting_regime"),
        "locale": company.get("locale"),
        "is_active": company.get("is_active", True),
        "created_at": company.get("created_at"),
        "updated_at": company.get("updated_at"),
    }


def serialize_fiscal_year(fy: dict) -> dict:
    return {
        "id": fy.get("id"),
        "company_id": fy.get("company_id"),
        "fiscal_year": fy.get("fiscal_year"),
        "start_date": fy.get("start_date"),
        "end_date": fy.get("end_date"),
        "is_closed": fy.get("is_closed", False),
        "is_current": fy.get("is_current", False),
    }


def serialize_numbering_rule(rule: dict) -> dict:
    return {
        "id": rule.get("id"),
        "company_id": rule.get("company_id"),
        "document_type": rule.get("document_type"),
        "prefix": rule.get("prefix"),
        "suffix": rule.get("suffix"),
        "next_number": rule.get("next_number"),
        "pad_length": rule.get("pad_length"),
        "fiscal_year": rule.get("fiscal_year"),
    }


def serialize_checklist_item(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "section": item.get("section"),
        "label": item.get("label"),
        "is_completed": item.get("is_completed", False),
        "sort_order": item.get("sort_order"),
    }
