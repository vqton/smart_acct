import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import {
  EinvInvoiceTypeId, EinvTemplateId, EinvSeriesId,
  EinvProviderId, EinvCertificateId, EinvProviderTemplateId, EinvReasonCodeId,
} from "./einv-ids.js";
import { EinvInvoiceCategory, EinvProviderType, EinvCertStatus, EinvSignatureMethod, EinvDigestAlgorithm } from "./einv-enums.js";
import {
  EinvTemplateCreated, EinvSeriesCreated, EinvCertificateRegistered,
  EinvCertificateExpired, EinvCertificateRevoked,
} from "./einv-events.js";
import { SeriesCode } from "./einv-value-objects.js";

// ─── Invoice Type ──────────────────────────────────────────────────────────────

export interface EinvInvoiceTypeState {
  id: string; code: string; name: string; description: string | null;
  category: string; isActive: boolean;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvInvoiceType extends AggregateRoot<EinvInvoiceTypeId> {
  private _id: EinvInvoiceTypeId;
  private _code: string;
  private _name: string;
  private _description: string | null;
  private _category: EinvInvoiceCategory;
  private _isActive: boolean;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvInvoiceTypeId, code: string, name: string, category: EinvInvoiceCategory) {
    super();
    this._id = id; this._code = code; this._name = name; this._category = category;
    this._description = null; this._isActive = true;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { code: string; name: string; category: EinvInvoiceCategory; description?: string }): EinvInvoiceType {
    return new EinvInvoiceType(EinvInvoiceTypeId.new(), p.code, p.name, p.category);
  }

