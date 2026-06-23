import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { DomainEvent } from "../../shared/domain-event.js";
import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class TaxRegistrationId extends Identifier {
  static new(): TaxRegistrationId { return new TaxRegistrationId(IdGenerator.uuid()); }
}

export class TaxpayerId extends Identifier {
  static new(): TaxpayerId { return new TaxpayerId(IdGenerator.uuid()); }
}

export enum TaxpayerType {
  Enterprise = "enterprise",
  Household = "household",
  Individual = "individual",
  Cooperative = "cooperative",
  ForeignEntity = "foreign_entity",
  Government = "government",
  NonProfit = "non_profit",
}

export enum TaxRegistrationStatus {
  Pending = "pending",
  Registered = "registered",
  Suspended = "suspended",
  Revoked = "revoked",
  Cancelled = "cancelled",
}

export enum TaxComplianceStatus {
  Compliant = "compliant",
  NonCompliant = "non_compliant",
  UnderReview = "under_review",
  Penalized = "penalized",
}

export class TaxpayerRegistered implements DomainEvent {
  readonly eventName = "TaxpayerRegistered";
  constructor(readonly aggregateId: string, readonly occurredAt: Date, readonly payload: Record<string, unknown>) {}
}

export interface TaxRegistrationState {
  id: string;
  taxpayerId: string;
  taxTypeId: string;
  taxAuthorityId: string;
  registrationNumber: string;
  status: TaxRegistrationStatus;
  registeredAt: Date | null;
  suspendedAt: Date | null;
  revokedAt: Date | null;
  reason: string | null;
  certificateNumber: string | null;
  certificateIssuedAt: Date | null;
  certificateExpiresAt: Date | null;
  metadata: Record<string, unknown> | null;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class TaxRegistration extends AggregateRoot<TaxRegistrationId> {
  private _id: TaxRegistrationId;
  private _taxpayerId!: string;
  private _taxTypeId!: string;
  private _taxAuthorityId!: string;
  private _registrationNumber!: string;
  private _status: TaxRegistrationStatus;
  private _registeredAt: Date | null;
  private _suspendedAt: Date | null;
  private _revokedAt: Date | null;
  private _reason: string | null;
  private _certificateNumber: string | null;
  private _certificateIssuedAt: Date | null;
  private _certificateExpiresAt: Date | null;
  private _metadata: Record<string, unknown> | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _version: number;

  private constructor(id: TaxRegistrationId) {
    super();
    this._id = id;
    this._status = TaxRegistrationStatus.Pending;
    this._registeredAt = null;
    this._suspendedAt = null;
    this._revokedAt = null;
    this._reason = null;
    this._certificateNumber = null;
    this._certificateIssuedAt = null;
    this._certificateExpiresAt = null;
    this._metadata = null;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._version = 1;
  }

  static create(params: { taxpayerId: string; taxTypeId: string; taxAuthorityId: string; registrationNumber: string }): TaxRegistration {
    const reg = new TaxRegistration(TaxRegistrationId.new());
    reg._taxpayerId = params.taxpayerId;
    reg._taxTypeId = params.taxTypeId;
    reg._taxAuthorityId = params.taxAuthorityId;
    reg._registrationNumber = params.registrationNumber;
    return reg;
  }

  static load(s: TaxRegistrationState): TaxRegistration {
    const reg = new TaxRegistration(new TaxRegistrationId(s.id));
    reg._taxpayerId = s.taxpayerId; reg._taxTypeId = s.taxTypeId;
    reg._taxAuthorityId = s.taxAuthorityId; reg._registrationNumber = s.registrationNumber;
    reg._status = s.status; reg._registeredAt = s.registeredAt;
    reg._suspendedAt = s.suspendedAt; reg._revokedAt = s.revokedAt;
    reg._reason = s.reason; reg._certificateNumber = s.certificateNumber;
    reg._certificateIssuedAt = s.certificateIssuedAt;
    reg._certificateExpiresAt = s.certificateExpiresAt;
    reg._metadata = s.metadata;
    reg._createdAt = s.createdAt; reg._updatedAt = s.updatedAt; reg._version = s.version;
    return reg;
  }

  get id() { return this._id; }
  get taxpayerId() { return this._taxpayerId; }
  get taxTypeId() { return this._taxTypeId; }
  get status() { return this._status; }
  get registrationNumber() { return this._registrationNumber; }

  register(certNumber: string): void {
    if (this._status !== TaxRegistrationStatus.Pending) throw new DomainError("BusinessRule", "Only pending registrations can be registered");
    this._status = TaxRegistrationStatus.Registered;
    this._certificateNumber = certNumber;
    this._certificateIssuedAt = new Date();
    this._registeredAt = new Date();
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new TaxpayerRegistered(this._id.value, new Date(), { taxpayerId: this._taxpayerId, taxTypeId: this._taxTypeId }));
  }

  suspend(reason: string): void {
    if (this._status !== TaxRegistrationStatus.Registered) throw new DomainError("BusinessRule", "Only active registrations can be suspended");
    this._status = TaxRegistrationStatus.Suspended;
    this._suspendedAt = new Date();
    this._reason = reason;
    this._updatedAt = new Date();
    this._version++;
  }

  revoke(reason: string): void {
    if (this._status === TaxRegistrationStatus.Revoked || this._status === TaxRegistrationStatus.Cancelled) throw new DomainError("BusinessRule", "Already revoked or cancelled");
    this._status = TaxRegistrationStatus.Revoked;
    this._revokedAt = new Date();
    this._reason = reason;
    this._updatedAt = new Date();
    this._version++;
  }

  isActive(): boolean {
    return this._status === TaxRegistrationStatus.Registered;
  }

  toState(): TaxRegistrationState {
    return {
      id: this._id.value, taxpayerId: this._taxpayerId, taxTypeId: this._taxTypeId,
      taxAuthorityId: this._taxAuthorityId, registrationNumber: this._registrationNumber,
      status: this._status, registeredAt: this._registeredAt,
      suspendedAt: this._suspendedAt, revokedAt: this._revokedAt, reason: this._reason,
      certificateNumber: this._certificateNumber,
      certificateIssuedAt: this._certificateIssuedAt,
      certificateExpiresAt: this._certificateExpiresAt,
      metadata: this._metadata, createdAt: this._createdAt, updatedAt: this._updatedAt,
      version: this._version,
    };
  }
}
