import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PaymentRequestId, PaymentBatchId, RecurringPaymentId, StandingInstructionId, PaymentScheduleId } from "./bank-ids.js";
import { TransactionMethod, PaymentPriority, ChargeBearer, PaymentBatchStatus, ApprovalStatus, RecurringFrequency, TransactionStatus } from "./bank-enums.js";
import { PaymentRequestCreated, PaymentRequestApproved, PaymentBatchReleased } from "./bank-events.js";

// ─── Payment Request ───────────────────────────────────────────────────────────

export interface PaymentRequestState {
  id: string; companyId: string; requestNumber: string;
  paymentDate: Date; amount: number; currencyCode: string;
  fromAccountId: string; toAccountId: string | null;
  beneficiaryName: string; beneficiaryAccount: string | null;
  beneficiaryBank: string | null; beneficiaryBankSwift: string | null;
  method: string; priority: string; chargeBearer: string;
  reference: string | null; description: string | null;
  approvalStatus: string; approvalLevel: number; requiredApprovals: number;
  requestedById: string; requestedAt: Date;
  approvedById: string | null; approvedAt: Date | null;
  rejectedById: string | null; rejectedAt: Date | null;
  rejectionReason: string | null; batchId: string | null;
  transactionId: string | null; postedToGL: boolean; glBatchId: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class PaymentRequest extends AggregateRoot<PaymentRequestId> {
  private _id: PaymentRequestId; private _companyId: string; private _requestNumber: string;
  private _paymentDate: Date; private _amount: number; private _currencyCode: string;
  private _fromAccountId: string; private _toAccountId: string | null;
  private _beneficiaryName: string; private _beneficiaryAccount: string | null;
  private _beneficiaryBank: string | null; private _beneficiaryBankSwift: string | null;
  private _method: TransactionMethod; private _priority: PaymentPriority;
  private _chargeBearer: ChargeBearer; private _reference: string | null;
  private _description: string | null; private _approvalStatus: ApprovalStatus;
  private _approvalLevel: number; private _requiredApprovals: number;
  private _requestedById: string; private _requestedAt: Date;
  private _approvedById: string | null; private _approvedAt: Date | null;
  private _rejectedById: string | null; private _rejectedAt: Date | null;
  private _rejectionReason: string | null; private _batchId: string | null;
  private _transactionId: string | null; private _postedToGL: boolean;
  private _glBatchId: string | null; private _version: number;
  private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: PaymentRequestId, companyId: string, requestNumber: string,
    paymentDate: Date, amount: number, currencyCode: string, fromAccountId: string,
    beneficiaryName: string, method: TransactionMethod, requestedById: string) {
    super(); this._id = id; this._companyId = companyId; this._requestNumber = requestNumber;
    this._paymentDate = paymentDate; this._amount = amount; this._currencyCode = currencyCode;
    this._fromAccountId = fromAccountId; this._beneficiaryName = beneficiaryName;
    this._method = method; this._requestedById = requestedById;
    this._toAccountId = null; this._beneficiaryAccount = null; this._beneficiaryBank = null;
    this._beneficiaryBankSwift = null;
    this._priority = PaymentPriority.Normal; this._chargeBearer = ChargeBearer.Sender;
    this._reference = null; this._description = null;
    this._approvalStatus = ApprovalStatus.Pending; this._approvalLevel = 0;
    this._requiredApprovals = 1; this._requestedAt = new Date();
    this._approvedById = null; this._approvedAt = null;
    this._rejectedById = null; this._rejectedAt = null; this._rejectionReason = null;
    this._batchId = null; this._transactionId = null;
    this._postedToGL = false; this._glBatchId = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    companyId: string; requestNumber: string; paymentDate: Date; amount: number;
    currencyCode?: string; fromAccountId: string; beneficiaryName: string;
    beneficiaryAccount?: string; beneficiaryBank?: string; beneficiaryBankSwift?: string;
    method?: TransactionMethod; priority?: PaymentPriority; chargeBearer?: ChargeBearer;
    reference?: string; description?: string; requestedById: string;
  }): PaymentRequest {
    const r = new PaymentRequest(PaymentRequestId.new(), p.companyId, p.requestNumber,
      p.paymentDate, p.amount, p.currencyCode ?? "VND", p.fromAccountId,
      p.beneficiaryName, p.method ?? TransactionMethod.Wire, p.requestedById);
    r._toAccountId = p.beneficiaryAccount ?? null;
    r._beneficiaryAccount = p.beneficiaryAccount ?? null;
    r._beneficiaryBank = p.beneficiaryBank ?? null;
    r._beneficiaryBankSwift = p.beneficiaryBankSwift ?? null;
    r._priority = p.priority ?? PaymentPriority.Normal;
    r._chargeBearer = p.chargeBearer ?? ChargeBearer.Sender;
    r._reference = p.reference ?? null; r._description = p.description ?? null;
    r.addEvent(new PaymentRequestCreated(r._id.value, new Date(), {
      requestNumber: r._requestNumber, amount: r._amount,
    }));
    return r;
  }

  static load(s: PaymentRequestState): PaymentRequest {
    const r = new PaymentRequest(new PaymentRequestId(s.id), s.companyId, s.requestNumber,
      s.paymentDate, s.amount, s.currencyCode, s.fromAccountId, s.beneficiaryName,
      s.method as TransactionMethod, s.requestedById);
    r._beneficiaryAccount = s.beneficiaryAccount; r._beneficiaryBank = s.beneficiaryBank;
    r._beneficiaryBankSwift = s.beneficiaryBankSwift;
    r._priority = s.priority as PaymentPriority; r._chargeBearer = s.chargeBearer as ChargeBearer;
    r._reference = s.reference; r._description = s.description;
    r._approvalStatus = s.approvalStatus as ApprovalStatus;
    r._approvalLevel = s.approvalLevel; r._requiredApprovals = s.requiredApprovals;
    r._requestedAt = s.requestedAt; r._approvedById = s.approvedById; r._approvedAt = s.approvedAt;
    r._rejectedById = s.rejectedById; r._rejectedAt = s.rejectedAt; r._rejectionReason = s.rejectionReason;
    r._batchId = s.batchId; r._transactionId = s.transactionId;
    r._postedToGL = s.postedToGL; r._glBatchId = s.glBatchId;
    r._version = s.version; r._createdAt = s.createdAt; r._updatedAt = s.updatedAt; r._deletedAt = s.deletedAt;
    return r;
  }

  get id(): PaymentRequestId { return this._id; }
  get requestNumber(): string { return this._requestNumber; }
  get amount(): number { return this._amount; }
  get approvalStatus(): ApprovalStatus { return this._approvalStatus; }
  get fromAccountId(): string { return this._fromAccountId; }
  get version(): number { return this._version; }

  approve(userId: string): void {
    if (this._approvalStatus !== ApprovalStatus.Pending) throw new DomainError("BusinessRule", "Only pending requests can be approved");
    this._approvalLevel++;
    if (this._approvalLevel >= this._requiredApprovals) {
      this._approvalStatus = ApprovalStatus.Approved;
      this._approvedById = userId; this._approvedAt = new Date();
      this.addEvent(new PaymentRequestApproved(this._id.value, new Date(), {
        requestNumber: this._requestNumber, userId,
      }));
    }
    this._updatedAt = new Date(); this._version++;
  }

  reject(userId: string, reason: string): void {
    if (this._approvalStatus !== ApprovalStatus.Pending) throw new DomainError("BusinessRule", "Only pending requests can be rejected");
    this._approvalStatus = ApprovalStatus.Rejected;
    this._rejectedById = userId; this._rejectedAt = new Date(); this._rejectionReason = reason;
    this._updatedAt = new Date(); this._version++;
  }

  assignBatch(batchId: string): void {
    this._batchId = batchId; this._updatedAt = new Date(); this._version++;
  }

  toState(): PaymentRequestState {
    return { id: this._id.value, companyId: this._companyId, requestNumber: this._requestNumber,
      paymentDate: this._paymentDate, amount: this._amount, currencyCode: this._currencyCode,
      fromAccountId: this._fromAccountId, toAccountId: this._toAccountId,
      beneficiaryName: this._beneficiaryName, beneficiaryAccount: this._beneficiaryAccount,
      beneficiaryBank: this._beneficiaryBank, beneficiaryBankSwift: this._beneficiaryBankSwift,
      method: this._method, priority: this._priority, chargeBearer: this._chargeBearer,
      reference: this._reference, description: this._description,
      approvalStatus: this._approvalStatus, approvalLevel: this._approvalLevel,
      requiredApprovals: this._requiredApprovals, requestedById: this._requestedById,
      requestedAt: this._requestedAt, approvedById: this._approvedById,
      approvedAt: this._approvedAt, rejectedById: this._rejectedById,
      rejectedAt: this._rejectedAt, rejectionReason: this._rejectionReason,
      batchId: this._batchId, transactionId: this._transactionId,
      postedToGL: this._postedToGL, glBatchId: this._glBatchId,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}

// ─── Payment Batch ──────────────────────────────────────────────────────────────

export interface PaymentBatchState {
  id: string; companyId: string; batchNumber: string;
  status: string; paymentCount: number; totalAmount: number;
  currencyCode: string; paymentDate: Date; valueDate: Date | null;
  approvedById: string | null; approvedAt: Date | null;
  releasedById: string | null; releasedAt: Date | null;
  completedAt: Date | null; failureCount: number;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class PaymentBatch extends AggregateRoot<PaymentBatchId> {
  private _id: PaymentBatchId; private _companyId: string; private _batchNumber: string;
  private _status: PaymentBatchStatus; private _paymentCount: number;
  private _totalAmount: number; private _currencyCode: string;
  private _paymentDate: Date; private _valueDate: Date | null;
  private _approvedById: string | null; private _approvedAt: Date | null;
  private _releasedById: string | null; private _releasedAt: Date | null;
  private _completedAt: Date | null; private _failureCount: number;
  private _paymentIds: string[] = [];
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: PaymentBatchId, companyId: string, batchNumber: string,
    paymentDate: Date, currencyCode: string) {
    super(); this._id = id; this._companyId = companyId; this._batchNumber = batchNumber;
    this._status = PaymentBatchStatus.Draft; this._paymentCount = 0; this._totalAmount = 0;
    this._currencyCode = currencyCode; this._paymentDate = paymentDate; this._valueDate = null;
    this._approvedById = null; this._approvedAt = null; this._releasedById = null;
    this._releasedAt = null; this._completedAt = null; this._failureCount = 0;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { companyId: string; batchNumber: string; paymentDate: Date; currencyCode?: string }): PaymentBatch {
    return new PaymentBatch(PaymentBatchId.new(), p.companyId, p.batchNumber, p.paymentDate, p.currencyCode ?? "VND");
  }

  static load(s: PaymentBatchState): PaymentBatch {
    const b = new PaymentBatch(new PaymentBatchId(s.id), s.companyId, s.batchNumber, s.paymentDate, s.currencyCode);
    b._status = s.status as PaymentBatchStatus; b._paymentCount = s.paymentCount;
    b._totalAmount = s.totalAmount; b._valueDate = s.valueDate;
    b._approvedById = s.approvedById; b._approvedAt = s.approvedAt;
    b._releasedById = s.releasedById; b._releasedAt = s.releasedAt;
    b._completedAt = s.completedAt; b._failureCount = s.failureCount;
    b._version = s.version; b._createdAt = s.createdAt; b._updatedAt = s.updatedAt; b._deletedAt = s.deletedAt;
    return b;
  }

  get id(): PaymentBatchId { return this._id; }
  get batchNumber(): string { return this._batchNumber; }
  get status(): PaymentBatchStatus { return this._status; }
  get paymentCount(): number { return this._paymentCount; }
  get totalAmount(): number { return this._totalAmount; }
  get version(): number { return this._version; }

  addPayment(paymentId: string, amount: number): void {
    if (this._status !== PaymentBatchStatus.Draft && this._status !== PaymentBatchStatus.Validated) {
      throw new DomainError("BusinessRule", "Cannot add payments to non-draft batch");
    }
    this._paymentIds.push(paymentId); this._paymentCount++; this._totalAmount += amount;
    this._updatedAt = new Date(); this._version++;
  }

  validate(): void {
    if (this._status !== PaymentBatchStatus.Draft) throw new DomainError("BusinessRule", "Only draft batches can be validated");
    if (this._paymentCount === 0) throw new DomainError("BusinessRule", "Cannot validate empty batch");
    this._status = PaymentBatchStatus.Validated; this._updatedAt = new Date(); this._version++;
  }

  approve(userId: string): void {
    if (this._status !== PaymentBatchStatus.Validated) throw new DomainError("BusinessRule", "Only validated batches can be approved");
    this._status = PaymentBatchStatus.Approved;
    this._approvedById = userId; this._approvedAt = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  release(userId: string): void {
    if (this._status !== PaymentBatchStatus.Approved) throw new DomainError("BusinessRule", "Only approved batches can be released");
    this._status = PaymentBatchStatus.Released;
    this._releasedById = userId; this._releasedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new PaymentBatchReleased(this._id.value, new Date(), {
      batchNumber: this._batchNumber, paymentCount: this._paymentCount, totalAmount: this._totalAmount,
    }));
  }

  complete(): void {
    if (this._status !== PaymentBatchStatus.Released && this._status !== PaymentBatchStatus.Processing) {
      throw new DomainError("BusinessRule", "Only released/processing batches can complete");
    }
    this._status = PaymentBatchStatus.Completed; this._completedAt = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  markFailed(): void {
    this._failureCount++; this._updatedAt = new Date(); this._version++;
  }

  cancel(): void {
    if (this._status === PaymentBatchStatus.Completed || this._status === PaymentBatchStatus.Released) {
      throw new DomainError("BusinessRule", "Cannot cancel completed/released batch");
    }
    this._status = PaymentBatchStatus.Cancelled; this._updatedAt = new Date(); this._version++;
  }

  toState(): PaymentBatchState {
    return { id: this._id.value, companyId: this._companyId, batchNumber: this._batchNumber,
      status: this._status, paymentCount: this._paymentCount, totalAmount: this._totalAmount,
      currencyCode: this._currencyCode, paymentDate: this._paymentDate, valueDate: this._valueDate,
      approvedById: this._approvedById, approvedAt: this._approvedAt,
      releasedById: this._releasedById, releasedAt: this._releasedAt,
      completedAt: this._completedAt, failureCount: this._failureCount,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}

// ─── Recurring Payment ──────────────────────────────────────────────────────────

export interface RecurringPaymentState {
  id: string; companyId: string; name: string;
  fromAccountId: string; toAccountId: string | null;
  beneficiaryName: string; beneficiaryAccount: string | null;
  beneficiaryBank: string | null; amount: number; currencyCode: string;
  frequency: string; interval: number; startDate: Date; endDate: Date | null;
  nextExecutionDate: Date; lastExecutionDate: Date | null;
  executionCount: number; maxExecutions: number | null;
  method: string; reference: string | null; description: string | null;
  isActive: boolean; version: number;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class RecurringPayment extends AggregateRoot<RecurringPaymentId> {
  private _id: RecurringPaymentId; private _companyId: string; private _name: string;
  private _fromAccountId: string; private _toAccountId: string | null;
  private _beneficiaryName: string; private _beneficiaryAccount: string | null;
  private _beneficiaryBank: string | null; private _amount: number;
  private _currencyCode: string; private _frequency: RecurringFrequency;
  private _interval: number; private _startDate: Date; private _endDate: Date | null;
  private _nextExecutionDate: Date; private _lastExecutionDate: Date | null;
  private _executionCount: number; private _maxExecutions: number | null;
  private _method: TransactionMethod; private _reference: string | null;
  private _description: string | null; private _isActive: boolean;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: RecurringPaymentId, companyId: string, name: string,
    fromAccountId: string, beneficiaryName: string, amount: number,
    currencyCode: string, frequency: RecurringFrequency, startDate: Date) {
    super(); this._id = id; this._companyId = companyId; this._name = name;
    this._fromAccountId = fromAccountId; this._beneficiaryName = beneficiaryName;
    this._amount = amount; this._currencyCode = currencyCode;
    this._frequency = frequency; this._interval = 1; this._startDate = startDate;
    this._endDate = null; this._nextExecutionDate = startDate;
    this._lastExecutionDate = null; this._executionCount = 0; this._maxExecutions = null;
    this._toAccountId = null; this._beneficiaryAccount = null; this._beneficiaryBank = null;
    this._method = TransactionMethod.Wire; this._reference = null; this._description = null;
    this._isActive = true;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    companyId: string; name: string; fromAccountId: string; beneficiaryName: string;
    beneficiaryAccount?: string; beneficiaryBank?: string; amount: number;
    currencyCode?: string; frequency: RecurringFrequency; startDate: Date;
    endDate?: Date | null; interval?: number; maxExecutions?: number;
    method?: TransactionMethod; reference?: string; description?: string;
  }): RecurringPayment {
    const r = new RecurringPayment(RecurringPaymentId.new(), p.companyId, p.name,
      p.fromAccountId, p.beneficiaryName, p.amount, p.currencyCode ?? "VND",
      p.frequency, p.startDate);
    r._beneficiaryAccount = p.beneficiaryAccount ?? null;
    r._beneficiaryBank = p.beneficiaryBank ?? null;
    r._endDate = p.endDate ?? null; r._interval = p.interval ?? 1;
    r._maxExecutions = p.maxExecutions ?? null;
    r._method = p.method ?? TransactionMethod.Wire;
    r._reference = p.reference ?? null; r._description = p.description ?? null;
    return r;
  }

  static load(s: RecurringPaymentState): RecurringPayment {
    const r = new RecurringPayment(new RecurringPaymentId(s.id), s.companyId, s.name,
      s.fromAccountId, s.beneficiaryName, s.amount, s.currencyCode,
      s.frequency as RecurringFrequency, s.startDate);
    r._beneficiaryAccount = s.beneficiaryAccount; r._beneficiaryBank = s.beneficiaryBank;
    r._toAccountId = s.toAccountId; r._endDate = s.endDate; r._interval = s.interval;
    r._nextExecutionDate = s.nextExecutionDate; r._lastExecutionDate = s.lastExecutionDate;
    r._executionCount = s.executionCount; r._maxExecutions = s.maxExecutions;
    r._method = s.method as TransactionMethod; r._reference = s.reference;
    r._description = s.description; r._isActive = s.isActive;
    r._version = s.version; r._createdAt = s.createdAt; r._updatedAt = s.updatedAt; r._deletedAt = s.deletedAt;
    return r;
  }

  get id(): RecurringPaymentId { return this._id; }
  get isActive(): boolean { return this._isActive; }
  get nextExecutionDate(): Date { return this._nextExecutionDate; }

  suspend(): void { this._isActive = false; this._updatedAt = new Date(); this._version++; }
  activate(): void { this._isActive = true; this._updatedAt = new Date(); this._version++; }

  recordExecution(): void {
    this._executionCount++; this._lastExecutionDate = new Date();
    this._calculateNextExecution();
    this._updatedAt = new Date(); this._version++;
  }

  private _calculateNextExecution(): void {
    const next = new Date(this._nextExecutionDate);
    switch (this._frequency) {
      case RecurringFrequency.Daily: next.setDate(next.getDate() + this._interval); break;
      case RecurringFrequency.Weekly: next.setDate(next.getDate() + 7 * this._interval); break;
      case RecurringFrequency.Monthly: next.setMonth(next.getMonth() + this._interval); break;
      case RecurringFrequency.Quarterly: next.setMonth(next.getMonth() + 3 * this._interval); break;
      case RecurringFrequency.Annual: next.setFullYear(next.getFullYear() + this._interval); break;
      default: next.setMonth(next.getMonth() + 1); break;
    }
    if (this._endDate && next > this._endDate) { this._isActive = false; }
    if (this._maxExecutions && this._executionCount >= this._maxExecutions) { this._isActive = false; }
    this._nextExecutionDate = next;
  }

  toState(): RecurringPaymentState {
    return { id: this._id.value, companyId: this._companyId, name: this._name,
      fromAccountId: this._fromAccountId, toAccountId: this._toAccountId,
      beneficiaryName: this._beneficiaryName, beneficiaryAccount: this._beneficiaryAccount,
      beneficiaryBank: this._beneficiaryBank, amount: this._amount, currencyCode: this._currencyCode,
      frequency: this._frequency, interval: this._interval, startDate: this._startDate,
      endDate: this._endDate, nextExecutionDate: this._nextExecutionDate,
      lastExecutionDate: this._lastExecutionDate, executionCount: this._executionCount,
      maxExecutions: this._maxExecutions, method: this._method, reference: this._reference,
      description: this._description, isActive: this._isActive, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}

// ─── Standing Instruction ───────────────────────────────────────────────────────

export interface StandingInstructionState {
  id: string; companyId: string; instructionNumber: string; name: string;
  fromAccountId: string; toAccountId: string; amount: number;
  currencyCode: string; frequency: string; startDate: Date; endDate: Date | null;
  isActive: boolean; lastExecutedAt: Date | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}
