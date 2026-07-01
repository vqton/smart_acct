from typing import List, Dict, Optional, Any, ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
import re

from domain.i18n import ErrorCodes
from domain.common import VASValidationError, ValidationError, _quantize_vnd


class FinancialStatementType(str, Enum):
    BALANCE_SHEET_GC = "B01_DN"
    BALANCE_SHEET_NGC = "B01_DNKLT"
    INCOME_STATEMENT_GC = "B02_DN"
    INCOME_STATEMENT_NGC = "B02_DNKLT"
    CASH_FLOW_GC = "B03_DN"
    CASH_FLOW_NGC = "B03_DNKLT"
    NOTES_GC = "B09_DN"
    NOTES_NGC = "B09_DNKLT"
    INTERIM_FULL_BALANCE = "B01a_DN"
    INTERIM_FULL_INCOME = "B02a_DN"
    INTERIM_FULL_CASHFLOW = "B03a_DN"
    INTERIM_FULL_NOTES = "B09a_DN"
    INTERIM_CONDENSED_BALANCE = "B01b_DN"
    INTERIM_CONDENSED_INCOME = "B02b_DN"
    INTERIM_CONDENSED_CASHFLOW = "B03b_DN"

    @classmethod
    def is_going_concern(cls, v: str) -> bool:
        return v in ("B01_DN", "B02_DN", "B03_DN", "B09_DN")

    @classmethod
    def is_non_going_concern(cls, v: str) -> bool:
        return v in ("B01_DNKLT", "B02_DNKLT", "B03_DNKLT", "B09_DNKLT")


class FSStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    SIGNED = "SIGNED"
    REJECTED = "REJECTED"
    AMENDED = "AMENDED"


class FSCashFlowMethod(str, Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"


class FSLineItem(BaseModel):
    id: Optional[int] = None
    fs_id: Optional[int] = None
    ma_so: str = Field(..., min_length=1, max_length=10)
    ten_chi_tieu: str = Field(..., min_length=1, max_length=500)
    so_thu_tu: int = Field(..., ge=0)
    parent_ma_so: Optional[str] = None
    current_year: Decimal = Decimal("0.00")
    previous_year: Optional[Decimal] = None
    is_subtotal: bool = False
    is_calculated: bool = False
    calculation_formula: Optional[str] = None
    thuyet_minh: Optional[str] = None

    @field_validator("current_year", "previous_year")
    @classmethod
    def validate_amt(cls, v):
        if v is None:
            return v
        return _quantize_vnd(v)


class FSAccountMapping(BaseModel):
    id: Optional[int] = None
    fs_ma_so: str = Field(..., min_length=1, max_length=10)
    account_code: str = Field(..., min_length=1, max_length=20)
    weight: Decimal = Decimal("1.00")
    direction: str = "both"
    statement_type: FinancialStatementType

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v):
        if v not in ("debit", "credit", "both"):
            raise ValidationError(ErrorCodes.FS_MAPPING_DIRECTION_INVALID)
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v):
        if v <= 0:
            raise ValidationError(ErrorCodes.FS_MAPPING_WEIGHT_INVALID)
        return v


class FSAuditLog(BaseModel):
    id: Optional[int] = None
    fs_id: int
    action: str = Field(..., max_length=50)
    user: str = Field(..., max_length=100)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Optional[str] = None
    version: int = 1


class FSApprovalAction(BaseModel):
    action: str = Field(..., pattern=r"^(submit|approve|reject|sign)$")
    user: str = Field(..., min_length=1, max_length=100)
    reason: Optional[str] = Field(None, max_length=1000)


