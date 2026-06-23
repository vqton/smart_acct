import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { BankTransactionId } from "./bank-ids.js";
import { TransactionStatus, TransactionNature, TransactionMethod, PaymentPriority, ChargeBearer, SettlementMethod } from "./bank-enums.js";
import {
  TransactionInitiated, TransactionAuthorized, TransactionExecuted,
  TransactionCompleted, TransactionFailed, TransactionReversed,
} from "./bank-events.js";

export interface BankTransactionState {
  id: string; companyId: string; transactionNumber: string;
  nature: string; method: string; status: string;
  fromAccountId: string; fromAccountNumber: string | null;
  toAccountId: string | null; toAccountNumber: string | null;
  toBankId: string | null; toBankName: string | null;
  toBankSwift: string | null; toBankRouting: string | null;
  beneficiaryName: string | null; beneficiaryAccount: string | null;
  beneficiaryAddress: string | null; beneficiaryBank: string | null;
  intermediaryBankId: string | null; intermediaryBankSwift: string | null;
  amount: number; currencyCode: string; exchangeRate: number;
  vndAmount: number; chargeBearer: string;
  paymentPriority: string; settlementMethod: string | null;
  paymentChannel: string | null; reference: string | null;
  description: string | null; fees: number; feeCurrencyCode: string;
  valueDate: Date | null; transactionDate: Date;
  swiftMessage: string | null; endToEndId: string | null;
  transactionId: string | null; clearingSystemRef: string | null;
  approvalLevel: number; requiredApprovals: number;
  approvedById: string | null; approvedAt: Date | null;
  executedById: string | null; executedAt: Date | null;
  completedAt: Date | null; failureReason: string | null;
  reversalReason: string | null; reversedAt: Date | null;
  postedToGL: boolean; glBatchId: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class BankTransaction extends AggregateRoot<BankTransactionId> {
  private _id: BankTransactionId; private _companyId: string;
  private _transactionNumber: string; private _nature: TransactionNature;
  private _method: TransactionMethod; private _status: TransactionStatus;
  private _fromAccountId: string; private _fromAccountNumber: string | null;
  private _toAccountId: string | null; private _toAccountNumber: string | null;
  private _toBankId: string | null; private _toBankName: string | null;
  private _toBankSwift: string | null; private _toBankRouting: string | null;
  private _beneficiaryName: string | null; private _beneficiaryAccount: string | null;
  private _beneficiaryAddress: string | null; private _beneficiaryBank: string | null;
  private _intermediaryBankId: string | null; private _intermediaryBankSwift: string | null;
  private _amount: number; private _currencyCode: string;
  private _exchangeRate: number; private _vndAmount: number;
  private _chargeBearer: ChargeBearer; private _paymentPriority: PaymentPriority;
  private _settlementMethod: SettlementMethod | null;
  private _paymentChannel: string | null;
  private _reference: string | null; private _description: string | null;
  private _fees: number; private _feeCurrencyCode: string;
  private _valueDate: Date | null; private _transactionDate: Date;
  private _swiftMessage: string | null; private _endToEndId: string | null;
  private _transactionId: string | null; private _clearingSystemRef: string | null;
  private _approvalLevel: number; private _requiredApprovals: number;
  private _approvedById: string | null; private _approvedAt: Date | null;
  private _executedById: string | null; private _executedAt: Date | null;
  private _completedAt: Date | null; private _failureReason: string | null;
  private _reversalReason: string | null; private _reversedAt: Date | null;
  private _postedToGL: boolean; private _glBatchId: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: BankTransactionId, companyId: string, transactionNumber: string,
    nature: TransactionNature, method: TransactionMethod, fromAccountId: string,
    amount: number, currencyCode: string, transactionDate: Date) {
    super();
    if (amount <= 0) throw new DomainError("BusinessRule", "Transaction amount must be positive");
    this._id = id; this._companyId = companyId; this._transactionNumber = transactionNumber;
    this._nature = nature; this._method = method; this._fromAccountId = fromAccountId;
    this._amount = amount; this._currencyCode = currencyCode; this._transactionDate = transactionDate;
    this._status = TransactionStatus.Draft; this._fromAccountNumber = null;
    this._toAccountId = null; this._toAccountNumber = null;
    this._toBankId = null; this._toBankName = null;
    this._toBankSwift = null; this._toBankRouting = null;
    this._beneficiaryName = null; this._beneficiaryAccount = null;
    this._beneficiaryAddress = null; this._beneficiaryBank = null;
    this._intermediaryBankId = null; this._intermediaryBankSwift = null;
    this._exchangeRate = 1; this._vndAmount = currencyCode === "VND" ? amount : 0;
    this._chargeBearer = ChargeBearer.Sender; this._paymentPriority = PaymentPriority.Normal;
    this._settlementMethod = null; this._paymentChannel = null;
    this._reference = null; this._description = null;
    this._fees = 0; this._feeCurrencyCode = "VND";
    this._valueDate = null; this._swiftMessage = null;
    this._endToEndId = null; this._transactionId = null; this._clearingSystemRef = null;
    this._approvalLevel = 0; this._requiredApprovals = 0;
    this._approvedById = null; this._approvedAt = null;
    this._executedById = null; this._executedAt = null;
    this._completedAt = null; this._failureReason = null;
    this._reversalReason = null; this._reversedAt = null;
    this._postedToGL = false; this._glBatchId = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    companyId: string; transactionNumber: string; nature: TransactionNature;
    method: TransactionMethod; fromAccountId: string; amount: number;
    currencyCode?: string; transactionDate: Date;
    toAccountId?: string | null; toAccountNumber?: string | null;
    toBankId?: string | null; toBankName?: string | null;
    toBankSwift?: string | null; beneficiaryName?: string | null;
    beneficiaryAccount?: string | null; beneficiaryBank?: string | null;
    reference?: string | null; description?: string | null;
    paymentPriority?: PaymentPriority; chargeBearer?: ChargeBearer;
    exchangeRate?: number; fees?: number;
  }): BankTransaction {
    const t = new BankTransaction(BankTransactionId.new(), p.companyId, p.transactionNumber,
      p.nature, p.method, p.fromAccountId, p.amount, p.currencyCode ?? "VND", p.transactionDate);
    t._toAccountId = p.toAccountId ?? null; t._toAccountNumber = p.toAccountNumber ?? null;
    t._toBankId = p.toBankId ?? null; t._toBankName = p.toBankName ?? null;
    t._toBankSwift = p.toBankSwift ?? null;
    t._beneficiaryName = p.beneficiaryName ?? null;
    t._beneficiaryAccount = p.beneficiaryAccount ?? null;
    t._beneficiaryBank = p.beneficiaryBank ?? null;
    t._reference = p.reference ?? null; t._description = p.description ?? null;
    t._paymentPriority = p.paymentPriority ?? PaymentPriority.Normal;
    t._chargeBearer = p.chargeBearer ?? ChargeBearer.Sender;
    if (p.exchangeRate && p.exchangeRate !== 1) {
      if (p.currencyCode === "VND") throw new DomainError("BusinessRule", "Exchange rate not applicable for VND");
      t._exchangeRate = p.exchangeRate; t._vndAmount = Math.round(p.amount * p.exchangeRate);
    }
    t._fees = p.fees ?? 0;
    t.addEvent(new TransactionInitiated(t._id.value, new Date(), {
      transactionNumber: t._transactionNumber, amount: t._amount, currency: t._currencyCode,
    }));
    return t;
  }

  static load(s: BankTransactionState): BankTransaction {
    const t = new BankTransaction(new BankTransactionId(s.id), s.companyId, s.transactionNumber,
      s.nature as TransactionNature, s.method as TransactionMethod, s.fromAccountId,
      s.amount, s.currencyCode, s.transactionDate);
    t._fromAccountNumber = s.fromAccountNumber; t._toAccountId = s.toAccountId;
    t._toAccountNumber = s.toAccountNumber; t._toBankId = s.toBankId;
    t._toBankName = s.toBankName; t._toBankSwift = s.toBankSwift;
    t._toBankRouting = s.toBankRouting; t._beneficiaryName = s.beneficiaryName;
    t._beneficiaryAccount = s.beneficiaryAccount; t._beneficiaryAddress = s.beneficiaryAddress;
    t._beneficiaryBank = s.beneficiaryBank; t._intermediaryBankId = s.intermediaryBankId;
    t._intermediaryBankSwift = s.intermediaryBankSwift;
    t._exchangeRate = s.exchangeRate; t._vndAmount = s.vndAmount;
    t._chargeBearer = s.chargeBearer as ChargeBearer;
    t._paymentPriority = s.paymentPriority as PaymentPriority;
    t._settlementMethod = s.settlementMethod ? s.settlementMethod as SettlementMethod : null;
    t._paymentChannel = s.paymentChannel;
    t._reference = s.reference; t._description = s.description;
    t._fees = s.fees; t._feeCurrencyCode = s.feeCurrencyCode;
    t._valueDate = s.valueDate; t._swiftMessage = s.swiftMessage;
    t._endToEndId = s.endToEndId; t._transactionId = s.transactionId;
    t._clearingSystemRef = s.clearingSystemRef;
    t._approvalLevel = s.approvalLevel; t._requiredApprovals = s.requiredApprovals;
    t._status = s.status as TransactionStatus;
    t._approvedById = s.approvedById; t._approvedAt = s.approvedAt;
    t._executedById = s.executedById; t._executedAt = s.executedAt;
    t._completedAt = s.completedAt; t._failureReason = s.failureReason;
    t._reversalReason = s.reversalReason; t._reversedAt = s.reversedAt;
    t._postedToGL = s.postedToGL; t._glBatchId = s.glBatchId;
    t._version = s.version; t._createdAt = s.createdAt; t._updatedAt = s.updatedAt; t._deletedAt = s.deletedAt;
    return t;
  }

  get id(): BankTransactionId { return this._id; }
  get transactionNumber(): string { return this._transactionNumber; }
  get nature(): TransactionNature { return this._nature; }
  get method(): TransactionMethod { return this._method; }
  get status(): TransactionStatus { return this._status; }
  get fromAccountId(): string { return this._fromAccountId; }
  get toAccountId(): string | null { return this._toAccountId; }
  get amount(): number { return this._amount; }
  get currencyCode(): string { return this._currencyCode; }
  get exchangeRate(): number { return this._exchangeRate; }
  get vndAmount(): number { return this._vndAmount; }
  get reference(): string | null { return this._reference; }
  get fees(): number { return this._fees; }
  get failureReason(): string | null { return this._failureReason; }
  get version(): number { return this._version; }

  authorize(userId: string): void {
    if (this._status !== TransactionStatus.Draft && this._status !== TransactionStatus.Pending) {
      throw new DomainError("BusinessRule", "Only draft/pending transactions can be authorized");
    }
    this._status = TransactionStatus.Authorized; this._approvalLevel++;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new TransactionAuthorized(this._id.value, new Date(), { userId }));
  }

  approve(userId: string): void {
    if (this._status !== TransactionStatus.Authorized) {
      throw new DomainError("BusinessRule", "Only authorized transactions can be approved");
    }
    this._approvalLevel++;
    if (this._approvalLevel >= this._requiredApprovals) {
      this._approvedById = userId; this._approvedAt = new Date();
      this._status = TransactionStatus.Approved;
    }
    this._updatedAt = new Date(); this._version++;
  }

  execute(userId: string): void {
    if (this._status !== TransactionStatus.Approved) {
      throw new DomainError("BusinessRule", "Only approved transactions can be executed");
    }
    this._status = TransactionStatus.Executed; this._executedById = userId;
    this._executedAt = new Date(); this._valueDate = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new TransactionExecuted(this._id.value, new Date(), { userId }));
  }

  complete(): void {
    if (this._status !== TransactionStatus.Executed && this._status !== TransactionStatus.Sent) {
      throw new DomainError("BusinessRule", "Transaction must be executed/sent before completing");
    }
    this._status = TransactionStatus.Completed; this._completedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new TransactionCompleted(this._id.value, new Date(), {
      transactionNumber: this._transactionNumber, amount: this._amount,
    }));
  }

  fail(reason: string): void {
    if (this._status === TransactionStatus.Completed || this._status === TransactionStatus.Reversed) {
      throw new DomainError("BusinessRule", "Cannot fail completed/reversed transaction");
    }
    this._status = TransactionStatus.Failed; this._failureReason = reason;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new TransactionFailed(this._id.value, new Date(), { reason }));
  }

  cancel(): void {
    if (this._status === TransactionStatus.Completed || this._status === TransactionStatus.Sent) {
      throw new DomainError("BusinessRule", "Cannot cancel completed or sent transaction");
    }
    this._status = TransactionStatus.Cancelled; this._updatedAt = new Date(); this._version++;
  }

  reverse(reason: string): void {
    if (this._status !== TransactionStatus.Completed) {
      throw new DomainError("BusinessRule", "Only completed transactions can be reversed");
    }
    this._status = TransactionStatus.Reversed; this._reversalReason = reason;
    this._reversedAt = new Date(); this._updatedAt = new Date(); this._version++;
    this.addEvent(new TransactionReversed(this._id.value, new Date(), { reason }));
  }

  markGLPosted(batchId: string): void {
    this._postedToGL = true; this._glBatchId = batchId;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): BankTransactionState {
    return {
      id: this._id.value, companyId: this._companyId, transactionNumber: this._transactionNumber,
      nature: this._nature, method: this._method, status: this._status,
      fromAccountId: this._fromAccountId, fromAccountNumber: this._fromAccountNumber,
      toAccountId: this._toAccountId, toAccountNumber: this._toAccountNumber,
      toBankId: this._toBankId, toBankName: this._toBankName,
      toBankSwift: this._toBankSwift, toBankRouting: this._toBankRouting,
      beneficiaryName: this._beneficiaryName, beneficiaryAccount: this._beneficiaryAccount,
      beneficiaryAddress: this._beneficiaryAddress, beneficiaryBank: this._beneficiaryBank,
      intermediaryBankId: this._intermediaryBankId, intermediaryBankSwift: this._intermediaryBankSwift,
      amount: this._amount, currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      vndAmount: this._vndAmount, chargeBearer: this._chargeBearer,
      paymentPriority: this._paymentPriority, settlementMethod: this._settlementMethod,
      paymentChannel: this._paymentChannel, reference: this._reference,
      description: this._description, fees: this._fees, feeCurrencyCode: this._feeCurrencyCode,
      valueDate: this._valueDate, transactionDate: this._transactionDate,
      swiftMessage: this._swiftMessage, endToEndId: this._endToEndId,
      transactionId: this._transactionId, clearingSystemRef: this._clearingSystemRef,
      approvalLevel: this._approvalLevel, requiredApprovals: this._requiredApprovals,
      approvedById: this._approvedById, approvedAt: this._approvedAt,
      executedById: this._executedById, executedAt: this._executedAt,
      completedAt: this._completedAt, failureReason: this._failureReason,
      reversalReason: this._reversalReason, reversedAt: this._reversedAt,
      postedToGL: this._postedToGL, glBatchId: this._glBatchId,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
