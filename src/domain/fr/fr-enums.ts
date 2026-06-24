export enum FrReportCategoryType {
  BalanceSheet = "balance_sheet",
  IncomeStatement = "income_statement",
  CashFlow = "cash_flow",
  ChangesInEquity = "changes_in_equity",
  TrialBalance = "trial_balance",
  GeneralLedger = "general_ledger",
  SubsidiaryLedger = "subsidiary_ledger",
  ManagementReport = "management_report",
  Consolidation = "consolidation",
  TaxReport = "tax_report",
  BudgetReport = "budget_report",
  FinancialAnalysis = "financial_analysis",
  Custom = "custom",
}

export enum FrReportStatus {
  Draft = "draft",
  Active = "active",
  Inactive = "inactive",
  Archived = "archived",
}

export enum FrInstanceStatus {
  Generating = "generating",
  Completed = "completed",
  Failed = "failed",
  Approved = "approved",
  Locked = "locked",
}

export enum FrRowType {
  Header = "header",
  Section = "section",
  Account = "account",
  Formula = "formula",
  Total = "total",
  Subtotal = "subtotal",
  Description = "description",
  Blank = "blank",
}

export enum FrCellType {
  Label = "label",
  Value = "value",
  Formula = "formula",
  Calculated = "calculated",
  AccountBalance = "account_balance",
  BudgetAmount = "budget_amount",
  Variance = "variance",
  Percentage = "percentage",
  Aggregated = "aggregated",
  Grouped = "grouped",
}

export enum FrFormulaType {
  Simple = "simple",
  Nested = "nested",
  Conditional = "conditional",
  Aggregation = "aggregation",
  Allocation = "allocation",
  Percentage = "percentage",
  Variance = "variance",
  GrowthRate = "growth_rate",
  RollingPeriod = "rolling_period",
  Window = "window",
  Custom = "custom",
}

export enum FrConsolidationMethod {
  Full = "full",
  Equity = "equity",
  Proportional = "proportional",
  Cost = "cost",
  JointVenture = "joint_venture",
}

export enum FrConsolidationStatus {
  Draft = "draft",
  InProgress = "in_progress",
  Completed = "completed",
  Verified = "verified",
  Approved = "approved",
  Locked = "locked",
}

export enum FrEliminationType {
  IntercompanyRevenue = "intercompany_revenue",
  IntercompanyExpense = "intercompany_expense",
  IntercompanyReceivable = "intercompany_receivable",
  IntercompanyPayable = "intercompany_payable",
  IntercompanyDividend = "intercompany_dividend",
  IntercompanyProfit = "intercompany_profit",
  MinorityInterest = "minority_interest",
  InvestmentElimination = "investment_elimination",
  EquityElimination = "equity_elimination",
  Other = "other",
}

export enum FrReportingDimensionType {
  Segment = "segment",
  Geography = "geography",
  BusinessUnit = "business_unit",
  ProductLine = "product_line",
  Channel = "channel",
  Project = "project",
  CostCenter = "cost_center",
  ProfitCenter = "profit_center",
  LegalEntity = "legal_entity",
  Custom = "custom",
}

export enum FrRatioCategory {
  Liquidity = "liquidity",
  Profitability = "profitability",
  Efficiency = "efficiency",
  Leverage = "leverage",
  CashFlow = "cash_flow",
  Market = "market",
  Valuation = "valuation",
  Custom = "custom",
}

export enum FrScheduleFrequency {
  Daily = "daily",
  Weekly = "weekly",
  Monthly = "monthly",
  Quarterly = "quarterly",
  SemiAnnual = "semi_annual",
  Annual = "annual",
  Custom = "custom",
}

export enum FrExportFormat {
  Excel = "excel",
  Csv = "csv",
  Pdf = "pdf",
  Json = "json",
  Xml = "xml",
  Xbrl = "xbrl",
  Html = "html",
}
