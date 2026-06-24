import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { ReceivableAccountId } from "./sales-ids.js";
import { ReceivableCreated, ReceivablePaid, ReceivableWrittenOff } from "./sales-events.js";

export interface ReceivableAccountState {
  id: string; customerId: string; invoiceId: string; invoiceNumber: string;
  companyId: string; branchId: string | null;
  originalAmount: number; outstandingAmount: number; paidAmount: number;
  discountedAmount: number; writtenOffAmount: number;
  currencyCode: string; exchangeRate: number;
  invoiceDate: Date; dueDate: Date; lastPaymentDate: Date | null;
  agingDays: number; agingBucket: string | null;
  status: string; isOverdue: boolean; isDisputed: boolean;
  dunningLevel: number; lastDunningDate: Date | null; dunningCount: number;
  assignedCollector: string | null; promiseDate: Date | null; promiseAmount: number;
  writtenOffAt: Date | null; writeOffReason: string | null; approvedBy: string | null;
  isBadDebt: boolean; badDebtAmount: number; badDebtProvision: number;
  glBatchId: string | null; postedToGL: boolean;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class ReceivableAccount extends AggregateRoot<ReceivableAccountId> {
  private _id: ReceivableAccountId; private _customerId: string; private _invoiceId: string;
  private _invoiceNumber: string; private _companyId: string; private _branchId: string | null;
  private _originalAmount: number; private _outstandingAmount: number;
  private _paidAmount: number; private _discountedAmount: number;
  private _writtenOffAmount: number; private _currencyCode: string;
  private _exchangeRate: number; private _invoiceDate: Date; private _dueDate: Date;
  private _lastPaymentDate: Date | null; private _agingDays: number;
  private _agingBucket: string | null; private _status: string;
  private _isOverdue: boolean; private _isDisputed: boolean;
  private _dunningLevel: number; private _lastDunningDate: Date | null;
  private _dunningCount: number; private _assignedCollector: string | null;
  private _promiseDate: Date | null; private _promiseAmount: number;
  private _writtenOffAt: Date | null; private _writeOffReason: string | null;
  private _approvedBy: string | null; private _isBadDebt: boolean;
  private _badDebtAmount: number; private _badDebtProvision: number;
  private _glBatchId: string | null; private _postedToGL: boolean;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: ReceivableAccountId, customerId: string, invoiceId: string, invoiceNumber: string, companyId: string, originalAmount: number, dueDate: Date) {
    super(); this._id = id; this._customerId = customerId; this._invoiceId = invoiceId;
    this._invoiceNumber = invoiceNumber; this._companyId = companyId;
    this._originalAmount = originalAmount; this._outstandingAmount = originalAmount;
    this._dueDate = dueDate; this._currencyCode = "VND"; this._exchangeRate = 1;
    this._paidAmount = 0; this._discountedAmount = 0; this._writtenOffAmount = 0;
    this._invoiceDate = new Date(); this._agingDays = 0; this._branchId = null;
    this._lastPaymentDate = null; this._agingBucket = null; this._status = "outstanding";
    this._isOverdue = false; this._isDisputed = false;
    this._dunningLevel = 0; this._lastDunningDate = null; this._dunningCount = 0;
    this._assignedCollector = null; this._promiseDate = null; this._promiseAmount = 0;
    this._writtenOffAt = null; this._writeOffReason = null; this._approvedBy = null;
    this._isBadDebt = false; this._badDebtAmount = 0; this._badDebtProvision = 0;
    this._glBatchId = null; this._postedToGL = false;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(customerId: string, invoiceId: string, invoiceNumber: string, companyId: string, originalAmount: number, dueDate: Date, branchId?: string, currencyCode?: string, exchangeRate?: number): ReceivableAccount {
    const a = new ReceivableAccount(ReceivableAccountId.new(), customerId, invoiceId, invoiceNumber, companyId, originalAmount, dueDate);
    a._branchId = branchId ?? null; a._currencyCode = currencyCode ?? "VND";
    a._exchangeRate = exchangeRate ?? 1; a._invoiceDate = new Date();
    a.addEvent(new ReceivableCreated(a._id.value, new Date(), { invoiceId, invoiceNumber, customerId, amount: originalAmount }));
    return a;
  }

  static load(s: ReceivableAccountState): ReceivableAccount {
    const a = new ReceivableAccount(new ReceivableAccountId(s.id), s.customerId, s.invoiceId, s.invoiceNumber, s.companyId, s.originalAmount, s.dueDate);
    a._branchId = s.branchId; a._outstandingAmount = s.outstandingAmount;
    a._paidAmount = s.paidAmount; a._discountedAmount = s.discountedAmount;
    a._writtenOffAmount = s.writtenOffAmount; a._currencyCode = s.currencyCode;
    a._exchangeRate = s.exchangeRate; a._invoiceDate = s.invoiceDate;
    a._lastPaymentDate = s.lastPaymentDate; a._agingDays = s.agingDays;
    a._agingBucket = s.agingBucket; a._status = s.status; a._isOverdue = s.isOverdue;
    a._isDisputed = s.isDisputed; a._dunningLevel = s.dunningLevel;
    a._lastDunningDate = s.lastDunningDate; a._dunningCount = s.dunningCount;
    a._assignedCollector = s.assignedCollector; a._promiseDate = s.promiseDate;
    a._promiseAmount = s.promiseAmount; a._writtenOffAt = s.writtenOffAt;
    a._writeOffReason = s.writeOffReason; a._approvedBy = s.approvedBy;
    a._isBadDebt = s.isBadDebt; a._badDebtAmount = s.badDebtAmount;
    a._badDebtProvision = s.badDebtProvision; a._glBatchId = s.glBatchId;
    a._postedToGL = s.postedToGL; a._version = s.version; a._createdAt = s.createdAt;
    a._updatedAt = s.updatedAt; a._deletedAt = s.deletedAt;
    return a;
  }

  get id(): ReceivableAccountId { return this._id; }
  get invoiceId(): string { return this._invoiceId; }
  get invoiceNumber(): string { return this._invoiceNumber; }
  get outstandingAmount(): number { return this._outstandingAmount; }
  get status(): string { return this._status; }
  get version(): number { return this._version; }
  get isOverdue(): boolean { return this._isOverdue; }

  recordPayment(amount: number, paymentDate: Date): void {
    if (amount <= 0) throw new DomainError("Validation", "Payment amount must be positive");
    if (amount > this._outstandingAmount) throw new DomainError("BusinessRule", "Payment exceeds outstanding amount");
    this._paidAmount += amount;
    this._outstandingAmount = this._originalAmount - this._paidAmount - this._discountedAmount - this._writtenOffAmount;
    this._lastPaymentDate = paymentDate;
    if (this._outstandingAmount <= 0) {
      this._status = "paid";
      this._outstandingAmount = 0;
    } else {
      this._status = "partially_paid";
    }
    this._updatedAt = new Date(); this._version++;
    this.updateAging();
    this.addEvent(new ReceivablePaid(this._id.value, new Date(), { invoiceId: this._invoiceId, amount, remaining: this._outstandingAmount }));
  }

  applyDiscount(amount: number): void {
    if (amount > this._outstandingAmount) throw new DomainError("BusinessRule", "Discount exceeds outstanding");
    this._discountedAmount += amount;
    this._outstandingAmount = this._originalAmount - this._paidAmount - this._discountedAmount - this._writtenOffAmount;
    this._updatedAt = new Date(); this._version++;
  }

  writeOff(amount: number, reason: string, approvedBy: string): void {
    if (amount > this._outstandingAmount) throw new DomainError("BusinessRule", "Write-off exceeds outstanding");
    this._writtenOffAmount += amount;
    this._outstandingAmount -= amount;
    this._writeOffReason = reason; this._writtenOffAt = new Date();
    this._approvedBy = approvedBy; this._isBadDebt = true;
    this._badDebtAmount += amount;
    if (this._outstandingAmount <= 0) this._status = "written_off";
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new ReceivableWrittenOff(this._id.value, new Date(), { invoiceId: this._invoiceId, amount, reason }));
  }

