import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import {
  VendorId, VendorGroupId, VendorContactId, VendorBankAccountId, VendorTaxInfoId,
  VendorCertificateId, VendorEvaluationId, VendorPerformanceId, VendorScorecardId,
  VendorQualificationId,
} from "./purchasing-ids.js";
import {
  VendorStatus, VendorType, VendorCategory, VendorClassification,
  VendorQualificationStatus, EvaluationScore,
} from "./purchasing-enums.js";
import { Address, ContactInfo, BankInfo, CertificateInfo } from "./purchasing-value-objects.js";
import { VendorCreated, VendorUpdated, VendorBlocked, VendorUnblocked, VendorQualified, VendorEvaluationCompleted } from "./purchasing-events.js";

// ─── Vendor State ───────────────────────────────────────────────────────────────

export interface VendorState {
  id: string; groupId: string | null; code: string; name: string; nameEn: string | null;
  taxCode: string | null; vendorType: string; category: string; status: string;
  classification: string; address: string | null; ward: string | null; district: string | null;
  province: string | null; country: string; postalCode: string | null;
  phone: string | null; email: string | null; website: string | null;
  paymentTermCode: string | null; currencyCode: string;
  isActive: boolean; version: number;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

// ─── Vendor Aggregate ────────────────────────────────────────────────────────────

export class Vendor extends AggregateRoot<VendorId> {
  private _id: VendorId; private _groupId: string | null; private _code: string; private _name: string;
  private _nameEn: string | null; private _taxCode: string | null;
  private _vendorType: VendorType; private _category: string; private _status: VendorStatus;
  private _classification: string; private _address: string | null; private _ward: string | null;
  private _district: string | null; private _province: string | null; private _country: string;
  private _postalCode: string | null; private _phone: string | null; private _email: string | null;
  private _website: string | null; private _paymentTermCode: string | null;
  private _currencyCode: string; private _isActive: boolean;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;
  private _qualifications: VendorQualification[] = [];

  private constructor(id: VendorId, code: string, name: string, country: string) {
    super(); this._id = id; this._code = code; this._name = name; this._country = country;
    this._nameEn = null; this._taxCode = null; this._vendorType = VendorType.company;
    this._category = ""; this._status = VendorStatus.active; this._classification = "local";
    this._address = null; this._ward = null; this._district = null; this._province = null;
    this._postalCode = null; this._phone = null; this._email = null; this._website = null;
    this._paymentTermCode = null; this._currencyCode = "VND"; this._groupId = null;
    this._isActive = true; this._version = 1;
    this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    code: string; name: string; country: string; nameEn?: string; taxCode?: string;
    vendorType?: VendorType; category?: string; classification?: string;
    phone?: string; email?: string; website?: string; address?: string;
    ward?: string; district?: string; province?: string; postalCode?: string;
    paymentTermCode?: string; currencyCode?: string; groupId?: string;
  }): Vendor {
    const v = new Vendor(VendorId.new(), p.code, p.name, p.country);
    v._nameEn = p.nameEn ?? null; v._taxCode = p.taxCode ?? null;
    v._vendorType = p.vendorType ?? VendorType.company; v._category = p.category ?? "";
    v._classification = p.classification ?? "local"; v._address = p.address ?? null;
    v._ward = p.ward ?? null; v._district = p.district ?? null; v._province = p.province ?? null;
    v._postalCode = p.postalCode ?? null; v._phone = p.phone ?? null; v._email = p.email ?? null;
    v._website = p.website ?? null; v._paymentTermCode = p.paymentTermCode ?? null;
    v._currencyCode = p.currencyCode ?? "VND"; v._groupId = p.groupId ?? null;
    v.addEvent(new VendorCreated(v._id.value, new Date(), { code: v._code, name: v._name }));
    return v;
  }

