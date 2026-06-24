import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class EinvInvoiceId extends Identifier { static new(): EinvInvoiceId { return new EinvInvoiceId(IdGenerator.uuid()); } static from(id: string): EinvInvoiceId { return new EinvInvoiceId(id); } }
export class EinvInvoiceLineId extends Identifier { static new(): EinvInvoiceLineId { return new EinvInvoiceLineId(IdGenerator.uuid()); } }
export class EinvInvoiceTypeId extends Identifier { static new(): EinvInvoiceTypeId { return new EinvInvoiceTypeId(IdGenerator.uuid()); } static from(id: string): EinvInvoiceTypeId { return new EinvInvoiceTypeId(id); } }
export class EinvTemplateId extends Identifier { static new(): EinvTemplateId { return new EinvTemplateId(IdGenerator.uuid()); } static from(id: string): EinvTemplateId { return new EinvTemplateId(id); } }
export class EinvSeriesId extends Identifier { static new(): EinvSeriesId { return new EinvSeriesId(IdGenerator.uuid()); } static from(id: string): EinvSeriesId { return new EinvSeriesId(id); } }
export class EinvProviderId extends Identifier { static new(): EinvProviderId { return new EinvProviderId(IdGenerator.uuid()); } static from(id: string): EinvProviderId { return new EinvProviderId(id); } }
export class EinvCertificateId extends Identifier { static new(): EinvCertificateId { return new EinvCertificateId(IdGenerator.uuid()); } static from(id: string): EinvCertificateId { return new EinvCertificateId(id); } }
export class EinvSignatureId extends Identifier { static new(): EinvSignatureId { return new EinvSignatureId(IdGenerator.uuid()); } }
export class EinvTransmissionId extends Identifier { static new(): EinvTransmissionId { return new EinvTransmissionId(IdGenerator.uuid()); } }
export class EinvAdjustmentId extends Identifier { static new(): EinvAdjustmentId { return new EinvAdjustmentId(IdGenerator.uuid()); } }
export class EinvArchiveId extends Identifier { static new(): EinvArchiveId { return new EinvArchiveId(IdGenerator.uuid()); } }
export class EinvDeliveryLogId extends Identifier { static new(): EinvDeliveryLogId { return new EinvDeliveryLogId(IdGenerator.uuid()); } }
export class EinvReasonCodeId extends Identifier { static new(): EinvReasonCodeId { return new EinvReasonCodeId(IdGenerator.uuid()); } }
export class EinvAuditLogId extends Identifier { static new(): EinvAuditLogId { return new EinvAuditLogId(IdGenerator.uuid()); } }
export class EinvProviderTemplateId extends Identifier { static new(): EinvProviderTemplateId { return new EinvProviderTemplateId(IdGenerator.uuid()); } }
