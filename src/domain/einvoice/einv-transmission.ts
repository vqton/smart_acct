import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { EinvTransmissionId } from "./einv-ids.js";
import { EinvTransmissionStatus } from "./einv-enums.js";
import { EinvTransmissionSent, EinvTransmissionAcknowledged, EinvTransmissionFailed } from "./einv-events.js";

export interface EinvTransmissionState {
  id: string; invoiceId: string; providerId: string;
  transmissionId: string | null;
  status: string;
  requestData: string | null; responseData: string | null;
  statusCode: string | null; statusMessage: string | null;
  retryCount: number; maxRetries: number; nextRetryAt: Date | null;
  acknowledgedAt: Date | null; completedAt: Date | null;
  failedAt: Date | null; errorDetail: string | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvTransmission extends AggregateRoot<EinvTransmissionId> {
  private _id: EinvTransmissionId;
  private _invoiceId: string;
  private _providerId: string;
  private _transmissionId: string | null;
  private _status: EinvTransmissionStatus;
  private _requestData: string | null;
  private _responseData: string | null;
  private _statusCode: string | null;
  private _statusMessage: string | null;
  private _retryCount: number;
  private _maxRetries: number;
  private _nextRetryAt: Date | null;
  private _acknowledgedAt: Date | null;
  private _completedAt: Date | null;
  private _failedAt: Date | null;
  private _errorDetail: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvTransmissionId, invoiceId: string, providerId: string, maxRetries: number) {
    super();
    this._id = id; this._invoiceId = invoiceId; this._providerId = providerId;
    this._maxRetries = maxRetries;
    this._status = EinvTransmissionStatus.pending;
    this._transmissionId = null; this._requestData = null; this._responseData = null;
    this._statusCode = null; this._statusMessage = null;
    this._retryCount = 0; this._nextRetryAt = null;
    this._acknowledgedAt = null; this._completedAt = null;
    this._failedAt = null; this._errorDetail = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { invoiceId: string; providerId: string; maxRetries?: number }): EinvTransmission {
    return new EinvTransmission(EinvTransmissionId.new(), p.invoiceId, p.providerId, p.maxRetries ?? 3);
  }

  static load(s: EinvTransmissionState): EinvTransmission {
    const t = new EinvTransmission(new EinvTransmissionId(s.id), s.invoiceId, s.providerId, s.maxRetries);
    t._transmissionId = s.transmissionId; t._status = s.status as EinvTransmissionStatus;
    t._requestData = s.requestData; t._responseData = s.responseData;
    t._statusCode = s.statusCode; t._statusMessage = s.statusMessage;
    t._retryCount = s.retryCount; t._nextRetryAt = s.nextRetryAt;
    t._acknowledgedAt = s.acknowledgedAt; t._completedAt = s.completedAt;
    t._failedAt = s.failedAt; t._errorDetail = s.errorDetail;
    t._version = s.version; t._createdAt = s.createdAt; t._updatedAt = s.updatedAt;
    return t;
  }

  get id() { return this._id; }
  get status() { return this._status; }
  get retryCount() { return this._retryCount; }
  get maxRetries() { return this._maxRetries; }
  get transmissionId() { return this._transmissionId; }
  get nextRetryAt() { return this._nextRetryAt; }
  get version() { return this._version; }

  markSending(): void {
    if (this._status !== EinvTransmissionStatus.pending && this._status !== EinvTransmissionStatus.retrying) {
      throw new DomainError("BusinessRule", "Transmission not in pending/retrying status");
    }
    this._status = EinvTransmissionStatus.sending;
    this._updatedAt = new Date(); this._version++;
  }

  markSent(requestData: string): void {
    if (this._status !== EinvTransmissionStatus.sending) {
      throw new DomainError("BusinessRule", "Transmission not in sending status");
    }
    this._status = EinvTransmissionStatus.sent;
    this._requestData = requestData;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvTransmissionSent(this._id.value, new Date(), { invoiceId: this._invoiceId }));
  }

  markAcknowledged(transmissionId: string, responseData: string, statusCode: string, statusMessage: string): void {
    if (this._status !== EinvTransmissionStatus.sent) {
      throw new DomainError("BusinessRule", "Transmission not in sent status");
    }
    this._status = EinvTransmissionStatus.acknowledged;
    this._transmissionId = transmissionId;
    this._responseData = responseData;
    this._statusCode = statusCode;
    this._statusMessage = statusMessage;
    this._acknowledgedAt = new Date();
    this._completedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvTransmissionAcknowledged(this._id.value, new Date(), { invoiceId: this._invoiceId, transmissionId }));
  }

  markFailed(errorDetail: string): void {
    if (this._status !== EinvTransmissionStatus.sending && this._status !== EinvTransmissionStatus.sent) {
      throw new DomainError("BusinessRule", "Transmission not in sending/sent status");
    }
    this._retryCount++;
    this._errorDetail = errorDetail;
    if (this._retryCount >= this._maxRetries) {
      this._status = EinvTransmissionStatus.failed;
      this._failedAt = new Date();
    } else {
      this._status = EinvTransmissionStatus.retrying;
      this._nextRetryAt = new Date(Date.now() + Math.pow(2, this._retryCount) * 60000);
    }
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvTransmissionFailed(this._id.value, new Date(), { invoiceId: this._invoiceId, errorDetail, retryCount: this._retryCount }));
  }

  toState(): EinvTransmissionState {
    return { id: this._id.value, invoiceId: this._invoiceId, providerId: this._providerId,
      transmissionId: this._transmissionId, status: this._status,
      requestData: this._requestData, responseData: this._responseData,
      statusCode: this._statusCode, statusMessage: this._statusMessage,
      retryCount: this._retryCount, maxRetries: this._maxRetries,
      nextRetryAt: this._nextRetryAt, acknowledgedAt: this._acknowledgedAt,
      completedAt: this._completedAt, failedAt: this._failedAt,
      errorDetail: this._errorDetail, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}
