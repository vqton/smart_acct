import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PayrollPaymentId } from "./prl-ids.js";
import { PayrollPaymentCreated, PayrollPaymentConfirmed } from "./prl-events.js";

export interface PayrollPaymentLineState {
  id: string;
  paymentId: string;
  runId: string;
  lineId: string;
  employeeId: string;
  employeeCode: string;
  employeeName: string;
  netPay: bigint;
  bankName: string | null;
  bankBranch: string | null;
  accountNumber: string | null;
  accountName: string | null;
  isPaid: boolean;
  paidAt: Date | null;
  failReason: string | null;
}

export interface PayrollPaymentState {
  id: string;
  runId: string;
  paymentNumber: string;
  paymentDate: Date;
  totalAmount: bigint;
  currencyCode: string;
  paymentMethod: string;
  status: string;
  confirmedAt: Date | null;
  confirmedById: string | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
  lines: PayrollPaymentLineState[];
}

export class PayrollPayment extends AggregateRoot<PayrollPaymentId> {
  private _id: PayrollPaymentId;
  private _runId: string;
  private _paymentNumber: string;
  private _paymentDate: Date;
  private _totalAmount: bigint;
  private _currencyCode: string;
  private _paymentMethod: string;
  private _status: string;
  private _confirmedAt: Date | null;
  private _confirmedById: string | null;
  private _notes: string | null;
  private _lines: PayrollPaymentLineState[];
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: PayrollPaymentId, paymentNumber: string, runId: string, paymentDate: Date, totalAmount: bigint) {
    super();
    this._id = id;
    this._paymentNumber = paymentNumber;
    this._runId = runId;
    this._paymentDate = paymentDate;
    this._totalAmount = totalAmount;
    this._currencyCode = "VND";
    this._paymentMethod = "bank_transfer";
    this._status = "pending";
    this._confirmedAt = null;
    this._confirmedById = null;
    this._notes = null;
    this._lines = [];
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    paymentNumber: string; runId: string; paymentDate: Date;
    totalAmount: bigint; currencyCode?: string; paymentMethod?: string;
  }): PayrollPayment {
    if (!params.paymentNumber) throw new DomainError("Validation", "Payment number is required");
    if (!params.runId) throw new DomainError("Validation", "Payroll run is required");
    if (params.totalAmount < 0n) throw new DomainError("Validation", "Total amount cannot be negative");

    const pp = new PayrollPayment(PayrollPaymentId.new(), params.paymentNumber, params.runId, params.paymentDate, params.totalAmount);
    pp._currencyCode = params.currencyCode ?? "VND";
    pp._paymentMethod = params.paymentMethod ?? "bank_transfer";
    pp.addEvent(new PayrollPaymentCreated(pp._id.value, new Date(), { paymentNumber: pp._paymentNumber, runId: pp._runId }));
    return pp;
  }

  addLine(line: PayrollPaymentLineState): void {
    this._lines.push(line);
  }

  confirm(confirmedById: string): void {
    if (this._status !== "pending") throw new DomainError("BusinessRule", "Payment is not pending");
    this._status = "confirmed";
    this._confirmedById = confirmedById;
    this._confirmedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new PayrollPaymentConfirmed(this._id.value, new Date(), { paymentNumber: this._paymentNumber }));
  }

  markLinePaid(lineId: string): void {
    const line = this._lines.find(l => l.id === lineId);
    if (!line) throw new DomainError("NotFound", "Payment line not found");
    line.isPaid = true;
    line.paidAt = new Date();
  }

  markLineFailed(lineId: string, reason: string): void {
    const line = this._lines.find(l => l.id === lineId);
    if (!line) throw new DomainError("NotFound", "Payment line not found");
    line.isPaid = false;
    line.failReason = reason;
  }

  static load(state: PayrollPaymentState): PayrollPayment {
    const pp = new PayrollPayment(new PayrollPaymentId(state.id), state.paymentNumber, state.runId, state.paymentDate, state.totalAmount);
    pp._currencyCode = state.currencyCode;
    pp._paymentMethod = state.paymentMethod;
    pp._status = state.status;
    pp._confirmedAt = state.confirmedAt;
    pp._confirmedById = state.confirmedById;
    pp._notes = state.notes;
    pp._lines = state.lines ?? [];
    pp._version = state.version;
    pp._createdAt = state.createdAt;
    pp._updatedAt = state.updatedAt;
    pp._deletedAt = state.deletedAt;
    return pp;
  }

  toState(): PayrollPaymentState {
    return {
      id: this._id.value, runId: this._runId, paymentNumber: this._paymentNumber,
      paymentDate: this._paymentDate, totalAmount: this._totalAmount,
      currencyCode: this._currencyCode, paymentMethod: this._paymentMethod,
      status: this._status, confirmedAt: this._confirmedAt, confirmedById: this._confirmedById,
      notes: this._notes, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt,
      lines: this._lines,
    };
  }

  get id(): PayrollPaymentId { return this._id; }
  get runId(): string { return this._runId; }
  get paymentNumber(): string { return this._paymentNumber; }
  get totalAmount(): bigint { return this._totalAmount; }
  get status(): string { return this._status; }
  get version(): number { return this._version; }
}