  static load(s: EinvInvoiceTypeState): EinvInvoiceType {
    const t = new EinvInvoiceType(new EinvInvoiceTypeId(s.id), s.code, s.name, s.category as EinvInvoiceCategory);
    t._description = s.description; t._isActive = s.isActive;
    t._version = s.version; t._createdAt = s.createdAt; t._updatedAt = s.updatedAt;
    return t;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get name() { return this._name; }
  get category() { return this._category; }
  get isActive() { return this._isActive; }
  get version() { return this._version; }

  deactivate(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Invoice type already inactive");
    this._isActive = false;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): EinvInvoiceTypeState {
    return { id: this._id.value, code: this._code, name: this._name, description: this._description,
      category: this._category, isActive: this._isActive, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Template ──────────────────────────────────────────────────────────────────

export interface EinvTemplateState {
  id: string; code: string; name: string; description: string | null;
  templateFile: string | null; isDefault: boolean; isActive: boolean;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvTemplate extends AggregateRoot<EinvTemplateId> {
  private _id: EinvTemplateId;
  private _code: string;
  private _name: string;
  private _description: string | null;
  private _templateFile: string | null;
  private _isDefault: boolean;
  private _isActive: boolean;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvTemplateId, code: string, name: string) {
    super();
    this._id = id; this._code = code; this._name = name;
    this._description = null; this._templateFile = null;
    this._isDefault = false; this._isActive = true;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { code: string; name: string; description?: string; templateFile?: string; isDefault?: boolean }): EinvTemplate {
    const t = new EinvTemplate(EinvTemplateId.new(), p.code, p.name);
    t._description = p.description ?? null; t._templateFile = p.templateFile ?? null;
    t._isDefault = p.isDefault ?? false;
    t.addEvent(new EinvTemplateCreated(t._id.value, new Date(), { code: p.code, name: p.name }));
    return t;
  }

  static load(s: EinvTemplateState): EinvTemplate {
    const t = new EinvTemplate(new EinvTemplateId(s.id), s.code, s.name);
    t._description = s.description; t._templateFile = s.templateFile;
    t._isDefault = s.isDefault; t._isActive = s.isActive;
    t._version = s.version; t._createdAt = s.createdAt; t._updatedAt = s.updatedAt;
    return t;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get name() { return this._name; }
  get isDefault() { return this._isDefault; }
  get isActive() { return this._isActive; }
  get version() { return this._version; }

  deactivate(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Template already inactive");
    this._isActive = false;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): EinvTemplateState {
    return { id: this._id.value, code: this._code, name: this._name, description: this._description,
      templateFile: this._templateFile, isDefault: this._isDefault, isActive: this._isActive,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Series ────────────────────────────────────────────────────────────────────

export interface EinvSeriesState {
  id: string; code: string; name: string; invoiceTypeId: string;
  prefix: string; suffix: string | null;
  currentNumber: number; nextNumber: number; minDigits: number; maxDigits: number;
  fiscalYear: number | null; isActive: boolean;
  validFrom: Date; validTo: Date | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvSeries extends AggregateRoot<EinvSeriesId> {
  private _id: EinvSeriesId;
  private _code: SeriesCode;
  private _name: string;
  private _invoiceTypeId: string;
  private _prefix: string;
  private _suffix: string | null;
  private _currentNumber: number;
  private _nextNumber: number;
  private _minDigits: number;
  private _maxDigits: number;
  private _fiscalYear: number | null;
  private _isActive: boolean;
  private _validFrom: Date;
  private _validTo: Date | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvSeriesId, code: string, name: string, invoiceTypeId: string, prefix: string, validFrom: Date) {
    super();
    this._id = id; this._code = new SeriesCode(code); this._name = name;
    this._invoiceTypeId = invoiceTypeId; this._prefix = prefix;
    this._suffix = null; this._currentNumber = 0; this._nextNumber = 1;
    this._minDigits = 7; this._maxDigits = 7;
    this._fiscalYear = null; this._isActive = true;
    this._validFrom = validFrom; this._validTo = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { code: string; name: string; invoiceTypeId: string; prefix: string; suffix?: string; validFrom: Date; validTo?: Date; fiscalYear?: number; minDigits?: number; maxDigits?: number }): EinvSeries {
    const s = new EinvSeries(EinvSeriesId.new(), p.code, p.name, p.invoiceTypeId, p.prefix, p.validFrom);
    s._suffix = p.suffix ?? null; s._validTo = p.validTo ?? null;
    s._fiscalYear = p.fiscalYear ?? null;
    if (p.minDigits) s._minDigits = p.minDigits;
    if (p.maxDigits) s._maxDigits = p.maxDigits;
    s.addEvent(new EinvSeriesCreated(s._id.value, new Date(), { code: p.code, name: p.name }));
    return s;
  }

  static load(s: EinvSeriesState): EinvSeries {
    const obj = new EinvSeries(new EinvSeriesId(s.id), s.code, s.name, s.invoiceTypeId, s.prefix, s.validFrom);
    obj._suffix = s.suffix; obj._currentNumber = s.currentNumber; obj._nextNumber = s.nextNumber;
    obj._minDigits = s.minDigits; obj._maxDigits = s.maxDigits;
    obj._fiscalYear = s.fiscalYear; obj._isActive = s.isActive;
    obj._validTo = s.validTo; obj._version = s.version;
    obj._createdAt = s.createdAt; obj._updatedAt = s.updatedAt;
    return obj;
  }

  get id() { return this._id; }
  get code() { return this._code.value; }
  get name() { return this._name; }
  get prefix() { return this._prefix; }
  get nextNumber() { return this._nextNumber; }
  get isActive() { return this._isActive; }
  get version() { return this._version; }

  reserveNextNumber(): string {
    if (!this._isActive) throw new DomainError("BusinessRule", "Series is inactive");
    const num = String(this._nextNumber).padStart(this._minDigits, "0");
    this._currentNumber = this._nextNumber;
    this._nextNumber++;
    this._updatedAt = new Date(); this._version++;
    return `${this._prefix}${this._suffix ?? ""}${num}`;
  }

  deactivate(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Series already inactive");
    this._isActive = false;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): EinvSeriesState {
    return { id: this._id.value, code: this._code.value, name: this._name,
      invoiceTypeId: this._invoiceTypeId, prefix: this._prefix, suffix: this._suffix,
      currentNumber: this._currentNumber, nextNumber: this._nextNumber,
      minDigits: this._minDigits, maxDigits: this._maxDigits,
      fiscalYear: this._fiscalYear, isActive: this._isActive,
      validFrom: this._validFrom, validTo: this._validTo,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Provider ──────────────────────────────────────────────────────────────────

export interface EinvProviderState {
  id: string; code: string; name: string; providerType: string;
  apiEndpoint: string; apiVersion: string;
  apiUsername: string | null; apiPassword: string | null;
  apiKey: string | null; apiSecret: string | null;
  timeout: number; maxRetries: number; isActive: boolean;
  config: Record<string, unknown> | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvProvider extends AggregateRoot<EinvProviderId> {
  private _id: EinvProviderId;
  private _code: string;
  private _name: string;
  private _providerType: EinvProviderType;
  private _apiEndpoint: string;
  private _apiVersion: string;
  private _apiUsername: string | null;
  private _apiPassword: string | null;
  private _apiKey: string | null;
  private _apiSecret: string | null;
  private _timeout: number;
  private _maxRetries: number;
  private _isActive: boolean;
  private _config: Record<string, unknown> | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvProviderId, code: string, name: string, providerType: EinvProviderType, apiEndpoint: string, apiVersion: string) {
    super();
    this._id = id; this._code = code; this._name = name; this._providerType = providerType;
    this._apiEndpoint = apiEndpoint; this._apiVersion = apiVersion;
    this._apiUsername = null; this._apiPassword = null;
    this._apiKey = null; this._apiSecret = null;
    this._timeout = 30000; this._maxRetries = 3;
    this._isActive = true; this._config = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { code: string; name: string; providerType: EinvProviderType; apiEndpoint: string; apiVersion: string; apiUsername?: string; apiPassword?: string; apiKey?: string; apiSecret?: string; timeout?: number; maxRetries?: number }): EinvProvider {
    const pr = new EinvProvider(EinvProviderId.new(), p.code, p.name, p.providerType, p.apiEndpoint, p.apiVersion);
    pr._apiUsername = p.apiUsername ?? null; pr._apiPassword = p.apiPassword ?? null;
    pr._apiKey = p.apiKey ?? null; pr._apiSecret = p.apiSecret ?? null;
    if (p.timeout) pr._timeout = p.timeout;
    if (p.maxRetries) pr._maxRetries = p.maxRetries;
    return pr;
  }

  static load(s: EinvProviderState): EinvProvider {
    const p = new EinvProvider(new EinvProviderId(s.id), s.code, s.name, s.providerType as EinvProviderType, s.apiEndpoint, s.apiVersion);
    p._apiUsername = s.apiUsername; p._apiPassword = s.apiPassword;
    p._apiKey = s.apiKey; p._apiSecret = s.apiSecret;
    p._timeout = s.timeout; p._maxRetries = s.maxRetries; p._isActive = s.isActive;
    p._config = s.config; p._version = s.version;
    p._createdAt = s.createdAt; p._updatedAt = s.updatedAt;
    return p;
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get providerType() { return this._providerType; }
  get apiEndpoint() { return this._apiEndpoint; }
  get isActive() { return this._isActive; }
  get timeout() { return this._timeout; }
  get maxRetries() { return this._maxRetries; }
  get version() { return this._version; }

  deactivate(): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Provider already inactive");
    this._isActive = false;
    this._updatedAt = new Date(); this._version++;
  }

  toState(): EinvProviderState {
    return { id: this._id.value, code: this._code, name: this._name,
      providerType: this._providerType, apiEndpoint: this._apiEndpoint, apiVersion: this._apiVersion,
      apiUsername: this._apiUsername, apiPassword: this._apiPassword,
      apiKey: this._apiKey, apiSecret: this._apiSecret,
      timeout: this._timeout, maxRetries: this._maxRetries, isActive: this._isActive,
      config: this._config, version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Digital Certificate ───────────────────────────────────────────────────────

export interface EinvCertificateState {
  id: string; providerId: string; serialNumber: string;
  subjectDN: string; issuerDN: string; issuedTo: string; issuedBy: string;
  validFrom: Date; validTo: Date; thumbprint: string;
  certificateData: string | null; privateKeyRef: string | null;
  algorithm: string; digestAlgorithm: string;
  status: string; isDefault: boolean;
  companyId: string | null; branchId: string | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvDigitalCertificate extends AggregateRoot<EinvCertificateId> {
  private _id: EinvCertificateId;
  private _providerId: string;
  private _serialNumber: string;
  private _subjectDN: string;
  private _issuerDN: string;
  private _issuedTo: string;
  private _issuedBy: string;
  private _validFrom: Date;
  private _validTo: Date;
  private _thumbprint: string;
  private _certificateData: string | null;
  private _privateKeyRef: string | null;
  private _algorithm: EinvSignatureMethod;
  private _digestAlgorithm: EinvDigestAlgorithm;
  private _status: EinvCertStatus;
  private _isDefault: boolean;
  private _companyId: string | null;
  private _branchId: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvCertificateId, serialNumber: string, subjectDN: string, issuerDN: string, issuedTo: string, issuedBy: string, validFrom: Date, validTo: Date, thumbprint: string) {
    super();
    this._id = id; this._serialNumber = serialNumber; this._subjectDN = subjectDN;
    this._issuerDN = issuerDN; this._issuedTo = issuedTo; this._issuedBy = issuedBy;
    this._validFrom = validFrom; this._validTo = validTo; this._thumbprint = thumbprint;
    this._providerId = ""; this._certificateData = null; this._privateKeyRef = null;
    this._algorithm = EinvSignatureMethod.rsaSha256;
    this._digestAlgorithm = EinvDigestAlgorithm.sha256;
    this._status = EinvCertStatus.active; this._isDefault = false;
    this._companyId = null; this._branchId = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: {
    serialNumber: string; subjectDN: string; issuerDN: string;
    issuedTo: string; issuedBy: string; validFrom: Date; validTo: Date;
    thumbprint: string; providerId: string;
    algorithm?: EinvSignatureMethod; digestAlgorithm?: EinvDigestAlgorithm;
    certificateData?: string; privateKeyRef?: string;
    isDefault?: boolean; companyId?: string; branchId?: string;
  }): EinvDigitalCertificate {
    const c = new EinvDigitalCertificate(EinvCertificateId.new(), p.serialNumber, p.subjectDN, p.issuerDN, p.issuedTo, p.issuedBy, p.validFrom, p.validTo, p.thumbprint);
    c._providerId = p.providerId;
    c._certificateData = p.certificateData ?? null; c._privateKeyRef = p.privateKeyRef ?? null;
    if (p.algorithm) c._algorithm = p.algorithm;
    if (p.digestAlgorithm) c._digestAlgorithm = p.digestAlgorithm;
    c._isDefault = p.isDefault ?? false; c._companyId = p.companyId ?? null; c._branchId = p.branchId ?? null;
    c.addEvent(new EinvCertificateRegistered(c._id.value, new Date(), { serialNumber: p.serialNumber, issuedTo: p.issuedTo }));
    return c;
  }

  static load(s: EinvCertificateState): EinvDigitalCertificate {
    const c = new EinvDigitalCertificate(new EinvCertificateId(s.id), s.serialNumber, s.subjectDN, s.issuerDN, s.issuedTo, s.issuedBy, s.validFrom, s.validTo, s.thumbprint);
    c._providerId = s.providerId; c._certificateData = s.certificateData; c._privateKeyRef = s.privateKeyRef;
    c._algorithm = s.algorithm as EinvSignatureMethod;
    c._digestAlgorithm = s.digestAlgorithm as EinvDigestAlgorithm;
    c._status = s.status as EinvCertStatus; c._isDefault = s.isDefault;
    c._companyId = s.companyId; c._branchId = s.branchId;
    c._version = s.version; c._createdAt = s.createdAt; c._updatedAt = s.updatedAt;
    return c;
  }

  get id() { return this._id; }
  get serialNumber() { return this._serialNumber; }
  get subjectDN() { return this._subjectDN; }
  get validFrom() { return this._validFrom; }
  get validTo() { return this._validTo; }
  get status() { return this._status; }
  get isExpired(): boolean { return new Date() > this._validTo; }

  markExpired(): void {
    if (this._status === EinvCertStatus.expired) throw new DomainError("BusinessRule", "Certificate already expired");
    this._status = EinvCertStatus.expired;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvCertificateExpired(this._id.value, new Date(), { serialNumber: this._serialNumber }));
  }

  revoke(): void {
    if (this._status === EinvCertStatus.revoked) throw new DomainError("BusinessRule", "Certificate already revoked");
    this._status = EinvCertStatus.revoked;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvCertificateRevoked(this._id.value, new Date(), { serialNumber: this._serialNumber }));
  }

  toState(): EinvCertificateState {
    return { id: this._id.value, providerId: this._providerId, serialNumber: this._serialNumber,
      subjectDN: this._subjectDN, issuerDN: this._issuerDN, issuedTo: this._issuedTo,
      issuedBy: this._issuedBy, validFrom: this._validFrom, validTo: this._validTo,
      thumbprint: this._thumbprint, certificateData: this._certificateData,
      privateKeyRef: this._privateKeyRef, algorithm: this._algorithm, digestAlgorithm: this._digestAlgorithm,
      status: this._status, isDefault: this._isDefault, companyId: this._companyId,
      branchId: this._branchId, version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Provider Template Mapping ─────────────────────────────────────────────────

export interface EinvProviderTemplateState {
  id: string; providerId: string; templateId: string;
  providerTemplateCode: string; providerTemplateName: string | null;
  isDefault: boolean; isActive: boolean;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvProviderTemplate extends AggregateRoot<EinvProviderTemplateId> {
  private _id: EinvProviderTemplateId;
  private _providerId: string;
  private _templateId: string;
  private _providerTemplateCode: string;
  private _providerTemplateName: string | null;
  private _isDefault: boolean;
  private _isActive: boolean;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvProviderTemplateId, providerId: string, templateId: string, providerTemplateCode: string) {
    super();
    this._id = id; this._providerId = providerId; this._templateId = templateId;
    this._providerTemplateCode = providerTemplateCode;
    this._providerTemplateName = null; this._isDefault = false; this._isActive = true;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { providerId: string; templateId: string; providerTemplateCode: string; providerTemplateName?: string; isDefault?: boolean }): EinvProviderTemplate {
    const pt = new EinvProviderTemplate(EinvProviderTemplateId.new(), p.providerId, p.templateId, p.providerTemplateCode);
    pt._providerTemplateName = p.providerTemplateName ?? null;
    pt._isDefault = p.isDefault ?? false;
    return pt;
  }

  static load(s: EinvProviderTemplateState): EinvProviderTemplate {
    const pt = new EinvProviderTemplate(new EinvProviderTemplateId(s.id), s.providerId, s.templateId, s.providerTemplateCode);
    pt._providerTemplateName = s.providerTemplateName; pt._isDefault = s.isDefault;
    pt._isActive = s.isActive; pt._version = s.version;
    pt._createdAt = s.createdAt; pt._updatedAt = s.updatedAt;
    return pt;
  }

  get id() { return this._id; }
  get providerTemplateCode() { return this._providerTemplateCode; }
  get isActive() { return this._isActive; }

  toState(): EinvProviderTemplateState {
    return { id: this._id.value, providerId: this._providerId, templateId: this._templateId,
      providerTemplateCode: this._providerTemplateCode, providerTemplateName: this._providerTemplateName,
      isDefault: this._isDefault, isActive: this._isActive, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}

// ─── Reason Code ───────────────────────────────────────────────────────────────

export interface EinvReasonCodeState {
  id: string; code: string; name: string; description: string | null;
  category: string; isActive: boolean;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvReasonCode extends AggregateRoot<EinvReasonCodeId> {
  private _id: EinvReasonCodeId;
  private _code: string;
  private _name: string;
  private _description: string | null;
  private _category: string;
  private _isActive: boolean;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvReasonCodeId, code: string, name: string, category: string) {
    super();
    this._id = id; this._code = code; this._name = name; this._category = category;
    this._description = null; this._isActive = true;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: { code: string; name: string; category: string; description?: string }): EinvReasonCode {
    return new EinvReasonCode(EinvReasonCodeId.new(), p.code, p.name, p.category);
  }

  static load(s: EinvReasonCodeState): EinvReasonCode {
    const r = new EinvReasonCode(new EinvReasonCodeId(s.id), s.code, s.name, s.category);
    r._description = s.description; r._isActive = s.isActive;
    r._version = s.version; r._createdAt = s.createdAt; r._updatedAt = s.updatedAt;
    return r;
  }

  get id() { return this._id; }
  get code() { return this._code; }

  toState(): EinvReasonCodeState {
    return { id: this._id.value, code: this._code, name: this._name,
      description: this._description, category: this._category, isActive: this._isActive,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}
