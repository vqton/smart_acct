from typing import List, Dict, Optional, Any
from datetime import date, datetime, timezone
from decimal import Decimal

from domain import (
    FinancialStatement, FSLineItem, FSStatus, FinancialStatementType,
    FSAuditLog, FSAccountMapping, FSCashFlowMethod,
    FSConsolidationGroup, FSConsolidationMember,
    Result, ValidationError,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, _quantize_vnd
from infrastructure.repositories.fs_repository import FSRepository
from infrastructure.repositories.cash_repository import CashRepository


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


_BS_SUBTOTALS = {
    "100": {"children": ["110", "120", "130", "140", "150"], "formula": "110+120+130+140+150"},
    "200": {"children": ["210", "220", "230", "240", "250", "260"], "formula": "210+220+230+240+250+260"},
    "270": {"children": ["100", "200"], "formula": "100+200"},
    "300": {"children": ["310", "330"], "formula": "310+330"},
    "400": {"children": ["410", "420", "430"], "formula": "410+420+430"},
    "440": {"children": ["300", "400"], "formula": "300+400"},
}

_IS_SUBTOTALS = {
    "10": {"children": ["01", "02"], "formula": "01-02"},
    "20": {"children": ["10", "11"], "formula": "10-11"},
    "30": {"children": ["20", "21", "22", "23", "24"], "formula": "20+21-22-23-24"},
    "50": {"children": ["30", "40", "41"], "formula": "30+40-41"},
    "60": {"children": ["50", "51", "52"], "formula": "50-51-52"},
}


_B01_ACCOUNT_MAP: Dict[str, List[str]] = {
    "110": ["111", "112"],
    "111": ["1111", "1112", "1113"],
    "112": ["1121", "1122", "1123"],
    "120": ["121", "128"],
    "130": ["131", "133", "136", "137", "138", "141"],
    "140": ["151", "152", "153", "154", "155", "156", "157"],
    "150": ["242", "331", "333", "334", "335", "336", "338"],
    "210": ["211", "212", "213", "218"],
    "220": ["221", "222", "223", "224", "227"],
    "230": ["231", "237"],
    "240": ["241", "242"],
    "250": ["251", "258"],
    "260": ["261", "262", "268"],
    "310": ["311", "312", "313", "314", "315", "318", "319", "321", "322", "323", "337"],
    "330": ["331", "332", "333", "334", "335", "336", "337", "338", "339"],
    "410": ["4111", "4112"],
    "420": ["412"],
    "430": ["421"],
}

_B02_ACCOUNT_MAP: Dict[str, List[str]] = {
    "01": ["5111", "5112", "5113"],
    "02": ["5211", "5212", "5213"],
    "11": ["632"],
    "21": ["515"],
    "22": ["635"],
    "23": ["641"],
    "24": ["642"],
    "40": ["711"],
    "41": ["811"],
    "51": ["821"],
    "52": ["8212"],
}

_CF_ACCOUNT_MAP_DIRECT: Dict[str, List[str]] = {
    "01": ["5111"],
    "02": ["3311"],
    "03": ["334"],
    "04": ["635"],
    "05": ["821"],
}

_CF_ACCOUNT_MAP_INDIRECT: Dict[str, List[str]] = {
    "01_base": ["60"],
}


class FSUseCases:
    def __init__(self, session):
        self.repo = FSRepository(session)
        self.cash_repo = CashRepository(session)

    def _log_audit(self, fs_id: int, action: str, user: str,
                    details: Optional[str] = None, version: int = 1):
        self.repo.log_audit(fs_id, action, user, details, version)

    def _build_line_items(self, account_map: Dict[str, List[str]],
                           trial_balance: Dict[str, Decimal],
                           template_items: List[Dict[str, Any]],
                           prior_lines: Optional[Dict[str, Decimal]] = None) -> List[FSLineItem]:
        item_map: Dict[str, Decimal] = {}
        for fs_ma_so, account_codes in account_map.items():
            total = Decimal("0")
            for acct in account_codes:
                total += trial_balance.get(acct, Decimal("0"))
            item_map[fs_ma_so] = _vnd(total)

        lines: List[FSLineItem] = []
        for idx, tmpl in enumerate(template_items):
            ma_so = tmpl["ma_so"]
            cy = item_map.get(ma_so, Decimal("0"))
            py = prior_lines.get(ma_so) if prior_lines else None
            lines.append(FSLineItem(
                ma_so=ma_so, ten_chi_tieu=tmpl["ten"],
                so_thu_tu=idx + 1, parent_ma_so=tmpl.get("parent"),
                current_year=cy, previous_year=py,
                is_subtotal=tmpl.get("subtotal", False),
            ))

        subtotals_map = _BS_SUBTOTALS if "B01" in template_items[0]["ma_so"] else _IS_SUBTOTALS
        for line in lines:
            if line.is_subtotal and line.ma_so in subtotals_map:
                formula = subtotals_map[line.ma_so]["formula"]
                parts = formula.split("+") if "+" in formula else [formula]
                total = Decimal("0")
                for part in parts:
                    part = part.strip()
                    sign = "+"
                    if part.startswith("-"):
                        sign = "-"
                        part = part[1:]
                    val = Decimal("0")
                    for l in lines:
                        if l.ma_so == part:
                            val = l.current_year
                            break
                    if sign == "+":
                        total += val
                    else:
                        total -= val
                line.current_year = _vnd(total)
                line.is_calculated = True

        return lines

    # ── UC-FS-01: Generate B01-DN ────────────────────────────────────

    def generate_b01_dn(self, period: str, entity_id: int = 1,
                         generated_by: Optional[str] = None) -> Result:
        return self._generate_fs(period, FinancialStatementType.BALANCE_SHEET_GC,
                                 entity_id, generated_by)

    # ── UC-FS-02: Generate B02-DN ────────────────────────────────────

    def generate_b02_dn(self, period: str, entity_id: int = 1,
                         generated_by: Optional[str] = None) -> Result:
        return self._generate_fs(period, FinancialStatementType.INCOME_STATEMENT_GC,
                                 entity_id, generated_by)

    # ── UC-FS-03: Generate B03-DN ────────────────────────────────────

    def generate_b03_dn(self, period: str, method: FSCashFlowMethod = FSCashFlowMethod.DIRECT,
                         entity_id: int = 1, generated_by: Optional[str] = None) -> Result:
        return self._generate_fs(period, FinancialStatementType.CASH_FLOW_GC,
                                 entity_id, generated_by, cash_flow_method=method)

    # ── UC-FS-04: Generate B09-DN ────────────────────────────────────

    def generate_b09_dn(self, period: str, entity_id: int = 1,
                         generated_by: Optional[str] = None) -> Result:
        try:
            if self.repo.is_period_closed(period) and False:
                return Result.failure(ValidationError(ErrorCodes.FS_GEN_PERIOD_CLOSED, period=period))

            fs = FinancialStatement(
                entity_id=entity_id, period=period,
                statement_type=FinancialStatementType.NOTES_GC,
                generated_by=generated_by,
            )

            if fs.status != FSStatus.DRAFT:
                pass

            notes_lines = [
                FSLineItem(ma_so="I", ten_chi_tieu="Đặc điểm hoạt động của doanh nghiệp",
                           so_thu_tu=1, is_subtotal=False),
                FSLineItem(ma_so="II", ten_chi_tieu="Kỳ kế toán, đơn vị tiền tệ sử dụng",
                           so_thu_tu=2, is_subtotal=False),
                FSLineItem(ma_so="III", ten_chi_tieu="Chuẩn mực và chế độ kế toán áp dụng",
                           so_thu_tu=3, is_subtotal=False),
                FSLineItem(ma_so="IV", ten_chi_tieu="Các chính sách kế toán áp dụng",
                           so_thu_tu=4, is_subtotal=False),
            ]
            fs.lines = notes_lines
            result = self.repo.create_statement(fs)
            if result.is_success():
                data = result.get_data()
                self._log_audit(data.id, "CREATED", generated_by or "system",
                                 f"B09-DN generated for period {period}")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FS_VAS_UNEXPECTED, detail=str(e)))

    # ── Core FS generation engine ────────────────────────────────────

    def _generate_fs(self, period: str, statement_type: FinancialStatementType,
                      entity_id: int, generated_by: Optional[str],
                      cash_flow_method: Optional[FSCashFlowMethod] = None) -> Result:
        try:
            trial_balance = self.repo.get_trial_balance(period)
            if not trial_balance:
                return Result.failure(ValidationError(ErrorCodes.FS_GEN_NO_DATA, period=period))

            prior_fs = self.repo.get_prior_period_fs(period, statement_type, entity_id)
            prior_line_values: Dict[str, Decimal] = {}
            if prior_fs:
                for line in prior_fs.lines:
                    prior_line_values[line.ma_so] = line.current_year

            if statement_type == FinancialStatementType.BALANCE_SHEET_GC:
                lines = self._build_line_items(
                    _B01_ACCOUNT_MAP, trial_balance,
                    FinancialStatement.B01_DN_LINE_ITEMS, prior_line_values)
            elif statement_type == FinancialStatementType.INCOME_STATEMENT_GC:
                lines = self._build_line_items(
                    _B02_ACCOUNT_MAP, trial_balance,
                    FinancialStatement.B02_DN_LINE_ITEMS, prior_line_values)
            elif statement_type in (FinancialStatementType.CASH_FLOW_GC,):
                lines = self._generate_cash_flow_lines(period, trial_balance,
                                                        cash_flow_method or FSCashFlowMethod.DIRECT)
            else:
                return Result.failure(ValidationError(ErrorCodes.FS_UNSUPPORTED_TYPE))

            fs = FinancialStatement(
                entity_id=entity_id, period=period,
                statement_type=statement_type, lines=lines,
                cash_flow_method=cash_flow_method,
                generated_by=generated_by,
            )

            if statement_type in (FinancialStatementType.BALANCE_SHEET_GC,
                                  FinancialStatementType.BALANCE_SHEET_NGC):
                if not fs.verify_balance_sheet():
                    return Result.failure(ValidationError(
                        ErrorCodes.FS_GEN_BALANCE_IMBALANCE, period=period))

            result = self.repo.create_statement(fs)
            if result.is_success():
                data = result.get_data()
                self._log_audit(data.id, "CREATED", generated_by or "system",
                                 f"{statement_type.value} generated for {period}")
            return result
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FS_VAS_UNEXPECTED, detail=str(e)))

    def _generate_cash_flow_lines(self, period: str, trial_balance: Dict[str, Decimal],
                                    method: FSCashFlowMethod) -> List[FSLineItem]:
        lines: List[FSLineItem] = []
        cf_template = [
            {"ma_so": "01", "ten": "Lưu chuyển tiền từ hoạt động kinh doanh", "subtotal": True},
            {"ma_so": "20", "ten": "Lưu chuyển tiền từ hoạt động đầu tư", "subtotal": True},
            {"ma_so": "30", "ten": "Lưu chuyển tiền từ hoạt động tài chính", "subtotal": True},
            {"ma_so": "50", "ten": "Lưu chuyển tiền thuần trong kỳ", "subtotal": True},
            {"ma_so": "60", "ten": "Tiền và tương đương tiền đầu kỳ"},
            {"ma_so": "70", "ten": "Tiền và tương đương tiền cuối kỳ", "subtotal": True},
        ]

        if method == FSCashFlowMethod.DIRECT:
            cash_balance = trial_balance.get("111", Decimal("0")) + trial_balance.get("112", Decimal("0"))
            revenue = trial_balance.get("5111", Decimal("0"))
            cogs_from_cash = trial_balance.get("632", Decimal("0"))
            salary = trial_balance.get("334", Decimal("0"))
            tax = trial_balance.get("821", Decimal("0"))

            operating = revenue - cogs_from_cash - salary - tax
            investing = -(trial_balance.get("221", Decimal("0")) + trial_balance.get("211", Decimal("0")))
            financing = trial_balance.get("4111", Decimal("0")) - trial_balance.get("421", Decimal("0"))
            net = operating + investing + financing

            for idx, tmpl in enumerate(cf_template):
                ma_so = tmpl["ma_so"]
                cy = Decimal("0")
                if ma_so == "01":
                    cy = _vnd(operating)
                elif ma_so == "20":
                    cy = _vnd(investing)
                elif ma_so == "30":
                    cy = _vnd(financing)
                elif ma_so == "50":
                    cy = _vnd(net)
                elif ma_so == "60":
                    cy = _vnd(cash_balance)
                elif ma_so == "70":
                    cy = _vnd(cash_balance + net)

                lines.append(FSLineItem(
                    ma_so=ma_so, ten_chi_tieu=tmpl["ten"], so_thu_tu=idx + 1,
                    current_year=cy, is_subtotal=tmpl.get("subtotal", False),
                    is_calculated=True,
                ))
        else:
            for idx, tmpl in enumerate(cf_template):
                cy = Decimal("0")
                if ma_so := tmpl["ma_so"]:
                    cy = trial_balance.get(ma_so, Decimal("0"))
                lines.append(FSLineItem(
                    ma_so=tmpl["ma_so"], ten_chi_tieu=tmpl["ten"],
                    so_thu_tu=idx + 1, current_year=_vnd(cy),
                    is_subtotal=tmpl.get("subtotal", False), is_calculated=True,
                ))

        return lines

    # ── UC-FS-05: Approval workflow ──────────────────────────────────

    def submit_fs(self, fs_id: int, user: str, reason: Optional[str] = None) -> Result:
        return self.repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, user, reason)

    def review_fs(self, fs_id: int, user: str, reason: Optional[str] = None) -> Result:
        return self.repo.update_statement_status(fs_id, FSStatus.REVIEWED, user, reason)

    def approve_fs(self, fs_id: int, user: str, reason: Optional[str] = None) -> Result:
        return self.repo.update_statement_status(fs_id, FSStatus.APPROVED, user, reason)

    def sign_fs(self, fs_id: int, user: str, reason: Optional[str] = None) -> Result:
        return self.repo.update_statement_status(fs_id, FSStatus.SIGNED, user, reason)

    def reject_fs(self, fs_id: int, user: str, reason: Optional[str] = None) -> Result:
        return self.repo.update_statement_status(fs_id, FSStatus.REJECTED, user, reason)

    # ── UC-FS-06: Versioning & audit ─────────────────────────────────

    def amend_fs(self, fs_id: int, user: str, reason: Optional[str] = None) -> Result:
        result = self.repo.update_statement_status(fs_id, FSStatus.AMENDED, user, reason)
        if result.is_success():
            self.repo.increment_version(fs_id)
        return result

    def get_audit_log(self, fs_id: int) -> List[Dict[str, Any]]:
        return self.repo.get_audit_log(fs_id)

    # ── UC-FS-07: Export ─────────────────────────────────────────────

    def export_fs(self, fs_id: int, fmt: str = "html") -> Result:
        fs = self.repo.get_statement(fs_id)
        if not fs:
            return Result.failure(ValidationError(ErrorCodes.FS_NOT_FOUND))

        if fmt not in ("html", "pdf", "xlsx"):
            return Result.failure(ValidationError(ErrorCodes.FS_UNSUPPORTED_FORMAT))

        if fs.status not in (FSStatus.APPROVED, FSStatus.SIGNED):
            if fmt == "pdf":
                return Result.failure(ValidationError(ErrorCodes.FS_NOT_APPROVED))

        return Result.success({"fs": fs, "format": fmt})

    # ── UC-FS-08: Mapping config ─────────────────────────────────────

    def create_mapping(self, mapping: FSAccountMapping) -> Result:
        try:
            return self.repo.create_mapping(mapping)
        except VASValidationError:
            raise
        except Exception as e:
            return Result.failure(VASValidationError(
                ErrorCodes.FS_MAPPING_NOT_FOUND, detail=str(e)))

    def get_mappings(self, statement_type: Optional[FinancialStatementType] = None,
                     fs_ma_so: Optional[str] = None) -> List[FSAccountMapping]:
        return self.repo.get_mappings(statement_type, fs_ma_so)

    def delete_mapping(self, mapping_id: int) -> Result:
        return self.repo.delete_mapping(mapping_id)

    # ── Generic FS CRUD ──────────────────────────────────────────────

    def get_statement(self, fs_id: int) -> Optional[FinancialStatement]:
        return self.repo.get_statement(fs_id)

    def list_statements(self, period: Optional[str] = None,
                         statement_type: Optional[FinancialStatementType] = None,
                         status: Optional[FSStatus] = None,
                         entity_id: Optional[int] = None,
                         limit: int = 100, offset: int = 0) -> List[FinancialStatement]:
        return self.repo.list_statements(period, statement_type, status,
                                          entity_id, limit, offset)

    def delete_statement(self, fs_id: int) -> Result:
        return self.repo.delete_statement(fs_id)
