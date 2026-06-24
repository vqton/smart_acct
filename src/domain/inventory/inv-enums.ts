export enum ItemType {
  Inventory = "inventory",
  Service = "service",
  NonStock = "non_stock",
  Consignment = "consignment",
  FixedAsset = "fixed_asset",
}

export enum ItemStatus {
  Active = "active",
  Inactive = "inactive",
  Discontinued = "discontinued",
  Obsolete = "obsolete",
}

export enum ItemCategory {
  RawMaterial = "raw_material",
  SemiFinished = "semi_finished",
  FinishedGood = "finished_good",
  WIP = "wip",
  Packaging = "packaging",
  Supplies = "supplies",
  Trading = "trading",
  Service = "service",
  Asset = "asset",
}

export enum ItemValuationMethod {
  FIFO = "fifo",
  MovingAverage = "moving_average",
  WeightedAverage = "weighted_average",
  Standard = "standard",
  SpecificIdentification = "specific_identification",
}

export enum LotControl {
  None = "none",
  Lot = "lot",
  Serial = "serial",
  Both = "both",
}

export enum WarehouseType {
  Main = "main",
  DistributionCenter = "distribution_center",
  Store = "store",
  Transit = "transit",
  Consignment = "consignment",
  Virtual = "virtual",
}

export enum WarehouseStatus {
  Active = "active",
  Inactive = "inactive",
  Closed = "closed",
}

export enum LocationType {
  Zone = "zone",
  Area = "area",
  Aisle = "aisle",
  Rack = "rack",
  Shelf = "shelf",
  Bin = "bin",
  Dock = "dock",
  Staging = "staging",
  Quarantine = "quarantine",
}

export enum LocationStatus {
  Active = "active",
  Inactive = "inactive",
  Blocked = "blocked",
  Full = "full",
}

export enum StorageType {
  Dry = "dry",
  Cold = "cold",
  Frozen = "frozen",
  Hazardous = "hazardous",
  ClimateControlled = "climate_controlled",
}

export enum InventoryTransactionType {
  GoodsReceipt = "goods_receipt",
  GoodsIssue = "goods_issue",
  TransferOut = "transfer_out",
  TransferIn = "transfer_in",
  AdjustmentIncrease = "adjustment_increase",
  AdjustmentDecrease = "adjustment_decrease",
  WriteOff = "write_off",
  WriteOn = "write_on",
  ReturnToVendor = "return_to_vendor",
  CustomerReturn = "customer_return",
  ProductionConsumption = "production_consumption",
  ProductionReceipt = "production_receipt",
  Scrap = "scrap",
  Sample = "sample",
  Promotional = "promotional",
  InternalConsumption = "internal_consumption",
  OpeningBalance = "opening_balance",
  Reversal = "reversal",
  Revaluation = "revaluation",
  LandedCost = "landed_cost",
}

export enum InventoryTransactionStatus {
  Draft = "draft",
  Submitted = "submitted",
  Approved = "approved",
  Posted = "posted",
  Reversed = "reversed",
  Cancelled = "cancelled",
}

export enum MovementStatus {
  Pending = "pending",
  Reserved = "reserved",
  Allocated = "allocated",
  Picked = "picked",
  Packed = "packed",
  Shipped = "shipped",
  Received = "received",
  Returned = "returned",
  Damaged = "damaged",
  Lost = "lost",
}

export enum StockStatus {
  Available = "available",
  Reserved = "reserved",
  Allocated = "allocated",
  InTransit = "in_transit",
  OnOrder = "on_order",
  Quarantine = "quarantine",
  QualityHold = "quality_hold",
  InspectionHold = "inspection_hold",
  Blocked = "blocked",
  Damaged = "damaged",
  Returned = "returned",
}

export enum CountStatus {
  Planned = "planned",
  InProgress = "in_progress",
  Frozen = "frozen",
  Completed = "completed",
  Approved = "approved",
  Cancelled = "cancelled",
}

export enum CountType {
  Physical = "physical",
  Cycle = "cycle",
  Blind = "blind",
  Spot = "spot",
  Annual = "annual",
}

export enum ReservationStatus {
  Active = "active",
  PartiallyFulfilled = "partially_fulfilled",
  Fulfilled = "fulfilled",
  Cancelled = "cancelled",
  Expired = "expired",
}

export enum CostMethod {
  FIFO = "fifo",
  MovingAverage = "moving_average",
  WeightedAverage = "weighted_average",
  Standard = "standard",
  SpecificID = "specific_id",
}

export enum RevaluationType {
  CostChange = "cost_change",
  ExchangeRate = "exchange_rate",
  Provision = "provision",
  Reversal = "reversal",
}

export enum QualityStatus {
  NotInspected = "not_inspected",
  Passed = "passed",
  Failed = "failed",
  OnHold = "on_hold",
  Quarantine = "quarantine",
}

export enum InventoryReasonCode {
  PurchaseReceipt = "purchase_receipt",
  PurchaseReturn = "purchase_return",
  SalesIssue = "sales_issue",
  SalesReturn = "sales_return",
  Transfer = "transfer",
  Adjustment = "adjustment",
  CountVariance = "count_variance",
  WriteOff = "write_off",
  Production = "production",
  Scrap = "scrap",
  Sample = "sample",
  Promotion = "promotion",
  InternalUse = "internal_use",
  Opening = "opening",
  Reversal = "reversal",
  LandedCost = "landed_cost",
  Revaluation = "revaluation",
}
