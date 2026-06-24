import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { FrReportInstanceId } from "./fr-ids.js";
import { FrInstanceStatus } from "./fr-enums.js";
import { ReportInstanceGenerated, ReportInstanceApproved } from "./fr-events.js";

export interface ReportInstanceRowValue {
  rowDefId: string | null;
  parentRowId: string | null;
  rowType: string;
  rowCode: string | null;
  label: string;
  displayOrder: number;
  indentLevel: number;
  isBold: boolean;
  values: Record<string, number>;
}

export interface ReportInstanceState {
  id: string;
  reportDefId: string;
  instanceNumber: string;
  status: FrInstanceStatus;
  fiscalYearId: string;
  periodId: string | null;
  periodNumber: number | null;
  periodName: string | null;
  asOfDate: string | null;
  legalEntityId: string | null;
  consolidationRunId: string | null;
  reportingCurrency: string;
  exchangeRate: number;
  rows: ReportInstanceRowValue[];
  generatedById: string;
  generatedAt: Date;
  approvedById: string | null;
  approvedAt: Date | null;
  errorMessage: string | null;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class ReportInstance extends AggregateRoot<FrReportInstanceId> {
  private _id!: FrReportInstanceId;
  private _reportDefId!: string;
  private _instanceNumber!: string;
  private _status: FrInstanceStatus = FrInstanceStatus.Generating;
  private _fiscalYearId!: string;
  private _periodId: string | null = null;
  private _periodNumber: number | null = null;
  private _periodName: string | null = null;
  private _asOfDate: string | null = null;
  private _legalEntityId: string | null = null;
  private _consolidationRunId: string | null = null;
  private _reportingCurrency = "VND";
  private _exchangeRate = 1;
  private _rows: ReportInstanceRowValue[] = [];
  private _generatedById!: string;
  private _generatedAt: Date = new Date();
  private _approvedById: string | null = null;
  private _approvedAt: Date | null = null;
  private _errorMessage: string | null = null;
  private _createdAt: Date = new Date();
  private _updatedAt: Date = new Date();
  private _deletedAt: Date | null = null;

  private constructor(id: FrReportInstanceId) { super(); this._id = id; }

  static create(params: {
    reportDefId: string;
    instanceNumber: string;
    fiscalYearId: string;
    periodId?: string;
    periodNumber?: number;
    periodName?: string;
    asOfDate?: string;
    legalEntityId?: string;
    consolidationRunId?: string;
    reportingCurrency?: string;
    exchangeRate?: number;
    generatedById: string;
  }): ReportInstance {
    const inst = new ReportInstance(FrReportInstanceId.new());
    inst._reportDefId = params.reportDefId;
    inst._instanceNumber = params.instanceNumber;
    inst._fiscalYearId = params.fiscalYearId;
    inst._periodId = params.periodId ?? null;
    inst._periodNumber = params.periodNumber ?? null;
    inst._periodName = params.periodName ?? null;
    inst._asOfDate = params.asOfDate ?? null;
    inst._legalEntityId = params.legalEntityId ?? null;
    inst._consolidationRunId = params.consolidationRunId ?? null;
    inst._reportingCurrency = params.reportingCurrency ?? "VND";
    inst._exchangeRate = params.exchangeRate ?? 1;
    inst._generatedById = params.generatedById;
    return inst;
  }

  static load(state: ReportInstanceState): ReportInstance {
    const inst = new ReportInstance(new FrReportInstanceId(state.id));
    inst._reportDefId = state.reportDefId;
    inst._instanceNumber = state.instanceNumber;
    inst._status = state.status;
    inst._fiscalYearId = state.fiscalYearId;
    inst._periodId = state.periodId;
    inst._periodNumber = state.periodNumber;
    inst._periodName = state.periodName;
    inst._asOfDate = state.asOfDate;
    inst._legalEntityId = state.legalEntityId;
    inst._consolidationRunId = state.consolidationRunId;
    inst._reportingCurrency = state.reportingCurrency;
    inst._exchangeRate = state.exchangeRate;
    inst._rows = state.rows;
    inst._generatedById = state.generatedById;
    inst._generatedAt = state.generatedAt;
    inst._approvedById = state.approvedById;
    inst._approvedAt = state.approvedAt;
    inst._errorMessage = state.errorMessage;
    inst._createdAt = state.createdAt;
    inst._updatedAt = state.updatedAt;
    inst._deletedAt = state.deletedAt;
    return inst;
  }

  get id(): FrReportInstanceId { return this._id; }
  get reportDefId(): string { return this._reportDefId; }
  get instanceNumber(): string { return this._instanceNumber; }
  get status(): FrInstanceStatus { return this._status; }
  get fiscalYearId(): string { return this._fiscalYearId; }
  get periodId(): string | null { return this._periodId; }
  get periodNumber(): number | null { return this._periodNumber; }
  get legalEntityId(): string | null { return this._legalEntityId; }
  get consolidationRunId(): string | null { return this._consolidationRunId; }
  get reportingCurrency(): string { return this._reportingCurrency; }
  get rows(): readonly ReportInstanceRowValue[] { return this._rows; }
  get generatedById(): string { return this._generatedById; }
  get generatedAt(): Date { return this._generatedAt; }
  get approvedById(): string | null { return this._approvedById; }
  get errorMessage(): string | null { return this._errorMessage; }

  complete(rows: ReportInstanceRowValue[]): void {
    this._rows = rows;
    this._status = FrInstanceStatus.Completed;
    this._updatedAt = new Date();
    this.addEvent(new ReportInstanceGenerated(this._id.value, new Date(), {
      reportDefId: this._reportDefId,
      instanceNumber: this._instanceNumber,
      rowCount: rows.length,
    }));
  }

  fail(error: string): void {
    this._status = FrInstanceStatus.Failed;
    this._errorMessage = error;
    this._updatedAt = new Date();
  }

  approve(userId: string): void {
    if (this._status !== FrInstanceStatus.Completed) {
      throw new DomainError("BusinessRule", "Only completed instances can be approved");
    }
    this._status = FrInstanceStatus.Approved;
    this._approvedById = userId;
    this._approvedAt = new Date();
    this._updatedAt = new Date();
    this.addEvent(new ReportInstanceApproved(this._id.value, new Date(), {
      userId,
      instanceNumber: this._instanceNumber,
    }));
  }

  lock(): void {
    if (this._status !== FrInstanceStatus.Approved) {
      throw new DomainError("BusinessRule", "Only approved instances can be locked");
    }
    this._status = FrInstanceStatus.Locked;
    this._updatedAt = new Date();
  }

  toState(): ReportInstanceState {
    return {
      id: this._id.value,
      reportDefId: this._reportDefId,
      instanceNumber: this._instanceNumber,
      status: this._status,
      fiscalYearId: this._fiscalYearId,
      periodId: this._periodId,
      periodNumber: this._periodNumber,
      periodName: this._periodName,
      asOfDate: this._asOfDate,
      legalEntityId: this._legalEntityId,
      consolidationRunId: this._consolidationRunId,
      reportingCurrency: this._reportingCurrency,
      exchangeRate: this._exchangeRate,
      rows: [...this._rows],
      generatedById: this._generatedById,
      generatedAt: this._generatedAt,
      approvedById: this._approvedById,
      approvedAt: this._approvedAt,
      errorMessage: this._errorMessage,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}
