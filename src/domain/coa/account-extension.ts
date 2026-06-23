import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { AccountExtensionId, CoaAccountId } from "./coa-ids.js";
import {
  AccountEffectiveStatus,
  AccountControlLevel,
  DimensionRequirement,
} from "./coa-enums.js";

export interface AccountExtensionState {
  id: string;
  accountId: string;
  typeId: string | null;
  effectiveStatus: AccountEffectiveStatus;
  effectiveFrom: Date | null;
  effectiveTo: Date | null;
  statusReason: string | null;
  allowAutoPosting: boolean;
  requireApproval: boolean;
  budgetControlLevel: AccountControlLevel;
  budgetCheckMessage: string | null;
  defaultCostCenterId: string | null;
  defaultDepartmentId: string | null;
  defaultProjectId: string | null;
  defaultBranchId: string | null;
  costCenterRequired: DimensionRequirement;
  departmentRequired: DimensionRequirement;
  projectRequired: DimensionRequirement;
  branchRequired: DimensionRequirement;
  profitCenterRequired: DimensionRequirement;
  isCashAccount: boolean;
  isBankAccount: boolean;
  isTaxAccount: boolean;
  isInventoryAccount: boolean;
  isReceivableAccount: boolean;
  isPayableAccount: boolean;
  isIntercompanyAccount: boolean;
  defaultTaxCodeId: string | null;
  defaultTaxRateId: string | null;
  cashFlowCode: string | null;
  financialStatementCode: string | null;
  financialStatementNote: string | null;
  createdById: string | null;
  updatedById: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class AccountExtensionModified implements DomainEvent {
  readonly eventName = "AccountExtensionModified";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class AccountExtension extends AggregateRoot<AccountExtensionId> {
  private _id: AccountExtensionId;
  private _accountId: string;
  private _typeId: string | null;
  private _effectiveStatus: AccountEffectiveStatus;
  private _effectiveFrom: Date | null;
  private _effectiveTo: Date | null;
  private _statusReason: string | null;
  private _allowAutoPosting: boolean;
  private _requireApproval: boolean;
  private _budgetControlLevel: AccountControlLevel;
  private _budgetCheckMessage: string | null;
  private _defaultCostCenterId: string | null;
  private _defaultDepartmentId: string | null;
  private _defaultProjectId: string | null;
  private _defaultBranchId: string | null;
  private _costCenterRequired: DimensionRequirement;
  private _departmentRequired: DimensionRequirement;
  private _projectRequired: DimensionRequirement;
  private _branchRequired: DimensionRequirement;
  private _profitCenterRequired: DimensionRequirement;
  private _isCashAccount: boolean;
  private _isBankAccount: boolean;
  private _isTaxAccount: boolean;
  private _isInventoryAccount: boolean;
  private _isReceivableAccount: boolean;
  private _isPayableAccount: boolean;
  private _isIntercompanyAccount: boolean;
  private _defaultTaxCodeId: string | null;
  private _defaultTaxRateId: string | null;
  private _cashFlowCode: string | null;
  private _financialStatementCode: string | null;
  private _financialStatementNote: string | null;
  private _createdById: string | null;
  private _updatedById: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: AccountExtensionId, accountId: string) {
    super();
    this._id = id;
    this._accountId = accountId;
    this._typeId = null;
    this._effectiveStatus = AccountEffectiveStatus.Active;
    this._effectiveFrom = null;
    this._effectiveTo = null;
    this._statusReason = null;
    this._allowAutoPosting = true;
    this._requireApproval = false;
    this._budgetControlLevel = AccountControlLevel.None;
    this._budgetCheckMessage = null;
    this._defaultCostCenterId = null;
    this._defaultDepartmentId = null;
    this._defaultProjectId = null;
    this._defaultBranchId = null;
    this._costCenterRequired = DimensionRequirement.Optional;
    this._departmentRequired = DimensionRequirement.Optional;
    this._projectRequired = DimensionRequirement.Optional;
    this._branchRequired = DimensionRequirement.Optional;
    this._profitCenterRequired = DimensionRequirement.Optional;
    this._isCashAccount = false;
    this._isBankAccount = false;
    this._isTaxAccount = false;
    this._isInventoryAccount = false;
    this._isReceivableAccount = false;
    this._isPayableAccount = false;
    this._isIntercompanyAccount = false;
    this._defaultTaxCodeId = null;
    this._defaultTaxRateId = null;
    this._cashFlowCode = null;
    this._financialStatementCode = null;
    this._financialStatementNote = null;
    this._createdById = null;
    this._updatedById = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(accountId: string): AccountExtension {
    return new AccountExtension(AccountExtensionId.new(), accountId);
  }

  static load(state: AccountExtensionState): AccountExtension {
    const e = new AccountExtension(new AccountExtensionId(state.id), state.accountId);
    e._typeId = state.typeId;
    e._effectiveStatus = state.effectiveStatus;
    e._effectiveFrom = state.effectiveFrom;
    e._effectiveTo = state.effectiveTo;
    e._statusReason = state.statusReason;
    e._allowAutoPosting = state.allowAutoPosting;
    e._requireApproval = state.requireApproval;
    e._budgetControlLevel = state.budgetControlLevel;
    e._budgetCheckMessage = state.budgetCheckMessage;
    e._defaultCostCenterId = state.defaultCostCenterId;
    e._defaultDepartmentId = state.defaultDepartmentId;
    e._defaultProjectId = state.defaultProjectId;
    e._defaultBranchId = state.defaultBranchId;
    e._costCenterRequired = state.costCenterRequired;
    e._departmentRequired = state.departmentRequired;
    e._projectRequired = state.projectRequired;
    e._branchRequired = state.branchRequired;
    e._profitCenterRequired = state.profitCenterRequired;
    e._isCashAccount = state.isCashAccount;
    e._isBankAccount = state.isBankAccount;
    e._isTaxAccount = state.isTaxAccount;
    e._isInventoryAccount = state.isInventoryAccount;
    e._isReceivableAccount = state.isReceivableAccount;
    e._isPayableAccount = state.isPayableAccount;
    e._isIntercompanyAccount = state.isIntercompanyAccount;
    e._defaultTaxCodeId = state.defaultTaxCodeId;
    e._defaultTaxRateId = state.defaultTaxRateId;
    e._cashFlowCode = state.cashFlowCode;
    e._financialStatementCode = state.financialStatementCode;
    e._financialStatementNote = state.financialStatementNote;
    e._createdById = state.createdById;
    e._updatedById = state.updatedById;
    e._version = state.version;
    e._createdAt = state.createdAt;
    e._updatedAt = state.updatedAt;
    return e;
  }

  get id(): AccountExtensionId { return this._id; }
  get accountId(): string { return this._accountId; }
  get typeId(): string | null { return this._typeId; }
  get effectiveStatus(): AccountEffectiveStatus { return this._effectiveStatus; }
  get effectiveFrom(): Date | null { return this._effectiveFrom; }
  get effectiveTo(): Date | null { return this._effectiveTo; }
  get statusReason(): string | null { return this._statusReason; }
  get allowAutoPosting(): boolean { return this._allowAutoPosting; }
  get requireApproval(): boolean { return this._requireApproval; }
  get budgetControlLevel(): AccountControlLevel { return this._budgetControlLevel; }
  get budgetCheckMessage(): string | null { return this._budgetCheckMessage; }
  get defaultCostCenterId(): string | null { return this._defaultCostCenterId; }
  get defaultDepartmentId(): string | null { return this._defaultDepartmentId; }
  get defaultProjectId(): string | null { return this._defaultProjectId; }
  get defaultBranchId(): string | null { return this._defaultBranchId; }
  get costCenterRequired(): DimensionRequirement { return this._costCenterRequired; }
  get departmentRequired(): DimensionRequirement { return this._departmentRequired; }
  get projectRequired(): DimensionRequirement { return this._projectRequired; }
  get branchRequired(): DimensionRequirement { return this._branchRequired; }
  get profitCenterRequired(): DimensionRequirement { return this._profitCenterRequired; }
  get isCashAccount(): boolean { return this._isCashAccount; }
  get isBankAccount(): boolean { return this._isBankAccount; }
  get isTaxAccount(): boolean { return this._isTaxAccount; }
  get isInventoryAccount(): boolean { return this._isInventoryAccount; }
  get isReceivableAccount(): boolean { return this._isReceivableAccount; }
  get isPayableAccount(): boolean { return this._isPayableAccount; }
  get isIntercompanyAccount(): boolean { return this._isIntercompanyAccount; }
  get defaultTaxCodeId(): string | null { return this._defaultTaxCodeId; }
  get defaultTaxRateId(): string | null { return this._defaultTaxRateId; }
  get cashFlowCode(): string | null { return this._cashFlowCode; }
  get financialStatementCode(): string | null { return this._financialStatementCode; }
  get financialStatementNote(): string | null { return this._financialStatementNote; }
  get createdById(): string | null { return this._createdById; }
  get updatedById(): string | null { return this._updatedById; }
  get version(): number { return this._version; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }

  modify(params: Partial<Omit<AccountExtensionState, "id" | "accountId" | "version" | "createdAt" | "updatedAt">>): void {
    const changed: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(params)) {
      if (val !== undefined && key in this) {
        const field = `_${key}` as keyof this;
        if (field in this) {
          (this as any)[field] = val;
          changed[key] = val;
        }
      }
    }
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new AccountExtensionModified(this._id.value, new Date(), changed));
  }

