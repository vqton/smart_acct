import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from infrastructure.models.coa_models import Base


class AssetTypeDB(str, enum.Enum):
    TANGIBLE = "tangible"
    INTANGIBLE = "intangible"
    FINANCE_LEASE = "finance_lease"
    BIOLOGICAL = "biological"
    INVESTMENT_PROPERTY = "investment_property"


class DepreciationMethodDB(str, enum.Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"


class AssetStatusDB(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FULLY_DEPRECIATED = "fully_depreciated"
    DISPOSED = "disposed"
    HELD_FOR_SALE = "held_for_sale"


class DisposalTypeDB(str, enum.Enum):
    SALE = "sale"
    LIQUIDATION = "liquidation"
    DONATION = "donation"
    THEFT = "theft"
    DESTRUCTION = "destruction"


class AdjustmentTypeDB(str, enum.Enum):
    UPGRADE = "upgrade"
    PARTIAL_DISMANTLE = "partial_dismantle"
    COST_CORRECTION = "cost_correction"
    IMPAIRMENT = "impairment"
    REVALUATION = "revaluation"


class BiologicalTypeDB(str, enum.Enum):
    PERIODIC_PRODUCER_LONG_TERM = "periodic_producer_long_term"
    ONE_TIME_PRODUCT = "one_time_product"
    SEASONAL_CROP = "seasonal_crop"


class GrowthStageDB(str, enum.Enum):
    IMMATURE = "immature"
    MATURE = "mature"


class AssetClassificationDB(str, enum.Enum):
    BUILDINGS_STRUCTURES = "buildings_structures"
    MACHINERY_EQUIPMENT = "machinery_equipment"
    TRANSPORT_TRANSMISSION = "transport_transmission"
    MANAGEMENT_EQUIPMENT = "management_equipment"
    PERENNIAL_PLANTS_LIVESTOCK = "perennial_plants_livestock"
    SOE_INFRASTRUCTURE = "soe_infrastructure"
    OTHER = "other"


class FundSourceDB(str, enum.Enum):
    OWNERS_EQUITY = "owners_equity"
    LOAN = "loan"
    GOVERNMENT_GRANT = "government_grant"
    WELFARE_FUND = "welfare_fund"
    RD_FUND = "rd_fund"
    CAPITAL_CONSTRUCTION = "capital_construction"
    OTHER = "other"


class UseTypeDB(str, enum.Enum):
    PRODUCTION = "production"
    ADMINISTRATION = "administration"
    SELLING = "selling"
    CONSTRUCTION = "construction"
    WELFARE = "welfare"
    RD = "rd"


class InventoryStatusDB(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class ProvisionTypeDB(str, enum.Enum):
    NEW = "new"
    REVERSAL = "reversal"


class FACategoryModel(Base):
    __tablename__ = "fa_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(300), nullable=False)
    parent_id = Column(Integer, ForeignKey("fa_categories.id"), nullable=True)
    useful_life_months = Column(Integer, nullable=True)
    depreciation_method = Column(SAEnum(DepreciationMethodDB), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    children = relationship("FACategoryModel", back_populates="parent", lazy="selectin",
                            cascade="all, delete-orphan")
    parent = relationship("FACategoryModel", back_populates="children", remote_side=[id], lazy="selectin")

    def __repr__(self) -> str:
        return f"<FACategoryModel(id={self.id}, code='{self.code}')>"


class FixedAssetModel(Base):
    __tablename__ = "fa_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    category_id = Column(Integer, ForeignKey("fa_categories.id"), nullable=False, index=True)
    asset_type = Column(SAEnum(AssetTypeDB), nullable=False)
    asset_classification = Column(SAEnum(AssetClassificationDB), nullable=False)
    original_cost = Column(Numeric(18, 2), nullable=False)
    accumulated_depreciation = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    residual_value = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    useful_life_months = Column(Integer, nullable=False)
    depreciation_method = Column(SAEnum(DepreciationMethodDB), nullable=False)
    acquisition_date = Column(Date, nullable=False)
    in_use_date = Column(Date, nullable=False)
    department_id = Column(Integer, nullable=True)
    location = Column(String(200), nullable=True)
    status = Column(SAEnum(AssetStatusDB), default=AssetStatusDB.ACTIVE, nullable=False)
    fund_source = Column(SAEnum(FundSourceDB), nullable=False)
    use_type = Column(SAEnum(UseTypeDB), nullable=False)
    supplier = Column(String(300), nullable=True)
    invoice_ref = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    category = relationship("FACategoryModel", lazy="selectin")
    depreciation_records = relationship("DepreciationRecordModel", back_populates="asset",
                                        lazy="selectin", cascade="all, delete-orphan")
    adjustments = relationship("FAAdjustmentModel", back_populates="asset",
                               lazy="selectin", cascade="all, delete-orphan")
    disposals = relationship("FADisposalModel", back_populates="asset",
                             lazy="selectin", cascade="all, delete-orphan")
    transfers = relationship("FATransferModel", back_populates="asset",
                             lazy="selectin", cascade="all, delete-orphan")
    spare_parts = relationship("FASparePartModel", back_populates="asset",
                               lazy="selectin", cascade="all, delete-orphan")
    components = relationship("FAComponentModel", back_populates="asset",
                              lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<FixedAssetModel(id={self.id}, code='{self.code}')>"


class DepreciationRecordModel(Base):
    __tablename__ = "fa_depreciation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("fa_assets.id"), nullable=False, index=True)
    period = Column(String(7), nullable=False, index=True)
    depreciation_date = Column(Date, nullable=False)
    depreciation_amount = Column(Numeric(18, 2), nullable=False)
    accumulated_after = Column(Numeric(18, 2), nullable=False)
    net_book_value_after = Column(Numeric(18, 2), nullable=False)
    is_manual = Column(Boolean, default=False, nullable=False)
    notes = Column(String(500), nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    asset = relationship("FixedAssetModel", back_populates="depreciation_records", lazy="selectin")

    def __repr__(self) -> str:
        return f"<DepreciationRecordModel(id={self.id}, asset={self.asset_id}, period='{self.period}')>"


class FAAdjustmentModel(Base):
    __tablename__ = "fa_adjustments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("fa_assets.id"), nullable=False, index=True)
    adjustment_type = Column(SAEnum(AdjustmentTypeDB), nullable=False)
    adjustment_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    previous_cost = Column(Numeric(18, 2), nullable=False)
    new_cost = Column(Numeric(18, 2), nullable=False)
    reason = Column(Text, nullable=False)
    reference_number = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    asset = relationship("FixedAssetModel", back_populates="adjustments", lazy="selectin")

    def __repr__(self) -> str:
        return f"<FAAdjustmentModel(id={self.id}, type='{self.adjustment_type}', asset={self.asset_id})>"


class FADisposalModel(Base):
    __tablename__ = "fa_disposals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("fa_assets.id"), nullable=False, index=True)
    disposal_type = Column(SAEnum(DisposalTypeDB), nullable=False)
    disposal_date = Column(Date, nullable=False)
    net_book_value = Column(Numeric(18, 2), nullable=False)
    proceeds = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    gain_loss = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    reason = Column(Text, nullable=False)
    counterparty = Column(String(300), nullable=True)
    invoice_ref = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    asset = relationship("FixedAssetModel", back_populates="disposals", lazy="selectin")

    def __repr__(self) -> str:
        return f"<FADisposalModel(id={self.id}, type='{self.disposal_type}', asset={self.asset_id})>"


class FAInventoryModel(Base):
    __tablename__ = "fa_inventories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_date = Column(Date, nullable=False, index=True)
    inventory_number = Column(String(50), unique=True, nullable=False, index=True)
    department_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(SAEnum(InventoryStatusDB), default=InventoryStatusDB.OPEN, nullable=False)
    conducted_by = Column(String(100), nullable=False)
    approved_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    lines = relationship("FAInventoryLineModel", back_populates="inventory",
                         lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<FAInventoryModel(id={self.id}, number='{self.inventory_number}')>"


class FAInventoryLineModel(Base):
    __tablename__ = "fa_inventory_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_id = Column(Integer, ForeignKey("fa_inventories.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("fa_assets.id"), nullable=False, index=True)
    book_quantity = Column(Integer, default=1, nullable=False)
    actual_quantity = Column(Integer, nullable=False)
    book_cost = Column(Numeric(18, 2), nullable=False)
    actual_cost = Column(Numeric(18, 2), nullable=False)
    difference_quantity = Column(Integer, default=0, nullable=False)
    difference_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    notes = Column(String(500), nullable=True)

    inventory = relationship("FAInventoryModel", back_populates="lines", lazy="selectin")
    asset = relationship("FixedAssetModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<FAInventoryLineModel(id={self.id}, inventory={self.inventory_id}, asset={self.asset_id})>"


class FATransferModel(Base):
    __tablename__ = "fa_transfers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("fa_assets.id"), nullable=False, index=True)
    transfer_date = Column(Date, nullable=False)
    from_department_id = Column(Integer, nullable=True)
    to_department_id = Column(Integer, nullable=True)
    from_location = Column(String(200), nullable=True)
    to_location = Column(String(200), nullable=True)
    reason = Column(Text, nullable=False)
    approved_by = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    asset = relationship("FixedAssetModel", back_populates="transfers", lazy="selectin")

    def __repr__(self) -> str:
        return f"<FATransferModel(id={self.id}, asset={self.asset_id})>"


class FASparePartModel(Base):
    __tablename__ = "fa_spare_parts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("fa_assets.id"), nullable=False, index=True)
    part_code = Column(String(50), nullable=False, index=True)
    part_name = Column(String(300), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(18, 2), nullable=False)
    total_cost = Column(Numeric(18, 2), nullable=False)
    replacement_date = Column(Date, nullable=True)
    expected_life_months = Column(Integer, nullable=True)
    supplier = Column(String(300), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    asset = relationship("FixedAssetModel", back_populates="spare_parts", lazy="selectin")

    def __repr__(self) -> str:
        return f"<FASparePartModel(id={self.id}, code='{self.part_code}')>"


class FAComponentModel(Base):
    __tablename__ = "fa_components"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("fa_assets.id"), nullable=False, index=True)
    component_name = Column(String(300), nullable=False)
    component_code = Column(String(50), nullable=True)
    original_cost = Column(Numeric(18, 2), nullable=False)
    accumulated_depreciation = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    useful_life_months = Column(Integer, nullable=True)
    depreciation_method = Column(SAEnum(DepreciationMethodDB), nullable=True)
    acquisition_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    asset = relationship("FixedAssetModel", back_populates="components", lazy="selectin")

    def __repr__(self) -> str:
        return f"<FAComponentModel(id={self.id}, name='{self.component_name}')>"


class BiologicalAssetModel(Base):
    __tablename__ = "fa_biological_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("fa_assets.id"), nullable=False, index=True)
    biological_type = Column(SAEnum(BiologicalTypeDB), nullable=False)
    growth_stage = Column(SAEnum(GrowthStageDB), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=False)
    location = Column(String(200), nullable=True)
    planted_date = Column(Date, nullable=True)
    expected_harvest_date = Column(Date, nullable=True)
    harvest_cycle_months = Column(Integer, nullable=True)
    maturity_months = Column(Integer, nullable=True)
    yield_estimate = Column(Numeric(18, 2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    asset = relationship("FixedAssetModel", lazy="selectin")
    provisions = relationship("BiologicalProvisionModel", back_populates="biological_asset",
                              lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BiologicalAssetModel(id={self.id}, type='{self.biological_type}')>"


class BiologicalProvisionModel(Base):
    __tablename__ = "fa_biological_provisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    biological_asset_id = Column(Integer, ForeignKey("fa_biological_assets.id"), nullable=False, index=True)
    provision_type = Column(SAEnum(ProvisionTypeDB), nullable=False)
    provision_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    reason = Column(Text, nullable=False)
    reference_number = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    biological_asset = relationship("BiologicalAssetModel", back_populates="provisions", lazy="selectin")

    def __repr__(self) -> str:
        return f"<BiologicalProvisionModel(id={self.id}, type='{self.provision_type}', amount={self.amount})>"
