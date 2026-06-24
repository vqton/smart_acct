export enum Permission {
  // GL
  JournalCreate = "gl:journal:create",
  JournalSubmit = "gl:journal:submit",
  JournalApprove = "gl:journal:approve",
  JournalPost = "gl:journal:post",
  JournalReverse = "gl:journal:reverse",
  AccountRead = "gl:account:read",
  AccountCreate = "gl:account:create",
  AccountUpdate = "gl:account:update",
  AccountDelete = "gl:account:delete",
  TrialBalance = "gl:report:trial-balance",
  LedgerReport = "gl:report:ledger",

  // Tax
  TaxTypeManage = "tax:type:manage",
  TaxCodeManage = "tax:code:manage",
  TaxReturnManage = "tax:return:manage",
  TaxPaymentManage = "tax:payment:manage",

  // COA
  CoaClassManage = "coa:class:manage",
  CoaTypeManage = "coa:type:manage",
  CoaMappingManage = "coa:mapping:manage",
  CoaExtensionManage = "coa:extension:manage",

  // Budget
  BudgetPlanCreate = "budget:plan:create",
  BudgetPlanApprove = "budget:plan:approve",
  BudgetControl = "budget:control:manage",
  BudgetTransfer = "budget:transfer:execute",

  // CM
  CashReceiptCreate = "cm:receipt:create",
  CashPaymentCreate = "cm:payment:create",
  CashBoxManage = "cm:cashbox:manage",
  BankTransferExecute = "cm:bank-transfer:execute",

  // Sales
  SalesOrderCreate = "sales:order:create",
  SalesInvoiceCreate = "sales:invoice:create",
  SalesInvoiceCancel = "sales:invoice:cancel",

  // Purchasing
  PurchaseOrderCreate = "pur:order:create",
  PurchaseInvoiceApprove = "pur:invoice:approve",
  GoodsReceiptCreate = "pur:goods-receipt:create",

  // Inventory
  InventoryAdjust = "inv:adjust",
  InventoryTransfer = "inv:transfer",
  InventoryCount = "inv:count",

  // Payroll
  PayrollRunCreate = "prl:run:create",
  PayrollRunApprove = "prl:run:approve",
  PayrollRunPost = "prl:run:post",

  // Bank
  BankTransactionCreate = "bnk:transaction:create",
  BankReconciliationManage = "bnk:reconciliation:manage",
  BankAccountManage = "bnk:account:manage",

  // Admin
  UserManage = "admin:user:manage",
  RoleManage = "admin:role:manage",
  AuditLogView = "admin:audit:view",
}