  updateEffectiveStatus(status: AccountEffectiveStatus, reason?: string): void {
    if (this._effectiveStatus === AccountEffectiveStatus.Closed && status !== AccountEffectiveStatus.Archived) {
      throw new DomainError("BusinessRule", "Cannot change status of a closed account");
    }
    if (this._effectiveStatus === AccountEffectiveStatus.Archived) {
      throw new DomainError("BusinessRule", "Cannot change status of an archived account");
    }
    this._effectiveStatus = status;
    this._statusReason = reason ?? null;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new AccountExtensionModified(this._id.value, new Date(), { effectiveStatus: status, reason }));
  }

  markAsCashAccount(cashFlowCode?: string): void {
    this._isCashAccount = true;
    this._isPostingAccount();
    if (cashFlowCode) this._cashFlowCode = cashFlowCode;
  }

  markAsBankAccount(): void {
    this._isBankAccount = true;
    this._isPostingAccount();
  }

  markAsTaxAccount(taxCodeId: string): void {
    this._isTaxAccount = true;
    this._defaultTaxCodeId = taxCodeId;
  }

  markAsInventoryAccount(): void {
    this._isInventoryAccount = true;
    this._isPostingAccount();
  }

  setDimensionRequirement(
    dimension: "costCenter" | "department" | "project" | "branch" | "profitCenter",
    requirement: DimensionRequirement,
  ): void {
    const field = `_${dimension}Required` as keyof this;
    if (field in this) {
      (this as any)[field] = requirement;
    }
  }

  setBudgetControl(level: AccountControlLevel, message?: string): void {
    this._budgetControlLevel = level;
    this._budgetCheckMessage = message ?? null;
  }

  private _isPostingAccount(): void {
    if (!this._allowAutoPosting) {
      throw new DomainError("BusinessRule", "Account must allow auto-posting to be a sub-ledger account");
    }
  }

  toState(): AccountExtensionState {
    return {
      id: this._id.value,
      accountId: this._accountId,
      typeId: this._typeId,
      effectiveStatus: this._effectiveStatus,
      effectiveFrom: this._effectiveFrom,
      effectiveTo: this._effectiveTo,
      statusReason: this._statusReason,
      allowAutoPosting: this._allowAutoPosting,
      requireApproval: this._requireApproval,
      budgetControlLevel: this._budgetControlLevel,
      budgetCheckMessage: this._budgetCheckMessage,
      defaultCostCenterId: this._defaultCostCenterId,
      defaultDepartmentId: this._defaultDepartmentId,
      defaultProjectId: this._defaultProjectId,
      defaultBranchId: this._defaultBranchId,
      costCenterRequired: this._costCenterRequired,
      departmentRequired: this._departmentRequired,
      projectRequired: this._projectRequired,
      branchRequired: this._branchRequired,
      profitCenterRequired: this._profitCenterRequired,
      isCashAccount: this._isCashAccount,
      isBankAccount: this._isBankAccount,
      isTaxAccount: this._isTaxAccount,
      isInventoryAccount: this._isInventoryAccount,
      isReceivableAccount: this._isReceivableAccount,
      isPayableAccount: this._isPayableAccount,
      isIntercompanyAccount: this._isIntercompanyAccount,
      defaultTaxCodeId: this._defaultTaxCodeId,
      defaultTaxRateId: this._defaultTaxRateId,
      cashFlowCode: this._cashFlowCode,
      financialStatementCode: this._financialStatementCode,
      financialStatementNote: this._financialStatementNote,
      createdById: this._createdById,
      updatedById: this._updatedById,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
    };
  }
}
