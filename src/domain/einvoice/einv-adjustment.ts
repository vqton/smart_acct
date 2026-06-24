import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { EinvAdjustmentId } from "./einv-ids.js";
import { EinvAdjustmentType } from "./einv-enums.js";

export interface EinvAdjustmentState {
  id: string; invoiceId: string; adjustmentType: string;
  originalInvoiceId: string;
  reasonCode: string | null; reasonDescription: string | null;
  adjustmentNumber: string | null; adjustmentDate: Date | null;
  additionalData: Record<string, unknown> | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvAdjustment extends AggregateRoot<EinvAdjustmentId> {
  private _id: EinvAdjustmentId;
  private _invoiceId: string;
  private _adjustmentType: EinvAdjustmentType;
  private _originalInvoiceId: string;
  private _reasonCode: string | null;
  private _reasonDescription: string | null;
  private _adjustmentNumber: string | null;
  private _adjustmentDate: Date | null;
  private _additionalData: Record<string, unknown> | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvAdjustmentId, invoiceId: string, adjustmentType: EinvAdjustmentType, originalInvoiceId: string) {
    super();
    this._id = id; this._invoiceId = invoiceId;
    this._adjustmentType = adjustmentType; this._originalInvoiceId = originalInvoiceId;
    this._reasonCode = null; this._reasonDescription = null;
    this._adjustmentNumber = null; this._adjustmentDate = null;
    this._additionalData = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: {
    invoiceId: string; adjustmentType: EinvAdjustmentType; originalInvoiceId: string;
    reasonCode?: string; reasonDescription?: string;
    adjustmentNumber?: string; adjustmentDate?: Date;
    additionalData?: Record<string, unknown>;
  }): EinvAdjustment {
    const a = new EinvAdjustment(EinvAdjustmentId.new(), p.invoiceId, p.adjustmentType, p.originalInvoiceId);
    a._reasonCode = p.reasonCode ?? null; a._reasonDescription = p.reasonDescription ?? null;
    a._adjustmentNumber = p.adjustmentNumber ?? null; a._adjustmentDate = p.adjustmentDate ?? null;
    a._additionalData = p.additionalData ?? null;
    return a;
  }

  static load(s: EinvAdjustmentState): EinvAdjustment {
    const a = new EinvAdjustment(new EinvAdjustmentId(s.id), s.invoiceId, s.adjustmentType as EinvAdjustmentType, s.originalInvoiceId);
    a._reasonCode = s.reasonCode; a._reasonDescription = s.reasonDescription;
    a._adjustmentNumber = s.adjustmentNumber; a._adjustmentDate = s.adjustmentDate;
    a._additionalData = s.additionalData;
    a._version = s.version; a._createdAt = s.createdAt; a._updatedAt = s.updatedAt;
    return a;
  }

  get id() { return this._id; }
  get adjustmentType() { return this._adjustmentType; }
  get originalInvoiceId() { return this._originalInvoiceId; }
  get version() { return this._version; }

  toState(): EinvAdjustmentState {
    return { id: this._id.value, invoiceId: this._invoiceId,
      adjustmentType: this._adjustmentType, originalInvoiceId: this._originalInvoiceId,
      reasonCode: this._reasonCode, reasonDescription: this._reasonDescription,
      adjustmentNumber: this._adjustmentNumber, adjustmentDate: this._adjustmentDate,
      additionalData: this._additionalData, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}
