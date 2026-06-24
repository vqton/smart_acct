import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { FrConsolidationGroupId, FrConsolidationRunId, FrConsolidationEntryId } from "./fr-ids.js";
import { FrConsolidationMethod, FrConsolidationStatus, FrEliminationType } from "./fr-enums.js";
import { ConsolidationRunStarted, ConsolidationRunCompleted, ConsolidationEntryCreated } from "./fr-events.js";
import { ConsolidationGroupMember, ConsolidationEliminationEntry } from "./fr-value-objects.js";

// ─── Consolidation Group ──────────────────────────────────────────────────

export interface ConsolidationGroupState {
  id: string;
  code: string;
  name: string;
  description: string | null;
  parentCompanyId: string;
  currencyCode: string;
  members: Array<{
    legalEntityId: string;
    legalEntityCode: string;
    legalEntityName: string;
    ownershipPercentage: number;
    consolidationMethod: string;
    consolidationDate: Date;
    functionalCurrency: string;
    goodwillAmount: number;
    isActive: boolean;
  }>;
  isActive: boolean;
  version: number;
  createdById: string;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class ConsolidationGroup extends AggregateRoot<FrConsolidationGroupId> {
  private _id!: FrConsolidationGroupId;
  private _code!: string;
  private _name!: string;
  private _description: string | null = null;
  private _parentCompanyId!: string;
  private _currencyCode = "VND";
  private _members: ConsolidationGroupMember[] = [];
  private _isActive = true;
  private _version = 1;
  private _createdById!: string;
  private _createdAt: Date = new Date();
  private _updatedAt: Date = new Date();
  private _deletedAt: Date | null = null;

  private constructor(id: FrConsolidationGroupId) { super(); this._id = id; }

  static create(params: {
    code: string;
    name: string;
    description?: string;
    parentCompanyId: string;
    currencyCode?: string;
    createdById: string;
  }): ConsolidationGroup {
    const g = new ConsolidationGroup(FrConsolidationGroupId.new());
    g._code = params.code;
    g._name = params.name;
    g._description = params.description ?? null;
    g._parentCompanyId = params.parentCompanyId;
    g._currencyCode = params.currencyCode ?? "VND";
    g._createdById = params.createdById;
    return g;
  }

  static load(state: ConsolidationGroupState): ConsolidationGroup {
    const g = new ConsolidationGroup(new FrConsolidationGroupId(state.id));
    g._code = state.code;
    g._name = state.name;
    g._description = state.description;
    g._parentCompanyId = state.parentCompanyId;
    g._currencyCode = state.currencyCode;
    g._members = state.members.map(m => new ConsolidationGroupMember(
      m.legalEntityId, m.legalEntityCode, m.legalEntityName,
      m.ownershipPercentage, m.consolidationMethod,
      m.consolidationDate, m.functionalCurrency,
      m.goodwillAmount, m.isActive,
    ));
    g._isActive = state.isActive;
    g._version = state.version;
    g._createdById = state.createdById;
    g._createdAt = state.createdAt;
    g._updatedAt = state.updatedAt;
    g._deletedAt = state.deletedAt;
    return g;
  }

  get id(): FrConsolidationGroupId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get parentCompanyId(): string { return this._parentCompanyId; }
  get currencyCode(): string { return this._currencyCode; }
  get members(): readonly ConsolidationGroupMember[] { return this._members; }
  get isActive(): boolean { return this._isActive; }
  get createdById(): string { return this._createdById; }

  addMember(member: ConsolidationGroupMember): void {
    const exists = this._members.some(m => m.legalEntityId === member.legalEntityId);
    if (exists) throw new DomainError("Conflict", "Member already exists in group");
    this._members.push(member);
    this._updatedAt = new Date();
    this._version++;
  }

  removeMember(legalEntityId: string): void {
    const idx = this._members.findIndex(m => m.legalEntityId === legalEntityId);
    if (idx < 0) throw new DomainError("NotFound", "Member not found");
    this._members.splice(idx, 1);
    this._updatedAt = new Date();
    this._version++;
  }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
    this._version++;
  }

