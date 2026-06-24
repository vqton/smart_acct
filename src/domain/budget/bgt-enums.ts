export enum BgtBudgetType {
  Annual = "annual",
  Quarterly = "quarterly",
  Monthly = "monthly",
  Weekly = "weekly",
  Daily = "daily",
  RollingForecast = "rolling_forecast",
  RollingBudget = "rolling_budget",
  Flexible = "flexible",
  Static = "static",
  ZeroBased = "zero_based",
  Incremental = "incremental",
  TopDown = "top_down",
  BottomUp = "bottom_up",
  Participative = "participative",
  DriverBased = "driver_based",
  ActivityBased = "activity_based",
  Capex = "capex",
  Opex = "opex",
  Revenue = "revenue",
  Cash = "cash",
  Production = "production",
  Procurement = "procurement",
  Department = "department",
  Project = "project",
  Sales = "sales",
  Marketing = "marketing",
  Hr = "hr",
  It = "it",
  Maintenance = "maintenance",
  Investment = "investment",
  Strategic = "strategic",
  Scenario = "scenario",
  ForecastVersion = "forecast_version",
}

export enum BgtBudgetStatus {
  Draft = "draft",
  Preparation = "preparation",
  Review = "review",
  Revision = "revision",
  Submitted = "submitted",
  Approved = "approved",
  Rejected = "rejected",
  Published = "published",
  Activated = "activated",
  Execution = "execution",
  Monitoring = "monitoring",
  Adjustment = "adjustment",
  Frozen = "frozen",
  Closed = "closed",
  Archived = "archived",
  Reopened = "reopened",
}

export enum BgtScenarioType {
  Base = "base",
  Optimistic = "optimistic",
  Pessimistic = "pessimistic",
  BestCase = "best_case",
  WorstCase = "worst_case",
  WhatIf = "what_if",
  Simulation = "simulation",
  Stretch = "stretch",
  Contingency = "contingency",
  Custom = "custom",
}

export enum BgtVersionStatus {
  Working = "working",
  InReview = "in_review",
  Approved = "approved",
  Published = "published",
  Frozen = "frozen",
  Superseded = "superseded",
  Archived = "archived",
}

export enum BgtControlLevel {
  None = "none",
  Soft = "soft",
  Hard = "hard",
  Preventive = "preventive",
  Advisory = "advisory",
}

export enum BgtControlAction {
  Warn = "warn",
  Block = "block",
  AllowWithApproval = "allow_with_approval",
  Notify = "notify",
}

export enum BgtReservationStatus {
  Draft = "draft",
  Active = "active",
  PartiallyConsumed = "partially_consumed",
  FullyConsumed = "fully_consumed",
  Released = "released",
  Expired = "expired",
  Cancelled = "cancelled",
}

export enum BgtCommitmentType {
  PurchaseRequisition = "purchase_requisition",
  PurchaseOrder = "purchase_order",
  Contract = "contract",
  GoodsReceipt = "goods_receipt",
  Invoice = "invoice",
  Payment = "payment",
  Accrual = "accrual",
  Reservation = "reservation",
}

export enum BgtAllocationMethod {
  Direct = "direct",
  Percentage = "percentage",
  DriverBased = "driver_based",
  Fixed = "fixed",
  Dynamic = "dynamic",
  Statistical = "statistical",
  Abc = "abc",
  StepDown = "step_down",
  Reciprocal = "reciprocal",
  CrossCompany = "cross_company",
  Intercompany = "intercompany",
}

export enum BgtAllocationStatus {
  Draft = "draft",
  Calculated = "calculated",
  Posted = "posted",
  Reversed = "reversed",
  Cancelled = "cancelled",
}

export enum BgtForecastMethod {
  Rolling = "rolling",
  DriverBased = "driver_based",
  Trend = "trend",
  Statistical = "statistical",
  Manual = "manual",
  AiAssisted = "ai_assisted",
  Seasonal = "seasonal",
  ExponentialSmoothing = "exponential_smoothing",
  LinearRegression = "linear_regression",
  MovingAverage = "moving_average",
}

export enum BgtForecastStatus {
  Draft = "draft",
  Submitted = "submitted",
  Approved = "approved",
  Published = "published",
  Archived = "archived",
}

export enum BgtApprovalStatus {
  Pending = "pending",
  Approved = "approved",
  Rejected = "rejected",
  Returned = "returned",
  Escalated = "escalated",
  Delegated = "delegated",
  Skipped = "skipped",
}

export enum BgtApprovalDecision {
  Approve = "approve",
  Reject = "reject",
  ReturnForRevision = "return_for_revision",
  Escalate = "escalate",
  Delegate = "delegate",
}

export enum BgtPeriodType {
  Daily = "daily",
  Weekly = "weekly",
  Monthly = "monthly",
  Quarterly = "quarterly",
  SemiAnnual = "semi_annual",
  Annual = "annual",
  Custom = "custom",
}

export enum BgtSnapshotType {
  Periodic = "periodic",
  PreClose = "pre_close",
  PostClose = "post_close",
  Freeze = "freeze",
  Version = "version",
  Audit = "audit",
  Restore = "restore",
}

export enum BgtJournalType {
  BudgetApproval = "budget_approval",
  BudgetAdjustment = "budget_adjustment",
  BudgetTransfer = "budget_transfer",
  BudgetAllocation = "budget_allocation",
  Commitment = "commitment",
  Encumbrance = "encumbrance",
  Consumption = "consumption",
  Reversal = "reversal",
  CarryForward = "carry_forward",
  PeriodClose = "period_close",
  OpeningBalance = "opening_balance",
}

export enum BgtTransferStatus {
  Draft = "draft",
  Submitted = "submitted",
  Approved = "approved",
  Completed = "completed",
  Reversed = "reversed",
  Cancelled = "cancelled",
}
