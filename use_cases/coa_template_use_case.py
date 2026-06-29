from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from domain import (
    ChartOfAccounts, AccountType, DCRDirection,
    AccountingRegime, Result,
)
from infrastructure.repositories.coa_repository import COARepository


STANDARD_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "tt99_2025_standard": {
        "name": "Standard COA (TT99/2025)",
        "description": "Hệ thống tài khoản kế toán theo Thông tư 99/2025/TT-BTC",
        "regime": "tt99_2025",
        "accounts": [
            {"code": "1", "name": "Tài sản", "account_type": "asset", "drcr_direction": "debit", "level": 1},
            {"code": "11", "name": "Tiền và các khoản tương đương tiền", "account_type": "asset", "drcr_direction": "debit", "level": 2},
            {"code": "111", "name": "Tiền mặt", "account_type": "cash", "drcr_direction": "debit", "level": 3},
            {"code": "1111", "name": "Tiền mặt tại quỹ (VND)", "account_type": "cash", "drcr_direction": "debit", "level": 4, "currency": "VND"},
            {"code": "112", "name": "Tiền gửi ngân hàng", "account_type": "bank", "drcr_direction": "debit", "level": 3},
            {"code": "2", "name": "Nợ phải trả", "account_type": "liability", "drcr_direction": "credit", "level": 1},
            {"code": "331", "name": "Phải trả người bán", "account_type": "liability", "drcr_direction": "credit", "level": 2},
            {"code": "3311", "name": "Phải trả người bán trong nước", "account_type": "liability", "drcr_direction": "credit", "level": 3},
            {"code": "5", "name": "Doanh thu", "account_type": "revenue", "drcr_direction": "credit", "level": 1},
            {"code": "511", "name": "Doanh thu bán hàng", "account_type": "revenue", "drcr_direction": "credit", "level": 2},
            {"code": "5111", "name": "Doanh thu bán hàng hóa", "account_type": "revenue", "drcr_direction": "credit", "level": 3},
            {"code": "6", "name": "Chi phí sản xuất", "account_type": "expense", "drcr_direction": "debit", "level": 1},
            {"code": "621", "name": "Chi phí nguyên vật liệu trực tiếp", "account_type": "expense", "drcr_direction": "debit", "level": 2},
        ],
    },
    "tt133_2016_standard": {
        "name": "Standard COA (TT133/2016)",
        "description": "Hệ thống tài khoản kế toán theo Thông tư 133/2016/TT-BTC",
        "regime": "tt133_2016",
        "accounts": [
            {"code": "1", "name": "Tài sản", "account_type": "asset", "drcr_direction": "debit", "level": 1},
            {"code": "11", "name": "Tiền và các khoản tương đương tiền", "account_type": "asset", "drcr_direction": "debit", "level": 2},
            {"code": "111", "name": "Tiền mặt", "account_type": "cash", "drcr_direction": "debit", "level": 3},
            {"code": "1111", "name": "Tiền mặt VND", "account_type": "cash", "drcr_direction": "debit", "level": 4},
            {"code": "2", "name": "Nợ phải trả", "account_type": "liability", "drcr_direction": "credit", "level": 1},
            {"code": "331", "name": "Phải trả người bán", "account_type": "accounts_payable", "drcr_direction": "credit", "level": 2},
            {"code": "5", "name": "Doanh thu", "account_type": "revenue", "drcr_direction": "credit", "level": 1},
            {"code": "511", "name": "Doanh thu bán hàng", "account_type": "revenue", "drcr_direction": "credit", "level": 2},
            {"code": "6", "name": "Chi phí", "account_type": "expense", "drcr_direction": "debit", "level": 1},
            {"code": "621", "name": "Chi phí NVL trực tiếp", "account_type": "expense", "drcr_direction": "debit", "level": 2},
        ],
    },
}


class COATemplateUseCase:
    def __init__(self, session: Session):
        self.repo = COARepository(session)
        self.session = session

    def list_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": tid,
                "name": tpl["name"],
                "description": tpl["description"],
                "regime": tpl["regime"],
                "account_count": len(tpl["accounts"]),
            }
            for tid, tpl in STANDARD_TEMPLATES.items()
        ]

    def preview_template(self, template_id: str) -> Result:
        if template_id not in STANDARD_TEMPLATES:
            return Result.failure(ValueError(f"Template '{template_id}' not found"))
        tpl = STANDARD_TEMPLATES[template_id]
        return Result.success({
            "id": template_id,
            "name": tpl["name"],
            "description": tpl["description"],
            "regime": tpl["regime"],
            "accounts": [
                {
                    "code": a["code"],
                    "name": a["name"],
                    "account_type": a["account_type"],
                    "drcr_direction": a["drcr_direction"],
                    "level": a["level"],
                }
                for a in tpl["accounts"]
            ],
        })

    def apply_template(self, template_id: str, clear_existing: bool = False) -> Result:
        if template_id not in STANDARD_TEMPLATES:
            return Result.failure(ValueError(f"Template '{template_id}' not found"))
        template = STANDARD_TEMPLATES[template_id]

        if clear_existing:
            existing = self.repo.list_all()
            for acc in existing:
                self.repo.delete(acc.code)
            self.session.flush()

        created: List[str] = []
        errors: List[str] = []

        for acc_data in template["accounts"]:
            try:
                domain_acc = ChartOfAccounts(
                    code=acc_data["code"],
                    name=acc_data["name"],
                    account_type=AccountType(acc_data["account_type"]),
                    regime=AccountingRegime(template["regime"]),
                    drcr_direction=DCRDirection(acc_data["drcr_direction"]),
                    level=acc_data["level"],
                    currency=acc_data.get("currency", "VND"),
                    unit=acc_data.get("currency", "VND"),
                )
                result = self.repo.create(domain_acc)
                if result.is_success():
                    created.append(acc_data["code"])
                else:
                    errors.append(f"{acc_data['code']}: {result.error}")
            except Exception as e:
                errors.append(f"{acc_data['code']}: {e}")

        return Result.success({
            "template_id": template_id,
            "template_name": template["name"],
            "total_accounts": len(template["accounts"]),
            "created_count": len(created),
            "created": created,
            "error_count": len(errors),
            "errors": errors,
        })
