export enum ErrorSeverity {
  Critical = "critical",
  Error = "error",
  Warning = "warning",
  Info = "info",
}

export enum ErrorCategory {
  Authentication = "authentication",
  Authorization = "authorization",
  Validation = "validation",
  Accounting = "accounting",
  Fiscal = "fiscal",
  Currency = "currency",
  Dimension = "dimension",
  Budget = "budget",
  Concurrency = "concurrency",
  Infrastructure = "infrastructure",
  BusinessRule = "business_rule",
  System = "system",
}

export interface ErrorDefinition {
  code: string;
  message: string;
  httpStatus: number;
  severity: ErrorSeverity;
  category: ErrorCategory;
  retryable: boolean;
  description: string;
}

export class PostingError extends Error {
  public readonly timestamp: Date;

  constructor(
    public readonly code: string,
    message: string,
    public readonly category: ErrorCategory,
    public readonly httpStatus: number = 400,
    public readonly retryable: boolean = false,
    public readonly details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "PostingError";
    this.timestamp = new Date();
  }

  toJSON() {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      category: this.category,
      httpStatus: this.httpStatus,
      retryable: this.retryable,
      timestamp: this.timestamp,
      details: this.details,
    };
  }
}

export const ErrorCatalogue: Record<string, ErrorDefinition> = {
  // Authentication & Authorization
  AUTH_001: { code: "AUTH_001", message: "User session is not active or expired", httpStatus: 401, severity: ErrorSeverity.Error, category: ErrorCategory.Authentication, retryable: false, description: "Active user session is required for posting" },
  AUTH_002: { code: "AUTH_002", message: "User lacks posting permission", httpStatus: 403, severity: ErrorSeverity.Error, category: ErrorCategory.Authorization, retryable: false, description: "User must have the posting role or permission" },
  AUTH_003: { code: "AUTH_003", message: "Voucher type access denied", httpStatus: 403, severity: ErrorSeverity.Error, category: ErrorCategory.Authorization, retryable: false, description: "User not authorized for this voucher type" },
  AUTH_004: { code: "AUTH_004", message: "Segregation of duties violation: creator and approver must differ", httpStatus: 403, severity: ErrorSeverity.Error, category: ErrorCategory.Authorization, retryable: false, description: "Same user cannot create and approve" },

  // Validation
  VAL_001: { code: "VAL_001", message: "Journal batch not found", httpStatus: 404, severity: ErrorSeverity.Error, category: ErrorCategory.Validation, retryable: false, description: "Batch ID does not exist" },
  VAL_002: { code: "VAL_002", message: "Account not found: {accountId}", httpStatus: 404, severity: ErrorSeverity.Error, category: ErrorCategory.Validation, retryable: false, description: "Referenced account does not exist" },
  VAL_003: { code: "VAL_003", message: "Period not found", httpStatus: 404, severity: ErrorSeverity.Error, category: ErrorCategory.Validation, retryable: false, description: "Referenced period does not exist" },
  VAL_004: { code: "VAL_004", message: "Fiscal year not found", httpStatus: 404, severity: ErrorSeverity.Error, category: ErrorCategory.Validation, retryable: false, description: "Referenced fiscal year does not exist" },
  VAL_005: { code: "VAL_005", message: "Batch is empty: no journal lines", httpStatus: 400, severity: ErrorSeverity.Error, category: ErrorCategory.Validation, retryable: false, description: "Cannot post a batch with zero lines" },
  VAL_006: { code: "VAL_006", message: "Batch already posted", httpStatus: 409, severity: ErrorSeverity.Error, category: ErrorCategory.Validation, retryable: false, description: "Cannot post a batch that is already posted" },

  // Accounting
  ACC_001: { code: "ACC_001", message: "Total debit ({totalDebit}) does not equal total credit ({totalCredit})", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "Double-entry fundamental rule violation" },
  ACC_002: { code: "ACC_002", message: "Account {accountCode} is not a posting account", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "Only posting (non-control) accounts can be used" },
  ACC_003: { code: "ACC_003", message: "Account {accountCode} is inactive", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "Inactive accounts cannot be posted to" },
  ACC_004: { code: "ACC_004", message: "Account {accountCode} is deleted", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "Deleted accounts cannot be used" },
  ACC_005: { code: "ACC_005", message: "Line amount must be non-negative", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "Negative amounts not allowed on journal lines" },
  ACC_006: { code: "ACC_006", message: "Line must have either debit or credit amount", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "Both zero amounts on a line is invalid" },
  ACC_007: { code: "ACC_007", message: "Control account {accountCode} cannot be posted to directly", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "Control accounts are summary accounts" },
  ACC_008: { code: "ACC_008", message: "Account {accountCode} does not allow manual entry", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "System-controlled account" },
  ACC_009: { code: "ACC_009", message: "Line description is required", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "Each journal line needs a description" },
  ACC_010: { code: "ACC_010", message: "Currency mismatch within batch", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "All lines must use the same currency" },
  ACC_011: { code: "ACC_011", message: "Journal must have at least 2 lines", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Accounting, retryable: false, description: "Minimum line count requirement" },

  // Fiscal
  FIS_001: { code: "FIS_001", message: "Period {periodName} is closed", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Fiscal, retryable: false, description: "Cannot post to a closed period" },
  FIS_002: { code: "FIS_002", message: "Period {periodName} is locked", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Fiscal, retryable: false, description: "Cannot post to a locked period" },
  FIS_003: { code: "FIS_003", message: "Fiscal year {yearCode} is closed", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Fiscal, retryable: false, description: "Cannot post to a closed fiscal year" },
  FIS_004: { code: "FIS_004", message: "Posting date {date} is outside period date range", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Fiscal, retryable: false, description: "Posting date must be within period" },
  FIS_005: { code: "FIS_005", message: "Posting date {date} is in the future", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Fiscal, retryable: false, description: "Future posting not allowed" },
  FIS_006: { code: "FIS_006", message: "Voucher date {date} exceeds allowed past range", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Fiscal, retryable: false, description: "Voucher date too far in the past" },

  // Currency
  CUR_001: { code: "CUR_001", message: "No valid exchange rate found for {fromCurrency}/{toCurrency} on {date}", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Currency, retryable: false, description: "Exchange rate must exist and be active" },
  CUR_002: { code: "CUR_002", message: "Foreign currency total debit ({fcDebit}) != total credit ({fcCredit})", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Currency, retryable: false, description: "Foreign currency totals must balance" },
  CUR_003: { code: "CUR_003", message: "Line currency {lineCurrency} does not match batch currency {batchCurrency}", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Currency, retryable: false, description: "All lines must use batch currency or VND" },

  // Dimension
  DIM_001: { code: "DIM_001", message: "Cost center {code} is inactive or not found", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Dimension, retryable: false, description: "Cost center must be active" },
  DIM_002: { code: "DIM_002", message: "Department {code} is inactive or not found", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Dimension, retryable: false, description: "Department must be active" },
  DIM_003: { code: "DIM_003", message: "Cost center is mandatory for expense account {accountCode}", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Dimension, retryable: false, description: "Expense accounts require cost center" },

  // Budget
  BUD_001: { code: "BUD_001", message: "Budget exceeded for account {accountCode}: remaining {remaining}, required {required}", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Budget, retryable: false, description: "Insufficient budget" },
  BUD_002: { code: "BUD_002", message: "Budget {budgetName} is not in approved status", httpStatus: 422, severity: ErrorSeverity.Error, category: ErrorCategory.Budget, retryable: false, description: "Budget must be approved" },
  BUD_003: { code: "BUD_003", message: "Budget {budgetName} is nearing limit: {remaining} remaining ({percent}%)", httpStatus: 200, severity: ErrorSeverity.Warning, category: ErrorCategory.Budget, retryable: false, description: "Budget warning threshold" },

  // Concurrency
  CON_001: { code: "CON_001", message: "Optimistic lock conflict on account {accountCode}: version mismatch", httpStatus: 409, severity: ErrorSeverity.Error, category: ErrorCategory.Concurrency, retryable: true, description: "Retry the posting" },
  CON_002: { code: "CON_002", message: "Optimistic lock conflict on batch {batchNumber}", httpStatus: 409, severity: ErrorSeverity.Error, category: ErrorCategory.Concurrency, retryable: true, description: "Retry the posting" },
  CON_003: { code: "CON_003", message: "Pessimistic lock timeout on account {accountCode}", httpStatus: 409, severity: ErrorSeverity.Error, category: ErrorCategory.Concurrency, retryable: true, description: "Lock timeout, retry later" },

  // Infrastructure
  INF_001: { code: "INF_001", message: "Database connection failed", httpStatus: 503, severity: ErrorSeverity.Critical, category: ErrorCategory.Infrastructure, retryable: true, description: "Infrastructure failure" },
  INF_002: { code: "INF_002", message: "Transaction commit failed, changes rolled back", httpStatus: 500, severity: ErrorSeverity.Critical, category: ErrorCategory.Infrastructure, retryable: true, description: "Transaction failure" },
  INF_003: { code: "INF_003", message: "Queue submission failed", httpStatus: 503, severity: ErrorSeverity.Error, category: ErrorCategory.Infrastructure, retryable: true, description: "Queue infrastructure failure" },

  // Security
  SEC_001: { code: "SEC_001", message: "Duplicate posting detected: idempotency key {key} already processed", httpStatus: 409, severity: ErrorSeverity.Error, category: ErrorCategory.Validation, retryable: false, description: "Idempotency key already used" },
};

export function getError(code: string): ErrorDefinition {
  const def = ErrorCatalogue[code];
  if (!def) {
    return {
      code: "UNKNOWN",
      message: `Unknown error code: ${code}`,
      httpStatus: 500,
      severity: ErrorSeverity.Error,
      category: ErrorCategory.System,
      retryable: false,
      description: "Undefined error",
    };
  }
  return def;
}

export function createPostingError(code: string, details?: Record<string, unknown>): PostingError {
  const def = getError(code);
  let msg = def.message;
  if (details) {
    for (const [key, val] of Object.entries(details)) {
      msg = msg.replace(`{${key}}`, String(val));
    }
  }
  return new PostingError(code, msg, def.category, def.httpStatus, def.retryable, details);
}
