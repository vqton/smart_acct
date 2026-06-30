from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, ValidationError, _quantize_vnd


class AssetType(str, Enum):
    TANGIBLE = "tangible"
    INTANGIBLE = "intangible"
    FINANCE_LEASE = "finance_lease"
    BIOLOGICAL = "biological"
    INVESTMENT_PROPERTY = "investment_property"


class DepreciationMethod(str, Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"


class AssetStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FULLY_DEPRECIATED = "fully_depreciated"
    DISPOSED = "disposed"
    HELD_FOR_SALE = "held_for_sale"


class DisposalType(str, Enum):
    SALE = "sale"
    LIQUIDATION = "liquidation"
    DONATION = "donation"
    THEFT = "theft"
    DESTRUCTION = "destruction"


class AdjustmentType(str, Enum):
    UPGRADE = "upgrade"
    PARTIAL_DISMANTLE = "partial_dismantle"
    COST_CORRECTION = "cost_correction"
    IMPAIRMENT = "impairment"
    REVALUATION = "revaluation"


class BiologicalType(str, Enum):
    PERIODIC_PRODUCER_LONG_TERM = "periodic_producer_long_term"
    ONE_TIME_PRODUCT = "one_time_product"
    SEASONAL_CROP = "seasonal_crop"


class GrowthStage(str, Enum):
    IMMATURE = "immature"
    MATURE = "mature"


class AssetClassification(str, Enum):
    BUILDINGS_STRUCTURES = "buildings_structures"
    MACHINERY_EQUIPMENT = "machinery_equipment"
    TRANSPORT_TRANSMISSION = "transport_transmission"
    MANAGEMENT_EQUIPMENT = "management_equipment"
    PERENNIAL_PLANTS_LIVESTOCK = "perennial_plants_livestock"
    SOE_INFRASTRUCTURE = "soe_infrastructure"
    OTHER = "other"


class FundSource(str, Enum):
    OWNERS_EQUITY = "owners_equity"
    LOAN = "loan"
    GOVERNMENT_GRANT = "government_grant"
    WELFARE_FUND = "welfare_fund"
    RD_FUND = "rd_fund"
    CAPITAL_CONSTRUCTION = "capital_construction"
    OTHER = "other"


class UseType(str, Enum):
    PRODUCTION = "production"
    ADMINISTRATION = "administration"
    SELLING = "selling"
    CONSTRUCTION = "construction"
    WELFARE = "welfare"
    RD = "rd"


class InventoryStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class ProvisionType(str, Enum):
    NEW = "new"
    REVERSAL = "reversal"


class FACategory(BaseModel):
    id: Optional[int] = None
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    asset_type: AssetType
    asset_classification: AssetClassification
    default_depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    default_useful_life_min: Optional[int] = Field(None, ge=1)
    default_useful_life_max: Optional[int] = Field(None, ge=1)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v.strip():
            raise ValidationError("FA_CODE_REQUIRED")
        return v.strip()


class FixedAsset(BaseModel):
    id: Optional[int] = None
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    category_id: int
    asset_type: AssetType
    asset_classification: AssetClassification
    original_cost: Decimal = Field(..., gt=Decimal("0"))
    accumulated_depreciation: Decimal = Decimal("0")
    residual_value: Decimal = Decimal("0")
    carrying_amount: Decimal = Decimal("0")
    useful_life_months: int = Field(..., ge=12)
    depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    acquisition_date: date
    in_use_date: date
    department_id: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=200)
    status: AssetStatus = AssetStatus.ACTIVE
    fund_source: FundSource = FundSource.OWNERS_EQUITY
    use_type: UseType = UseType.PRODUCTION
    supplier: Optional[str] = Field(None, max_length=200)
    invoice_ref: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @field_validator("original_cost", "accumulated_depreciation", "residual_value", "carrying_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v.strip():
            raise ValidationError("FA_CODE_REQUIRED")
        return v.strip()

    @model_validator(mode="after")
    def validate_dates(self):
        if self.in_use_date < self.acquisition_date:
            raise ValidationError("FA_DATE_IN_USE_AFTER_ACQUISITION")
        return self

    @model_validator(mode="after")
    def compute_carrying_amount(self):
        self.carrying_amount = _quantize_vnd(self.original_cost - self.accumulated_depreciation)
        return self


class DepreciationRecord(BaseModel):
    id: Optional[int] = None
    asset_id: int
    period: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    depreciation_amount: Decimal
    accumulated_total: Decimal
    nbv: Decimal
    is_posted: bool = False
    posted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("depreciation_amount", "accumulated_total", "nbv")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class FAAdjustment(BaseModel):
    id: Optional[int] = None
    asset_id: int
    adjustment_type: AdjustmentType
    amount: Decimal
    previous_cost: Decimal
    new_cost: Decimal
    previous_depreciation: Decimal = Decimal("0")
    new_depreciation: Decimal = Decimal("0")
    reason: str = Field(..., min_length=1, max_length=500)
    document_ref: Optional[str] = Field(None, max_length=100)
    effective_date: date
    appraised_by: Optional[str] = Field(None, max_length=200)
    appraisal_date: Optional[date] = None
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("amount", "previous_cost", "new_cost", "previous_depreciation", "new_depreciation")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class FADisposal(BaseModel):
    id: Optional[int] = None
    asset_id: int
    disposal_type: DisposalType
    disposal_date: date
    proceeds: Decimal = Decimal("0")
    costs: Decimal = Decimal("0")
    nbv_at_disposal: Decimal
    gain_loss: Decimal = Decimal("0")
    buyer_info: Optional[str] = Field(None, max_length=300)
    reason: str = Field(..., min_length=1, max_length=500)
    approved_by: Optional[str] = Field(None, max_length=100)
    document_ref: Optional[str] = Field(None, max_length=100)
    is_vat_applied: bool = False
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("proceeds", "costs", "nbv_at_disposal", "gain_loss")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @model_validator(mode="after")
    def compute_gain_loss(self):
        self.gain_loss = _quantize_vnd(self.proceeds - self.costs - self.nbv_at_disposal)
        return self


class FAInventoryLine(BaseModel):
    id: Optional[int] = None
    inventory_id: Optional[int] = None
    asset_id: int
    book_quantity: int = 1
    physical_quantity: int = 0
    difference: int = 0
    reason: Optional[str] = Field(None, max_length=500)
    resolution: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def compute_difference(self):
        self.difference = self.physical_quantity - self.book_quantity
        return self


class FAInventory(BaseModel):
    id: Optional[int] = None
    inventory_date: date
    department_id: str = Field(..., max_length=50)
    asset_count_book: int = 0
    asset_count_physical: int = 0
    surplus_count: int = 0
    deficit_count: int = 0
    status: InventoryStatus = InventoryStatus.OPEN
    notes: Optional[str] = Field(None, max_length=1000)
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    lines: List[FAInventoryLine] = Field(default_factory=list)

    @model_validator(mode="after")
    def compute_counts(self):
        self.surplus_count = max(0, self.asset_count_physical - self.asset_count_book)
        self.deficit_count = max(0, self.asset_count_book - self.asset_count_physical)
        return self


class FATransfer(BaseModel):
    id: Optional[int] = None
    asset_id: int
    from_department_id: str = Field(..., max_length=50)
    to_department_id: str = Field(..., max_length=50)
    from_location: Optional[str] = Field(None, max_length=200)
    to_location: Optional[str] = Field(None, max_length=200)
    effective_date: date
    reason: str = Field(..., min_length=1, max_length=500)
    created_by: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_different_departments(self):
        if self.from_department_id == self.to_department_id:
            raise ValidationError("FA_TRANSFER_SAME_DEPARTMENT")
        return self


class FASparePart(BaseModel):
    id: Optional[int] = None
    asset_id: int
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    quantity: int = 1
    unit: str = Field(..., max_length=50)
    value: Decimal = Decimal("0")

    @field_validator("value")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class FAComponent(BaseModel):
    id: Optional[int] = None
    asset_id: int
    name: str = Field(..., min_length=1, max_length=200)
    original_cost: Decimal = Decimal("0")
    useful_life_months: Optional[int] = Field(None, ge=1)
    depreciation_method: Optional[DepreciationMethod] = None

    @field_validator("original_cost")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class BiologicalAsset(BaseModel):
    id: Optional[int] = None
    asset_id: int
    biological_type: BiologicalType
    growth_stage: GrowthStage = GrowthStage.IMMATURE
    quantity: Decimal = Field(default=Decimal("1"), ge=Decimal("0"))
    unit: str = Field(..., max_length=50)
    planting_date: date
    expected_harvest_date: Optional[date] = None
    provision_amount: Decimal = Decimal("0")

    @field_validator("provision_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)

    @model_validator(mode="after")
    def validate_harvest_after_planting(self):
        if self.expected_harvest_date and self.expected_harvest_date < self.planting_date:
            raise ValidationError("FA_HARVEST_AFTER_PLANTING")
        return self


class BiologicalProvision(BaseModel):
    id: Optional[int] = None
    biological_asset_id: int
    period: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    provision_amount: Decimal
    provision_type: ProvisionType = ProvisionType.NEW
    reason: str = Field(..., min_length=1, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("provision_amount")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)


class DepreciationConfig(BaseModel):
    id: Optional[int] = None
    asset_id: int
    method: DepreciationMethod
    useful_life_months: int = Field(..., ge=1)
    residual_value: Decimal = Decimal("0")
    switch_to_sl_when_lower: bool = False

    @field_validator("residual_value")
    @classmethod
    def validate_amt(cls, v):
        return _quantize_vnd(v)