  markDeleted(): void {
    this._deletedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): ConsolidationGroupState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      description: this._description,
      parentCompanyId: this._parentCompanyId,
      currencyCode: this._currencyCode,
      members: this._members.map(m => ({
        legalEntityId: m.legalEntityId,
        legalEntityCode: m.legalEntityCode,
        legalEntityName: m.legalEntityName,
        ownershipPercentage: m.ownershipPercentage,
        consolidationMethod: m.consolidationMethod,
        consolidationDate: m.consolidationDate,
        functionalCurrency: m.functionalCurrency,
        goodwillAmount: m.goodwillAmount,
        isActive: m.isActive,
      })),
      isActive: this._isActive,
      version: this._version,
      createdById: this._createdById,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}

// ─── Consolidation Run ────────────────────────────────────────────────────

export interface ConsolidationRunState {
  id: string;
  groupId: string;
  runNumber: string;
  status: FrConsolidationStatus;
  fiscalYearId: string;
  periodId: string | null;
  periodNumber: number;
  periodName: string;
  asOfDate: Date;
  reportingCurrency: string;
  entries: Array<{
    eliminationType: FrEliminationType;
    fromEntityId: string | null;
    toEntityId: string | null;
    accountCode: string;
    debitAmount: number;
    creditAmount: number;
    description: string | null;
    isAutoDetected: boolean;
    sourceBatchId: string | null;
  }>;
  preparedById: string;
  reviewedById: string | null;
  approvedById: string | null;
  errorMessage: string | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class ConsolidationRun extends AggregateRoot<FrConsolidationRunId> {
  private _id!: FrConsolidationRunId;
  private _groupId!: string;
  private _runNumber!: string;
  private _status: FrConsolidationStatus = FrConsolidationStatus.Draft;
  private _fiscalYearId!: string;
  private _periodId: string | null = null;
  private _periodNumber!: number;
  private _periodName!: string;
  private _asOfDate!: Date;
  private _reportingCurrency = "VND";
  private _entries: ConsolidationEliminationEntry[] = [];
  private _preparedById!: string;
  private _reviewedById: string | null = null;
  private _approvedById: string | null = null;
  private _errorMessage: string | null = null;
  private _notes: string | null = null;
  private _version = 1;
  private _createdAt: Date = new Date();
  private _updatedAt: Date = new Date();
  private _deletedAt: Date | null = null;

  private constructor(id: FrConsolidationRunId) { super(); this._id = id; }

  static create(params: {
    groupId: string;
    runNumber: string;
    fiscalYearId: string;
    periodId?: string;
    periodNumber: number;
    periodName: string;
    asOfDate: Date;
    reportingCurrency?: string;
    preparedById: string;
  }): ConsolidationRun {
    const r = new ConsolidationRun(FrConsolidationRunId.new());
    r._groupId = params.groupId;
    r._runNumber = params.runNumber;
    r._fiscalYearId = params.fiscalYearId;
    r._periodId = params.periodId ?? null;
    r._periodNumber = params.periodNumber;
    r._periodName = params.periodName;
    r._asOfDate = params.asOfDate;
    r._reportingCurrency = params.reportingCurrency ?? "VND";
    r._preparedById = params.preparedById;

    r.addEvent(new ConsolidationRunStarted(r._id.value, new Date(), {
      runNumber: r._runNumber,
      groupId: r._groupId,
      periodNumber: r._periodNumber,
    }));

    return r;
  }

  static load(state: ConsolidationRunState): ConsolidationRun {
    const r = new ConsolidationRun(new FrConsolidationRunId(state.id));
    r._groupId = state.groupId;
    r._runNumber = state.runNumber;
    r._status = state.status;
    r._fiscalYearId = state.fiscalYearId;
    r._periodId = state.periodId;
    r._periodNumber = state.periodNumber;
    r._periodName = state.periodName;
    r._asOfDate = state.asOfDate;
    r._reportingCurrency = state.reportingCurrency;
    r._entries = state.entries.map(e => new ConsolidationEliminationEntry(
      e.eliminationType, e.fromEntityId, e.toEntityId,
      e.accountCode, e.debitAmount, e.creditAmount,
      e.description, e.isAutoDetected, e.sourceBatchId,
    ));
    r._preparedById = state.preparedById;
    r._reviewedById = state.reviewedById;
    r._approvedById = state.approvedById;
    r._errorMessage = state.errorMessage;
    r._notes = state.notes;
    r._version = state.version;
    r._createdAt = state.createdAt;
    r._updatedAt = state.updatedAt;
    r._deletedAt = state.deletedAt;
    return r;
  }

  get id(): FrConsolidationRunId { return this._id; }
  get groupId(): string { return this._groupId; }
  get runNumber(): string { return this._runNumber; }
  get status(): FrConsolidationStatus { return this._status; }
  get fiscalYearId(): string { return this._fiscalYearId; }
  get periodNumber(): number { return this._periodNumber; }
  get entries(): readonly ConsolidationEliminationEntry[] { return this._entries; }
  get preparedById(): string { return this._preparedById; }

  addEntry(entry: ConsolidationEliminationEntry): void {
    this._entries.push(entry);
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new ConsolidationEntryCreated(this._id.value, new Date(), {
      accountCode: entry.accountCode,
      eliminationType: entry.eliminationType,
    }));
  }

