export enum CstCostMethod {
  Standard = "standard",
  Actual = "actual",
  WeightedAverage = "weighted_average",
  MovingAverage = "moving_average",
  FIFO = "fifo",
  SpecificIdentification = "specific_identification",
  Batch = "batch",
  JobOrder = "job_order",
  Process = "process",
  ABC = "abc",
  Absorption = "absorption",
  Marginal = "marginal",
  Hybrid = "hybrid",
}

export enum CstCostElementType {
  Material = "material",
  Labor = "labor",
  Machine = "machine",
  Overhead = "overhead",
  Subcontract = "subcontract",
  Setup = "setup",
  Tooling = "tooling",
  Energy = "energy",
  Transportation = "transportation",
  Duty = "duty",
  Administration = "administration",
  Selling = "selling",
}

export enum CstCostPoolType {
  Production = "production",
  Service = "service",
  Administration = "administration",
  Selling = "selling",
  MaterialOverhead = "material_overhead",
  LaborOverhead = "labor_overhead",
  MachineOverhead = "machine_overhead",
  GeneralOverhead = "general_overhead",
  IT = "it",
  HR = "hr",
  Facility = "facility",
  Quality = "quality",
  Logistics = "logistics",
  Maintenance = "maintenance",
  Utilities = "utilities",
}

export enum CstAllocationMethod {
  Direct = "direct",
  StepDown = "step_down",
  Reciprocal = "reciprocal",
  DriverBased = "driver_based",
  Percentage = "percentage",
  Fixed = "fixed",
  ABC = "abc",
  Statistical = "statistical",
}

export enum CstAllocationBasis {
  Volume = "volume",
  Value = "value",
  LaborHours = "labor_hours",
  MachineHours = "machine_hours",
  Headcount = "headcount",
  Area = "area",
  PowerConsumption = "power_consumption",
  MaterialCost = "material_cost",
  LaborCost = "labor_cost",
  Revenue = "revenue",
  UnitsProduced = "units_produced",
  Orders = "orders",
  Transactions = "transactions",
  Time = "time",
  Custom = "custom",
}

export enum CstProductionOrderStatus {
  Planned = "planned",
  Released = "released",
  InProgress = "in_progress",
  Completed = "completed",
  Closed = "closed",
  Cancelled = "cancelled",
  OnHold = "on_hold",
}

export enum CstCostSnapshotType {
  PeriodClose = "period_close",
  CostFreeze = "cost_freeze",
  PreClose = "pre_close",
  PostClose = "post_close",
  Actual = "actual",
  Budget = "budget",
  Simulation = "simulation",
  Revaluation = "revaluation",
}

export enum CstVarianceType {
  MaterialPrice = "material_price",
  MaterialUsage = "material_usage",
  LaborRate = "labor_rate",
  LaborEfficiency = "labor_efficiency",
  MachineRate = "machine_rate",
  MachineEfficiency = "machine_efficiency",
  OverheadVolume = "overhead_volume",
  OverheadSpending = "overhead_spending",
  OverheadEfficiency = "overhead_efficiency",
  PurchasePrice = "purchase_price",
  ExchangeRate = "exchange_rate",
  ProductionVolume = "production_volume",
  Yield = "yield",
  Mix = "mix",
  YieldQuantity = "yield_quantity",
  Revaluation = "revaluation",
}
