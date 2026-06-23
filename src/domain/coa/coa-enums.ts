export enum AccountClassType {
  Asset = "asset",
  Liability = "liability",
  Equity = "equity",
  Revenue = "revenue",
  Expense = "expense",
  CostOfGoodsSold = "cost_of_goods_sold",
  OtherIncome = "other_income",
  OtherExpense = "other_expense",
  Manufacturing = "manufacturing",
}

export enum AccountTypeCategory {
  CurrentAsset = "current_asset",
  NonCurrentAsset = "non_current_asset",
  CurrentLiability = "current_liability",
  NonCurrentLiability = "non_current_liability",
  Equity = "equity",
  Revenue = "revenue",
  OperatingExpense = "operating_expense",
  ManufacturingCost = "manufacturing_cost",
  CostOfGoodsSold = "cost_of_goods_sold",
  OtherIncome = "other_income",
  OtherExpense = "other_expense",
  OffBalanceSheet = "off_balance_sheet",
}

export enum AccountSubType {
  Cash = "cash",
  Bank = "bank",
  Receivable = "receivable",
  Inventory = "inventory",
  FixedAsset = "fixed_asset",
  IntangibleAsset = "intangible_asset",
  Investment = "investment",
  Payable = "payable",
  TaxPayable = "tax_payable",
  Loan = "loan",
  EquityCapital = "equity_capital",
  RetainedEarnings = "retained_earnings",
  Revenue = "revenue",
  CostOfSales = "cost_of_sales",
  Salary = "salary",
  Depreciation = "depreciation",
  TaxExpense = "tax_expense",
  Other = "other",
}

export enum AccountMappingStandard {
  Ifrs = "ifrs",
  Vas = "vas",
  CashFlow = "cash_flow",
  Tax = "tax",
  Statutory = "statutory",
  Management = "management",
}

export enum AccountMappingType {
  Direct = "direct",
  Aggregation = "aggregation",
  Percentage = "percentage",
  Formula = "formula",
  Manual = "manual",
}

export enum DimensionRequirement {
  Optional = "optional",
  Recommended = "recommended",
  Required = "required",
  Prohibited = "prohibited",
}

export enum AccountEffectiveStatus {
  Draft = "draft",
  Active = "active",
  Suspended = "suspended",
  Closed = "closed",
  Archived = "archived",
}

export enum AccountControlLevel {
  None = "none",
  Warning = "warning",
  Strict = "strict",
}
