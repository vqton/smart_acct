export enum AccountCategory {
  ShortTermAsset = "short_term_asset",
  LongTermAsset = "long_term_asset",
  ShortTermLiability = "short_term_liability",
  LongTermLiability = "long_term_liability",
  Equity = "equity",
  Revenue = "revenue",
  OperatingExpense = "operating_expense",
  OtherExpense = "other_expense",
  OtherIncome = "other_income",
  CostOfGoodsSold = "cost_of_goods_sold",
  ManufacturingCost = "manufacturing_cost",
}

export enum AccountNature {
  Debit = "debit",
  Credit = "credit",
}

export enum AccountClass {
  Asset = "1",
  Liability = "2",
  Equity = "3",
  Revenue = "4",
  Expense = "5",
  CostOfGoodsSold = "6",
  OtherIncome = "7",
  OtherExpense = "8",
  Manufacturing = "9",
}
