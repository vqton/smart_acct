import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { EinvArchiveId } from "./einv-ids.js";
import { EinvArchiveStatus } from "./einv-enums.js";

export interface EinvArchiveState {
  id: string; invoiceId: string; archiveDate: Date; archiveType: string;
  storagePath: string | null;
  xmlData: string | null; pdfData: string | null;
  checksum: string | null; fileSize: bigint | null;
  status: string; retentionUntil: Date | null; destroyedAt: Date | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class EinvArchive extends AggregateRoot<EinvArchiveId> {
  private _id: EinvArchiveId;
  private _invoiceId: string;
  private _archiveDate: Date;
  private _archiveType: string;
  private _storagePath: string | null;
  private _xmlData: string | null;
  private _pdfData: string | null;
  private _checksum: string | null;
  private _fileSize: bigint | null;
  private _status: EinvArchiveStatus;
  private _retentionUntil: Date | null;
  private _destroyedAt: Date | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(id: EinvArchiveId, invoiceId: string, archiveDate: Date, archiveType: string) {
    super();
    this._id = id; this._invoiceId = invoiceId; this._archiveDate = archiveDate; this._archiveType = archiveType;
    this._storagePath = null; this._xmlData = null; this._pdfData = null;
    this._checksum = null; this._fileSize = null;
    this._status = EinvArchiveStatus.active;
    this._retentionUntil = null; this._destroyedAt = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date();
  }

  static create(p: {
    invoiceId: string; archiveDate: Date; archiveType: string;
    storagePath?: string; xmlData?: string; pdfData?: string;
    checksum?: string; fileSize?: bigint; retentionUntil?: Date;
  }): EinvArchive {
    const a = new EinvArchive(EinvArchiveId.new(), p.invoiceId, p.archiveDate, p.archiveType);
    a._storagePath = p.storagePath ?? null; a._xmlData = p.xmlData ?? null;
    a._pdfData = p.pdfData ?? null; a._checksum = p.checksum ?? null;
    a._fileSize = p.fileSize ?? null; a._retentionUntil = p.retentionUntil ?? null;
    return a;
  }

  static load(s: EinvArchiveState): EinvArchive {
    const a = new EinvArchive(new EinvArchiveId(s.id), s.invoiceId, s.archiveDate, s.archiveType);
    a._storagePath = s.storagePath; a._xmlData = s.xmlData; a._pdfData = s.pdfData;
    a._checksum = s.checksum; a._fileSize = s.fileSize;
    a._status = s.status as EinvArchiveStatus;
    a._retentionUntil = s.retentionUntil; a._destroyedAt = s.destroyedAt;
    a._version = s.version; a._createdAt = s.createdAt; a._updatedAt = s.updatedAt;
    return a;
  }

  get id() { return this._id; }
  get status() { return this._status; }
  get version() { return this._version; }

  markArchived(): void {
    if (this._status !== EinvArchiveStatus.active) throw new DomainError("BusinessRule", "Archive already archived");
    this._status = EinvArchiveStatus.archived;
    this._updatedAt = new Date(); this._version++;
  }

  markDestroyed(): void {
    if (this._status === EinvArchiveStatus.destroyed) throw new DomainError("BusinessRule", "Archive already destroyed");
    this._status = EinvArchiveStatus.destroyed;
    this._destroyedAt = new Date();
    this._updatedAt = new Date(); this._version++;
  }

  toState(): EinvArchiveState {
    return { id: this._id.value, invoiceId: this._invoiceId, archiveDate: this._archiveDate,
      archiveType: this._archiveType, storagePath: this._storagePath,
      xmlData: this._xmlData, pdfData: this._pdfData,
      checksum: this._checksum, fileSize: this._fileSize,
      status: this._status, retentionUntil: this._retentionUntil,
      destroyedAt: this._destroyedAt, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt };
  }
}
