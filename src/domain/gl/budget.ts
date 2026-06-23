import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class BudgetId extends Identifier {
  static new(): BudgetId {
    return new BudgetId(IdGenerator.uuid());
  }
}

export enum BudgetStatus {
  Draft = "draft",
  Submitted = "submitted",
  Approved = "approved",
  Rejected = "rejected",
  Closed = "closed",
}

export enum BudgetType {
  Operational = "operational",
  Capital = "capital",
  Project = "project",
  Department = "department",
}

export interface BudgetLine {
  id: string;
  accountId: string;
  originalAmount: number;
  currentAmount: number;
  usedAmount: number;
  remainingAmount: number;
  period1: number;
  period2: number;
  period3: number;
  period4: number;
  period5: number;
  period6: number;
  period7: number;
  period8: number;
  period9: number;
  period10: number;
  period11: number;
  period12: number;
}

export interface BudgetState {
  id: string;
  code: string;
  name: string;
  type: BudgetType;
  status: BudgetStatus;
  fiscalYearId: string;
  costCenterId: string | null;
  departmentId: string | null;
  projectId: string | null;
  totalOriginalAmount: number;
  totalCurrentAmount: number;
  totalUsedAmount: number;
  totalRemainingAmount: number;
  currencyCode: string;
  description: string | null;
  approvedById: string | null;
  approvedAt: Date | null;
  lines: BudgetLine[];
  createdById: string;
  createdAt: Date;
  updatedAt: Date;
  version: number;
  deletedAt: Date | null;
}

export class Budget extends AggregateRoot<BudgetId> {
  private _id!: BudgetId;
  private _code!: string;
  private _name!: string;
  private _type!: BudgetType;
  private _status: BudgetStatus = BudgetStatus.Draft;
  private _fiscalYearId!: string;
  private _costCenterId: string | null = null;
  private _departmentId: string | null = null;
  private _projectId: string | null = null;
  private _totalOriginalAmount = 0;
  private _totalCurrentAmount = 0;
  private _totalUsedAmount = 0;
  private _totalRemainingAmount = 0;
  private _currencyCode = "VND";
  private _description: string | null = null;
  private _approvedById: string | null = null;
  private _approvedAt: Date | null = null;
  private _lines: BudgetLine[] = [];
  private _createdById!: string;
  private _createdAt = new Date();
  private _updatedAt = new Date();
  private _version = 1;
  private _deletedAt: Date | null = null;

  private constructor(id: BudgetId) {
    super();
    this._id = id;
  }

  static create(params: {
    code: string;
    name: string;
    type: BudgetType;
    fiscalYearId: string;
    createdById: string;
    costCenterId?: string;
    departmentId?: string;
    projectId?: string;
    currencyCode?: string;
    description?: string;
  }): Budget {
    const b = new Budget(BudgetId.new());
    b._code = params.code;
    b._name = params.name;
    b._type = params.type;
    b._fiscalYearId = params.fiscalYearId;
    b._createdById = params.createdById;
    b._costCenterId = params.costCenterId ?? null;
    b._departmentId = params.departmentId ?? null;
    b._projectId = params.projectId ?? null;
    b._currencyCode = params.currencyCode ?? "VND";
    b._description = params.description ?? null;
    return b;
  }

  static load(state: BudgetState): Budget {
    const b = new Budget(new BudgetId(state.id));
    b._code = state.code;
    b._name = state.name;
    b._type = state.type;
    b._status = state.status;
    b._fiscalYearId = state.fiscalYearId;
    b._costCenterId = state.costCenterId;
    b._departmentId = state.departmentId;
    b._projectId = state.projectId;
    b._totalOriginalAmount = state.totalOriginalAmount;
    b._totalCurrentAmount = state.totalCurrentAmount;
    b._totalUsedAmount = state.totalUsedAmount;
    b._totalRemainingAmount = state.totalRemainingAmount;
    b._currencyCode = state.currencyCode;
    b._description = state.description;
    b._approvedById = state.approvedById;
    b._approvedAt = state.approvedAt;
    b._lines = state.lines;
    b._createdById = state.createdById;
    b._createdAt = state.createdAt;
    b._updatedAt = state.updatedAt;
    b._version = state.version;
    b._deletedAt = state.deletedAt;
    return b;
  }