  complete(): void {
    const unbalanced = this._entries.filter(e => !e.isBalanced);
    if (unbalanced.length > 0) {
      throw new DomainError("BusinessRule", `Unbalanced entries: ${unbalanced.length}`);
    }
    this._status = FrConsolidationStatus.Completed;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new ConsolidationRunCompleted(this._id.value, new Date(), {
      runNumber: this._runNumber,
      entryCount: this._entries.length,
    }));
  }

  verify(userId: string): void {
    if (this._status !== FrConsolidationStatus.Completed) {
      throw new DomainError("BusinessRule", "Only completed runs can be verified");
    }
    this._status = FrConsolidationStatus.Verified;
    this._reviewedById = userId;
    this._updatedAt = new Date();
    this._version++;
  }

  approve(userId: string): void {
    if (this._status !== FrConsolidationStatus.Verified) {
      throw new DomainError("BusinessRule", "Only verified runs can be approved");
    }
    this._status = FrConsolidationStatus.Approved;
    this._approvedById = userId;
    this._updatedAt = new Date();
    this._version++;
  }

  fail(error: string): void {
    this._status = FrConsolidationStatus.Draft;
    this._errorMessage = error;
    this._updatedAt = new Date();
  }

  markDeleted(): void {
    this._deletedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): ConsolidationRunState {
    return {
      id: this._id.value,
      groupId: this._groupId,
      runNumber: this._runNumber,
      status: this._status,
      fiscalYearId: this._fiscalYearId,
      periodId: this._periodId,
      periodNumber: this._periodNumber,
      periodName: this._periodName,
      asOfDate: this._asOfDate,
      reportingCurrency: this._reportingCurrency,
      entries: this._entries.map(e => ({
        eliminationType: e.eliminationType as FrEliminationType,
        fromEntityId: e.fromEntityId,
        toEntityId: e.toEntityId,
        accountCode: e.accountCode,
        debitAmount: e.debitAmount,
        creditAmount: e.creditAmount,
        description: e.description,
        isAutoDetected: e.isAutoDetected,
        sourceBatchId: e.sourceBatchId,
      })),
      preparedById: this._preparedById,
      reviewedById: this._reviewedById,
      approvedById: this._approvedById,
      errorMessage: this._errorMessage,
      notes: this._notes,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