  static load(s: VendorState): Vendor {
    const v = new Vendor(new VendorId(s.id), s.code, s.name, s.country);
    v._groupId = s.groupId; v._nameEn = s.nameEn; v._taxCode = s.taxCode;
    v._vendorType = s.vendorType as VendorType; v._category = s.category;
    v._status = s.status as VendorStatus; v._classification = s.classification;
    v._address = s.address; v._ward = s.ward; v._district = s.district;
    v._province = s.province; v._postalCode = s.postalCode; v._phone = s.phone;
    v._email = s.email; v._website = s.website; v._paymentTermCode = s.paymentTermCode;
    v._currencyCode = s.currencyCode; v._isActive = s.isActive;
    v._version = s.version; v._createdAt = s.createdAt; v._updatedAt = s.updatedAt;
    v._deletedAt = s.deletedAt;
    return v;
  }

  get id(): VendorId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get email(): string | null { return this._email; }
  get status(): VendorStatus { return this._status; }
  get isActive(): boolean { return this._isActive; }
  get version(): number { return this._version; }

  update(p: Partial<{
    name: string; nameEn: string | null; taxCode: string | null; vendorType: VendorType;
    category: string; classification: string; phone: string | null; email: string | null;
    website: string | null; address: string | null; ward: string | null;
    district: string | null; province: string | null; postalCode: string | null;
    paymentTermCode: string | null; currencyCode: string;
  }>): void {
    if (p.name !== undefined) this._name = p.name;
    if (p.nameEn !== undefined) this._nameEn = p.nameEn;
    if (p.taxCode !== undefined) this._taxCode = p.taxCode;
    if (p.vendorType !== undefined) this._vendorType = p.vendorType;
    if (p.category !== undefined) this._category = p.category;
    if (p.classification !== undefined) this._classification = p.classification;
    if (p.phone !== undefined) this._phone = p.phone;
    if (p.email !== undefined) this._email = p.email;
    if (p.website !== undefined) this._website = p.website;
    if (p.address !== undefined) this._address = p.address;
    if (p.paymentTermCode !== undefined) this._paymentTermCode = p.paymentTermCode;
    if (p.currencyCode !== undefined) this._currencyCode = p.currencyCode;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new VendorUpdated(this._id.value, new Date(), { code: this._code }));
  }

  block(reason: string): void {
    if (this._status === VendorStatus.blocked) throw new DomainError("BusinessRule", "Vendor already blocked");
    this._status = VendorStatus.blocked; this._updatedAt = new Date(); this._version++;
    this.addEvent(new VendorBlocked(this._id.value, new Date(), { reason }));
  }

  unblock(): void {
    if (this._status !== VendorStatus.blocked) throw new DomainError("BusinessRule", "Vendor is not blocked");
    this._status = VendorStatus.active; this._updatedAt = new Date(); this._version++;
    this.addEvent(new VendorUnblocked(this._id.value, new Date(), {}));
  }

  deactivate(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Vendor already inactive");
    this._isActive = false; this._status = VendorStatus.inactive;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): VendorState {
    return { id: this._id.value, groupId: this._groupId, code: this._code, name: this._name,
      nameEn: this._nameEn, taxCode: this._taxCode, vendorType: this._vendorType,
      category: this._category, status: this._status, classification: this._classification,
      address: this._address, ward: this._ward, district: this._district, province: this._province,
      country: this._country, postalCode: this._postalCode, phone: this._phone, email: this._email,
      website: this._website, paymentTermCode: this._paymentTermCode, currencyCode: this._currencyCode,
      isActive: this._isActive, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Vendor Qualification ────────────────────────────────────────────────────────

export interface VendorQualificationState {
  id: string; vendorId: string; status: string; qualifiedBy: string;
  qualifiedAt: Date; expiresAt: Date | null; notes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class VendorQualification extends AggregateRoot<VendorQualificationId> {
  private _id: VendorQualificationId; private _vendorId: string;
  private _status: VendorQualificationStatus; private _qualifiedBy: string;
  private _qualifiedAt: Date; private _expiresAt: Date | null; private _notes: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: VendorQualificationId, vendorId: string, qualifiedBy: string) {
    super(); this._id = id; this._vendorId = vendorId; this._qualifiedBy = qualifiedBy;
    this._status = VendorQualificationStatus.underReview; this._qualifiedAt = new Date();
    this._expiresAt = null; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { vendorId: string; qualifiedBy: string; expiresAt?: Date; notes?: string }): VendorQualification {
    const q = new VendorQualification(VendorQualificationId.new(), p.vendorId, p.qualifiedBy);
    q._expiresAt = p.expiresAt ?? null; q._notes = p.notes ?? null;
    return q;
  }

  static load(s: VendorQualificationState): VendorQualification {
    const q = new VendorQualification(new VendorQualificationId(s.id), s.vendorId, s.qualifiedBy);
    q._status = s.status as VendorQualificationStatus; q._qualifiedAt = s.qualifiedAt;
    q._expiresAt = s.expiresAt; q._notes = s.notes; q._version = s.version;
    q._createdAt = s.createdAt; q._updatedAt = s.updatedAt; q._deletedAt = s.deletedAt;
    return q;
  }

  get id(): VendorQualificationId { return this._id; }
  get status(): VendorQualificationStatus { return this._status; }
  get version(): number { return this._version; }

  qualify(): void {
    this._status = VendorQualificationStatus.qualified; this._qualifiedAt = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  revoke(): void {
    this._status = VendorQualificationStatus.revoked;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): VendorQualificationState {
    return { id: this._id.value, vendorId: this._vendorId, status: this._status,
      qualifiedBy: this._qualifiedBy, qualifiedAt: this._qualifiedAt, expiresAt: this._expiresAt,
      notes: this._notes, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Vendor Evaluation ───────────────────────────────────────────────────────────

export interface VendorEvaluationState {
  id: string; vendorId: string; evaluator: string; score: string;
  criteria: string; comments: string | null; evaluatedAt: Date;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class VendorEvaluation extends AggregateRoot<VendorEvaluationId> {
  private _id: VendorEvaluationId; private _vendorId: string; private _evaluator: string;
  private _score: EvaluationScore; private _criteria: string; private _comments: string | null;
  private _evaluatedAt: Date; private _version: number; private _createdAt: Date;
  private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: VendorEvaluationId, vendorId: string, evaluator: string, score: EvaluationScore, criteria: string) {
    super(); this._id = id; this._vendorId = vendorId; this._evaluator = evaluator;
    this._score = score; this._criteria = criteria; this._comments = null;
    this._evaluatedAt = new Date();
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: { vendorId: string; evaluator: string; score: EvaluationScore; criteria: string; comments?: string }): VendorEvaluation {
    const e = new VendorEvaluation(VendorEvaluationId.new(), p.vendorId, p.evaluator, p.score, p.criteria);
    e._comments = p.comments ?? null;
    e.addEvent(new VendorEvaluationCompleted(e._id.value, new Date(), { vendorId: p.vendorId, score: p.score }));
    return e;
  }

  static load(s: VendorEvaluationState): VendorEvaluation {
    const e = new VendorEvaluation(new VendorEvaluationId(s.id), s.vendorId, s.evaluator, s.score as EvaluationScore, s.criteria);
    e._comments = s.comments; e._evaluatedAt = s.evaluatedAt; e._version = s.version;
    e._createdAt = s.createdAt; e._updatedAt = s.updatedAt; e._deletedAt = s.deletedAt;
    return e;
  }

  get id(): VendorEvaluationId { return this._id; }
  get score(): EvaluationScore { return this._score; }
  get version(): number { return this._version; }

  toState(): VendorEvaluationState {
    return { id: this._id.value, vendorId: this._vendorId, evaluator: this._evaluator,
      score: this._score, criteria: this._criteria, comments: this._comments,
      evaluatedAt: this._evaluatedAt, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
