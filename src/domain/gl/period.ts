import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class PeriodId extends Identifier {
  static new(): PeriodId {
    return new PeriodId(IdGenerator.uuid());
  }
}

export class FiscalYearId extends Identifier {
  static new(): FiscalYearId {
    return new FiscalYearId(IdGenerator.uuid());
  }
}

export enum PeriodStatus {
  Open = "open",
  Closed = "closed",
  Locked = "locked",
}

export interface FiscalYearState {
  id: string;
  code: string;
  name: string;
  startDate: Date;
  endDate: Date;
  isActive: boolean;
  isClosed: boolean;
  closedAt: Date | null;
  closedById: string | null;
  periods: PeriodState[];
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export interface PeriodState {
  id: string;
  fiscalYearId: string;
  periodNumber: number;
  name: string;
  startDate: Date;
  endDate: Date;
  status: PeriodStatus;
  openedAt: Date;
  closedAt: Date | null;
  closedById: string | null;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class Period extends AggregateRoot<PeriodId> {
  private _id: PeriodId;
  private _fiscalYearId: string;
  private _periodNumber: number;
  private _name: string;
  private _startDate: Date;
  private _endDate: Date;
  private _status: PeriodStatus;
  private _openedAt: Date;
  private _closedAt: Date | null;
  private _closedById: string | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(
    id: PeriodId,
    fiscalYearId: string,
    periodNumber: number,
    name: string,
    startDate: Date,
    endDate: Date,
  ) {
    super();
    this._id = id;
    this._fiscalYearId = fiscalYearId;
    this._periodNumber = periodNumber;
    this._name = name;
    this._startDate = startDate;
    this._endDate = endDate;
    this._status = PeriodStatus.Open;
    this._openedAt = new Date();
    this._closedAt = null;
    this._closedById = null;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static load(state: PeriodState): Period {
    const p = new Period(
      new PeriodId(state.id),
      state.fiscalYearId,
      state.periodNumber,
      state.name,
      state.startDate,
      state.endDate,
    );
    p._status = state.status;
    p._openedAt = state.openedAt;
    p._closedAt = state.closedAt;
    p._closedById = state.closedById;
    p._createdAt = state.createdAt;
    p._updatedAt = state.updatedAt;
    p._version = state.version;
    return p;
  }

  get id(): PeriodId { return this._id; }
  get fiscalYearId(): string { return this._fiscalYearId; }
  get periodNumber(): number { return this._periodNumber; }
  get name(): string { return this._name; }
  get startDate(): Date { return this._startDate; }
  get endDate(): Date { return this._endDate; }
  get status(): PeriodStatus { return this._status; }
  get openedAt(): Date { return this._openedAt; }
  get closedAt(): Date | null { return this._closedAt; }
  get closedById(): string | null { return this._closedById; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }

  canPost(): void {
    if (this._status === PeriodStatus.Closed) {
      throw new DomainError("BusinessRule", `Period ${this._name} is closed`);
    }
    if (this._status === PeriodStatus.Locked) {
      throw new DomainError("BusinessRule", `Period ${this._name} is locked`);
    }
  }

  close(userId: string): void {
    if (this._status === PeriodStatus.Closed) {
      throw new DomainError("BusinessRule", `Period ${this._name} is already closed`);
    }
    this._status = PeriodStatus.Closed;
    this._closedAt = new Date();
    this._closedById = userId;
    this._updatedAt = new Date();
    this._version++;
  }

  lock(): void {
    this._status = PeriodStatus.Locked;
    this._updatedAt = new Date();
    this._version++;
  }

  reopen(): void {
    if (this._status !== PeriodStatus.Closed) {
      throw new DomainError("BusinessRule", "Only closed periods can be reopened");
    }
    this._status = PeriodStatus.Open;
    this._closedAt = null;
    this._closedById = null;
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): PeriodState {
    return {
      id: this._id.value,
      fiscalYearId: this._fiscalYearId,
      periodNumber: this._periodNumber,
      name: this._name,
      startDate: this._startDate,
      endDate: this._endDate,
      status: this._status,
      openedAt: this._openedAt,
      closedAt: this._closedAt,
      closedById: this._closedById,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
    };
  }
}

export class FiscalYearClosed implements DomainEvent {
  readonly eventName = "FiscalYearClosed";
  constructor(
    readonly aggregateId: string,
    readonly occurredAt: Date,
    readonly payload: Record<string, unknown>,
  ) {}
}

export class FiscalYear extends AggregateRoot<FiscalYearId> {
  private _id: FiscalYearId;
  private _code: string;
  private _name: string;
  private _startDate: Date;
  private _endDate: Date;
  private _isActive: boolean;
  private _isClosed: boolean;
  private _closedAt: Date | null;
  private _closedById: string | null;
  private _periods: Period[];
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  constructor(
    id: FiscalYearId,
    code: string,
    name: string,
    startDate: Date,
    endDate: Date,
  ) {
    super();
    this._id = id;
    this._code = code;
    this._name = name;
    this._startDate = startDate;
    this._endDate = endDate;
    this._isActive = true;
    this._isClosed = false;
    this._closedAt = null;
    this._closedById = null;
    this._periods = [];
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static load(state: FiscalYearState): FiscalYear {
    const fy = new FiscalYear(
      new FiscalYearId(state.id),
      state.code,
      state.name,
      state.startDate,
      state.endDate,
    );
    fy._isActive = state.isActive;
    fy._isClosed = state.isClosed;
    fy._closedAt = state.closedAt;
    fy._closedById = state.closedById;
    fy._periods = state.periods.map(p => Period.load(p));
    fy._createdAt = state.createdAt;
    fy._updatedAt = state.updatedAt;
    fy._version = state.version;
    return fy;
  }

  get id(): FiscalYearId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get startDate(): Date { return this._startDate; }
  get endDate(): Date { return this._endDate; }
  get isActive(): boolean { return this._isActive; }
  get isClosed(): boolean { return this._isClosed; }
  get closedAt(): Date | null { return this._closedAt; }
  get closedById(): string | null { return this._closedById; }
  get periods(): readonly Period[] { return this._periods; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }

  addPeriod(period: Period): void {
    if (this._isClosed) {
      throw new DomainError("BusinessRule", "Cannot add period to closed fiscal year");
    }
    const exists = this._periods.find(p => p.periodNumber === period.periodNumber);
    if (exists) throw new DomainError("BusinessRule", `Period ${period.periodNumber} already exists`);
    this._periods.push(period);
    this._updatedAt = new Date();
    this._version++;
  }

  generatePeriods(periodType: "monthly" | "quarterly" = "monthly"): void {
    if (periodType === "monthly") {
      for (let m = 0; m < 12; m++) {
        const start = new Date(this._startDate.getFullYear(), m, 1);
        const end = new Date(this._startDate.getFullYear(), m + 1, 0);
        const period = new Period(
          PeriodId.new(),
          this._id.value,
          m + 1,
          `Tháng ${m + 1}`,
          start,
          end,
        );
        this._periods.push(period);
      }
    }
  }

  getPeriodByDate(date: Date): Period | undefined {
    return this._periods.find(
      p => date >= p.startDate && date <= p.endDate && p.status === PeriodStatus.Open,
    );
  }

  canPost(): void {
    if (this._isClosed) {
      throw new DomainError("BusinessRule", `Fiscal year ${this._code} is closed`);
    }
  }

  close(userId: string): void {
    const openPeriods = this._periods.filter(p => p.status !== PeriodStatus.Closed);
    if (openPeriods.length > 0) {
      throw new DomainError("BusinessRule", "All periods must be closed before closing fiscal year");
    }
    this._isClosed = true;
    this._closedAt = new Date();
    this._closedById = userId;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new FiscalYearClosed(this._id.value, new Date(), {
      userId,
      code: this._code,
    }));
  }

  toState(): FiscalYearState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      startDate: this._startDate,
      endDate: this._endDate,
      isActive: this._isActive,
      isClosed: this._isClosed,
      closedAt: this._closedAt,
      closedById: this._closedById,
      periods: this._periods.map(p => p.toState()),
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
    };
  }
}