  markDisputed(): void {
    this._isDisputed = true;
    this._updatedAt = new Date(); this._version++;
  }

  markDisputeResolved(): void {
    this._isDisputed = false;
    this._updatedAt = new Date(); this._version++;
  }

  recordDunning(level: number): void {
    this._dunningLevel = level;
    this._lastDunningDate = new Date();
    this._dunningCount++;
    this._updatedAt = new Date(); this._version++;
  }

  setPromise(promiseDate: Date, promiseAmount: number): void {
    this._promiseDate = promiseDate; this._promiseAmount = promiseAmount;
    this._updatedAt = new Date(); this._version++;
  }

  updateAging(): void {
    const now = new Date();
    const diffTime = now.getTime() - this._dueDate.getTime();
    this._agingDays = Math.max(0, Math.floor(diffTime / (1000 * 60 * 60 * 24)));
    this._isOverdue = this._agingDays > 0 && this._outstandingAmount > 0;
    if (this._agingDays <= 0) this._agingBucket = "current";
    else if (this._agingDays <= 30) this._agingBucket = "1_30";
    else if (this._agingDays <= 60) this._agingBucket = "31_60";
    else if (this._agingDays <= 90) this._agingBucket = "61_90";
    else if (this._agingDays <= 180) this._agingBucket = "91_180";
    else this._agingBucket = "over_180";
  }

  markPosted(glBatchId: string): void {
    this._glBatchId = glBatchId; this._postedToGL = true;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): ReceivableAccountState {
    return { id: this._id.value, customerId: this._customerId, invoiceId: this._invoiceId,
      invoiceNumber: this._invoiceNumber, companyId: this._companyId, branchId: this._branchId,
      originalAmount: this._originalAmount, outstandingAmount: this._outstandingAmount,
      paidAmount: this._paidAmount, discountedAmount: this._discountedAmount,
      writtenOffAmount: this._writtenOffAmount, currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate, invoiceDate: this._invoiceDate, dueDate: this._dueDate,
      lastPaymentDate: this._lastPaymentDate, agingDays: this._agingDays,
      agingBucket: this._agingBucket, status: this._status, isOverdue: this._isOverdue,
      isDisputed: this._isDisputed, dunningLevel: this._dunningLevel,
      lastDunningDate: this._lastDunningDate, dunningCount: this._dunningCount,
      assignedCollector: this._assignedCollector, promiseDate: this._promiseDate,
      promiseAmount: this._promiseAmount, writtenOffAt: this._writtenOffAt,
      writeOffReason: this._writeOffReason, approvedBy: this._approvedBy,
      isBadDebt: this._isBadDebt, badDebtAmount: this._badDebtAmount,
      badDebtProvision: this._badDebtProvision, glBatchId: this._glBatchId,
      postedToGL: this._postedToGL, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