class FinancialStatement(BaseModel):
    id: Optional[int] = None
    entity_id: int = 1
    period: str = Field(..., pattern=r"^\d{4}(-\d{2})?$")
    statement_type: FinancialStatementType
    lines: List[FSLineItem] = Field(default_factory=list)
    status: FSStatus = FSStatus.DRAFT
    version: int = 1
    cash_flow_method: Optional[FSCashFlowMethod] = None
    approved_by: Optional[str] = None
    approval_date: Optional[date] = None
    signed_by: Optional[str] = None
    signed_date: Optional[date] = None
    generated_by: Optional[str] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_consolidated: bool = False
    consolidation_group_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    VALID_TRANSITIONS: ClassVar[Dict[FSStatus, List[FSStatus]]] = {
        FSStatus.DRAFT: [FSStatus.IN_REVIEW, FSStatus.AMENDED],
        FSStatus.IN_REVIEW: [FSStatus.REVIEWED, FSStatus.REJECTED],
        FSStatus.REVIEWED: [FSStatus.APPROVED, FSStatus.REJECTED],
        FSStatus.APPROVED: [FSStatus.SIGNED, FSStatus.REJECTED, FSStatus.AMENDED],
        FSStatus.SIGNED: [FSStatus.AMENDED],
        FSStatus.REJECTED: [FSStatus.DRAFT],
        FSStatus.AMENDED: [FSStatus.DRAFT],
    }

    B01_DN_LINE_ITEMS: ClassVar[List[Dict[str, Any]]] = [
        {"ma_so": "100", "ten": "TÀI SẢN NGẮN HẠN", "subtotal": True},
        {"ma_so": "110", "ten": "Tiền và các khoản tương đương tiền", "parent": "100", "subtotal": True},
        {"ma_so": "111", "ten": "Tiền", "parent": "110"},
        {"ma_so": "112", "ten": "Các khoản tương đương tiền", "parent": "110"},
        {"ma_so": "120", "ten": "Đầu tư tài chính ngắn hạn", "parent": "100"},
        {"ma_so": "130", "ten": "Các khoản phải thu ngắn hạn", "parent": "100"},
        {"ma_so": "140", "ten": "Hàng tồn kho", "parent": "100"},
        {"ma_so": "150", "ten": "Tài sản ngắn hạn khác", "parent": "100"},
        {"ma_so": "200", "ten": "TÀI SẢN DÀI HẠN", "subtotal": True},
        {"ma_so": "210", "ten": "Các khoản phải thu dài hạn", "parent": "200"},
        {"ma_so": "220", "ten": "Tài sản cố định", "parent": "200"},
        {"ma_so": "230", "ten": "Bất động sản đầu tư", "parent": "200"},
        {"ma_so": "240", "ten": "Tài sản dở dang dài hạn", "parent": "200"},
        {"ma_so": "250", "ten": "Đầu tư tài chính dài hạn", "parent": "200"},
        {"ma_so": "260", "ten": "Tài sản dài hạn khác", "parent": "200"},
        {"ma_so": "270", "ten": "TỔNG TÀI SẢN", "subtotal": True},
        {"ma_so": "300", "ten": "NỢ PHẢI TRẢ", "subtotal": True},
        {"ma_so": "310", "ten": "Nợ ngắn hạn", "parent": "300"},
        {"ma_so": "330", "ten": "Nợ dài hạn", "parent": "300"},
        {"ma_so": "400", "ten": "VỐN CHỦ SỞ HỮU", "subtotal": True},
        {"ma_so": "410", "ten": "Vốn góp của chủ sở hữu", "parent": "400"},
        {"ma_so": "420", "ten": "Thặng dư vốn cổ phần", "parent": "400"},
        {"ma_so": "430", "ten": "Lợi nhuận sau thuế chưa phân phối", "parent": "400"},
        {"ma_so": "440", "ten": "TỔNG NGUỒN VỐN", "subtotal": True},
    ]

    B02_DN_LINE_ITEMS: ClassVar[List[Dict[str, Any]]] = [
        {"ma_so": "01", "ten": "Doanh thu bán hàng và cung cấp dịch vụ"},
        {"ma_so": "02", "ten": "Các khoản giảm trừ doanh thu"},
        {"ma_so": "10", "ten": "Doanh thu thuần", "subtotal": True},
        {"ma_so": "11", "ten": "Giá vốn hàng bán"},
        {"ma_so": "20", "ten": "Lợi nhuận gộp", "subtotal": True},
        {"ma_so": "21", "ten": "Doanh thu hoạt động tài chính"},
        {"ma_so": "22", "ten": "Chi phí tài chính"},
        {"ma_so": "23", "ten": "Chi phí bán hàng"},
        {"ma_so": "24", "ten": "Chi phí quản lý doanh nghiệp"},
        {"ma_so": "30", "ten": "Lợi nhuận thuần từ HĐKD", "subtotal": True},
        {"ma_so": "40", "ten": "Thu nhập khác"},
        {"ma_so": "41", "ten": "Chi phí khác"},
        {"ma_so": "50", "ten": "Lợi nhuận kế toán trước thuế", "subtotal": True},
        {"ma_so": "51", "ten": "Chi phí thuế TNDN hiện hành"},
        {"ma_so": "52", "ten": "Chi phí thuế TNDN hoãn lại"},
        {"ma_so": "60", "ten": "Lợi nhuận sau thuế TNDN", "subtotal": True},
    ]

    @field_validator("period")
    @classmethod
    def validate_period(cls, v):
        if not re.match(r"^\d{4}(-\d{2})?$", v):
            raise ValidationError(ErrorCodes.PERIOD_FS_FORMAT)
        if len(v) == 7:
            try:
                month = int(v.split("-")[1])
                if not (1 <= month <= 12):
                    raise ValidationError(ErrorCodes.PERIOD_FS_MONTH)
            except (ValueError, IndexError):
                raise ValidationError(ErrorCodes.PERIOD_FS_INVALID)
        return v

    @model_validator(mode="after")
    def validate_cash_flow_method(self):
        if self.statement_type in (FinancialStatementType.CASH_FLOW_GC, FinancialStatementType.CASH_FLOW_NGC):
            if not self.cash_flow_method:
                raise ValidationError(ErrorCodes.FS_CASH_FLOW_METHOD_REQUIRED)
        return self

    def can_transition_to(self, target: FSStatus) -> bool:
        allowed = self.VALID_TRANSITIONS.get(self.status, [])
        return target in allowed

    def get_line_by_ma_so(self, ma_so: str) -> Optional[FSLineItem]:
        for line in self.lines:
            if line.ma_so == ma_so:
                return line
        return None

    def get_subtotals(self) -> Dict[str, Decimal]:
        result: Dict[str, Decimal] = {}
        balance_sheet_codes = {item["ma_so"] for item in self.B01_DN_LINE_ITEMS if item.get("subtotal")}
        income_codes = {item["ma_so"] for item in self.B02_DN_LINE_ITEMS if item.get("subtotal")}
        for line in self.lines:
            if line.ma_so in balance_sheet_codes or line.ma_so in income_codes:
                result[line.ma_so] = line.current_year
        return result

    def verify_balance_sheet(self) -> bool:
        if self.statement_type not in (FinancialStatementType.BALANCE_SHEET_GC, FinancialStatementType.BALANCE_SHEET_NGC):
            return True
        ts_line = self.get_line_by_ma_so("270")
        nv_line = self.get_line_by_ma_so("440")
        if ts_line and nv_line:
            return abs(ts_line.current_year - nv_line.current_year) <= Decimal("0.001")
        return True

    DIFF_THRESHOLD_PCT: ClassVar[Decimal] = Decimal("20")


class FSLineTemplate(BaseModel):
    ma_so: str
    ten_chi_tieu: str
    parent_ma_so: Optional[str] = None
    is_subtotal: bool = False
    children: List["FSLineTemplate"] = Field(default_factory=list)


class FSConsolidationGroup(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    parent_entity_id: int
    consolidation_method: str = "full"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FSConsolidationMember(BaseModel):
    id: Optional[int] = None
    group_id: int
    entity_id: int
    ownership_percentage: Decimal = Decimal("100.00")
    consolidation_method: str = "full"