  get id(): BudgetId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get type(): BudgetType { return this._type; }
  get status(): BudgetStatus { return this._status; }
  get fiscalYearId(): string { return this._fiscalYearId; }
  get costCenterId(): string | null { return this._costCenterId; }
  get departmentId(): string | null { return this._departmentId; }
  get projectId(): string | null { return this._projectId; }
  get totalOriginalAmount(): number { return this._totalOriginalAmount; }
  get totalCurrentAmount(): number { return this._totalCurrentAmount; }
  get totalUsedAmount(): number { return this._totalUsedAmount; }
  get totalRemainingAmount(): number { return this._totalRemainingAmount; }
  get currencyCode(): string { return this._currencyCode; }
  get description(): string | null { return this._description; }
  get approvedById(): string | null { return this._approvedById; }
  get approvedAt(): Date | null { return this._approvedAt; }
  get lines(): readonly BudgetLine[] { return this._lines; }
  get createdById(): string { return this._createdById; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }
  get deletedAt(): Date | null { return this._deletedAt; }

  addLine(accountId: string, amount: number, monthlyDistribution?: number[]): void {
    if (this._status !== BudgetStatus.Draft) {
      throw new DomainError("BusinessRule", "Cannot modify approved budget");
    }
    const dist = monthlyDistribution ?? Budget.distributeEvenly(amount);

    const line: BudgetLine = {
      id: IdGenerator.uuid(),
      accountId,
      originalAmount: amount,
      currentAmount: amount,
      usedAmount: 0,
      remainingAmount: amount,
      period1: dist[0], period2: dist[1], period3: dist[2], period4: dist[3],
      period5: dist[4], period6: dist[5], period7: dist[6], period8: dist[7],
      period9: dist[8], period10: dist[9], period11: dist[10], period12: dist[11],
    };

    this._lines.push(line);
    this._totalOriginalAmount += amount;
    this._totalCurrentAmount += amount;
    this._totalRemainingAmount += amount;
    this._updatedAt = new Date();
    this._version++;
  }

  checkBudget(accountId: string, amount: number, period: number): boolean {
    const line = this._lines.find(l => l.accountId === accountId);
    if (!line) return false;
    return line.remainingAmount >= amount;
  }

  consumeBudget(accountId: string, amount: number, period: number): void {
    const line = this._lines.find(l => l.accountId === accountId);
    if (!line) throw new DomainError("NotFound", `Budget line for account ${accountId} not found`);
    if (line.remainingAmount < amount) {
      throw new DomainError("BusinessRule", `Budget exceeded for account ${accountId}`);
    }
    line.usedAmount += amount;
    line.remainingAmount -= amount;
    this._totalUsedAmount += amount;
    this._totalRemainingAmount -= amount;
    this._updatedAt = new Date();
    this._version++;
  }

  approve(userId: string): void {
    if (this._status !== BudgetStatus.Submitted) {
      throw new DomainError("BusinessRule", "Only submitted budgets can be approved");
    }
    this._status = BudgetStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  submit(): void {
    if (this._status !== BudgetStatus.Draft) {
      throw new DomainError("BusinessRule", "Only draft budgets can be submitted");
    }
    if (this._lines.length === 0) throw new DomainError("BusinessRule", "Cannot submit empty budget");
    this._status = BudgetStatus.Submitted;
    this._updatedAt = new Date();
    this._version++;
  }

  reject(): void {
    this._status = BudgetStatus.Rejected;
    this._updatedAt = new Date();
    this._version++;
  }

  close(): void {
    this._status = BudgetStatus.Closed;
    this._updatedAt = new Date();
    this._version++;
  }

  private static distributeEvenly(amount: number): number[] {
    const monthly = Math.floor(amount / 12);
    const remainder = amount - monthly * 12;
    return Array.from({ length: 12 }, (_, i) => monthly + (i < remainder ? 1 : 0));
  }

  toState(): BudgetState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      type: this._type,
      status: this._status,
      fiscalYearId: this._fiscalYearId,
      costCenterId: this._costCenterId,
      departmentId: this._departmentId,
      projectId: this._projectId,
      totalOriginalAmount: this._totalOriginalAmount,
      totalCurrentAmount: this._totalCurrentAmount,
      totalUsedAmount: this._totalUsedAmount,
      totalRemainingAmount: this._totalRemainingAmount,
      currencyCode: this._currencyCode,
      description: this._description,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      lines: [...this._lines],
      createdById: this._createdById,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
      deletedAt: this._deletedAt,
    };
  }
}
