export enum FaAssetType {
  Tangible = "tangible",
  Intangible = "intangible",
  FinanceLease = "finance_lease",
  OperatingLease = "operating_lease",
  InvestmentProperty = "investment_property",
  ConstructionInProgress = "construction_in_progress",
  RightOfUse = "right_of_use",
  LandUseRight = "land_use_right",
  Software = "software",
  License = "license",
  Patent = "patent",
  Copyright = "copyright",
  Building = "building",
  Machinery = "machinery",
  Vehicle = "vehicle",
  OfficeEquipment = "office_equipment",
  ItEquipment = "it_equipment",
  Furniture = "furniture",
  Infrastructure = "infrastructure",
  Specialized = "specialized",
  Tool = "tool",
  LowValue = "low_value",
  CapitalizedExpense = "capitalized_expense",
  Other = "other",
}

export enum FaAssetStatus {
  Draft = "draft",
  PendingAcquisition = "pending_acquisition",
  Acquired = "acquired",
  PendingCapitalization = "pending_capitalization",
  Capitalized = "capitalized",
  InUse = "in_use",
  Suspended = "suspended",
  UnderMaintenance = "under_maintenance",
  FullyDepreciated = "fully_depreciated",
  PendingDisposal = "pending_disposal",
  Disposed = "disposed",
  Retired = "retired",
  Sold = "sold",
  Scrapped = "scrapped",
  Donated = "donated",
  Lost = "lost",
  Destroyed = "destroyed",
  WrittenOff = "written_off",
  Transferred = "transferred",
  Decommissioned = "decommissioned",
  Archived = "archived",
}

export enum FaAcquisitionType {
  Purchase = "purchase",
  SelfConstructed = "self_constructed",
  FinanceLease = "finance_lease",
  OperatingLease = "operating_lease",
  Contribution = "contribution",
  Donation = "donation",
  Exchange = "exchange",
  Transfer = "transfer",
  Merger = "merger",
  Surplus = "surplus",
  GovernmentAllocation = "government_allocation",
  CapitalizedExpense = "capitalized_expense",
  Other = "other",
}

export enum FaDepreciationMethod {
  StraightLine = "straight_line",
  DecliningBalance = "declining_balance",
  DoubleDecliningBalance = "double_declining_balance",
  SumOfYearsDigits = "sum_of_years_digits",
  UnitsOfProduction = "units_of_production",
  CustomFormula = "custom_formula",
  Immediate = "immediate",
  None = "none",
}

export enum FaDepreciationArea {
  Book = "book",
  Tax = "tax",
  Ifrs = "ifrs",
  Management = "management",
  Statutory = "statutory",
}

export enum FaDepreciationRunStatus {
  Pending = "pending",
  InProgress = "in_progress",
  Completed = "completed",
  Failed = "failed",
  Reversed = "reversed",
}

export enum FaDisposalType {
  Sale = "sale",
  Scrap = "scrap",
  Donation = "donation",
  Destruction = "destruction",
  Theft = "theft",
  Loss = "loss",
  TradeIn = "trade_in",
  Retirement = "retirement",
  Transfer = "transfer",
  Partial = "partial",
  Bulk = "bulk",
}

export enum FaRevaluationType {
  Upward = "upward",
  Downward = "downward",
  IndexBased = "index_based",
  MarketValue = "market_value",
  ProfessionalValuation = "professional_valuation",
  Bulk = "bulk",
}

export enum FaImpairmentType {
  External = "external",
  Internal = "internal",
  PhysicalDamage = "physical_damage",
  TechnologicalObsolescence = "technological_obsolescence",
  MarketDecline = "market_decline",
  Regulatory = "regulatory",
  Other = "other",
}

export enum FaLeaseType {
  Finance = "finance",
  Operating = "operating",
  SaleLeaseback = "sale_leaseback",
  DirectFinancing = "direct_financing",
}

export enum FaLeasePaymentFrequency {
  Monthly = "monthly",
  Quarterly = "quarterly",
  SemiAnnual = "semi_annual",
  Annual = "annual",
  Custom = "custom",
}

export enum FaMaintenanceType {
  Preventive = "preventive",
  Corrective = "corrective",
  Predictive = "predictive",
  Emergency = "emergency",
  Inspection = "inspection",
  Overhaul = "overhaul",
  Refurbishment = "refurbishment",
}

export enum FaMaintenanceStatus {
  Planned = "planned",
  Scheduled = "scheduled",
  InProgress = "in_progress",
  Completed = "completed",
  Cancelled = "cancelled",
  Postponed = "postponed",
}

export enum FaVerificationMethod {
  Barcode = "barcode",
  QrCode = "qr_code",
  Rfid = "rfid",
  Manual = "manual",
  Mobile = "mobile",
  Gps = "gps",
}

export enum FaVerificationStatus {
  Planned = "planned",
  InProgress = "in_progress",
  Completed = "completed",
  Approved = "approved",
  Cancelled = "cancelled",
}

export enum FaAssetCategory {
  A = "a",
  B = "b",
  C = "c",
  D = "d",
}

export enum FaCostAllocationMethod {
  Manual = "manual",
  Percentage = "percentage",
  Equal = "equal",
  ByArea = "by_area",
  ByUsage = "by_usage",
  ByHeadcount = "by_headcount",
  ByRevenue = "by_revenue",
}

export enum FaSplitMergeType {
  Split = "split",
  Merge = "merge",
}
