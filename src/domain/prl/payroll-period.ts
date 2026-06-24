import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PayrollPeriodId } from "./prl-ids.js";

export interface PayrollPeriodState {
  id: string;
  calendarId: string;
  periodNumber: number;
  name: string;
  startDate: Date;
  endDate: Date;
  paymentDate: Date | null;
  year: number;
  month: number;
  isClosed: boolean;
  closedAt: Date | null;
  closedById: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class PayrollPeriod extends AggregateRoot<PayrollPeriodId> {
  private _id: PayrollPeriodId;
  private _calendarId: string;
  private _periodNumber: number;
  private _name: string;
  private _startDate: Date;
  private _endDate: Date;
  private _paymentDate: Date | null;
  private _year: number;
  private _month: number;
  private _isClosed: boolean;
  private _closedAt: Date | null;
  private _closedById: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: PayrollPeriodId, calendarId: string, periodNumber: number, name: string, startDate: Date, endDate: Date, year: number, month: number) {
    super();
    this._id = id;
    this._calendarId = calendarId;
    this._periodNumber = periodNumber;
    this._name = name;
    this._startDate = startDate;
    this._endDate = endDate;
    this._year = year;
    this._month = month;
    this._paymentDate = null;
    this._isClosed = false;
    this._closedAt = null;
    this._closedById = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    calendarId: string; periodNumber: number; name: string;
    startDate: Date; endDate: Date; year: number; month: number;
    paymentDate?: Date;
  }): PayrollPeriod {
    if (params.endDate <= params.startDate) throw new DomainError("Validation", "End date must be after start date");
    const pp = new PayrollPeriod(PayrollPeriodId.new(), params.calendarId, params.periodNumber, params.name, params.startDate, params.endDate, params.year, params.month);
    pp._paymentDate = params.paymentDate ?? null;
    return pp;
  }

  close(closedById: string): void {
    if (this._isClosed) throw new DomainError("BusinessRule", "Period already closed");
    this._isClosed = true;
    this._closedById = closedById;
    this._closedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
  }

  open(): void {
    if (!this._isClosed) throw new DomainError("BusinessRule", "Period already open");
    this._isClosed = false;
    this._closedById = null;
    this._closedAt = null;
    this._version++;
    this._updatedAt = new Date();
  }

  contains(date: Date): boolean {
    return date >= this._startDate && date <= this._endDate;
  }

  static load(state: PayrollPeriodState): PayrollPeriod {
    const pp = new PayrollPeriod(new PayrollPeriodId(state.id), state.calendarId, state.periodNumber, state.name, state.startDate, state.endDate, state.year, state.month);
    pp._paymentDate = state.paymentDate;
    pp._isClosed = state.isClosed;
    pp._closedAt = state.closedAt;
    pp._closedById = state.closedById;
    pp._version = state.version;
    pp._createdAt = state.createdAt;
    pp._updatedAt = state.updatedAt;
    pp._deletedAt = state.deletedAt;
    return pp;
  }

  toState(): PayrollPeriodState {
    return {
      id: this._id.value, calendarId: this._calendarId, periodNumber: this._periodNumber,
      name: this._name, startDate: this._startDate, endDate: this._endDate,
      paymentDate: this._paymentDate, year: this._year, month: this._month,
      isClosed: this._isClosed, closedAt: this._closedAt, closedById: this._closedById,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }

  get id(): PayrollPeriodId { return this._id; }
  get name(): string { return this._name; }
  get startDate(): Date { return this._startDate; }
  get endDate(): Date { return this._endDate; }
  get year(): number { return this._year; }
  get month(): number { return this._month; }
  get isClosed(): boolean { return this._isClosed; }
  get version(): number { return this._version; }
}
