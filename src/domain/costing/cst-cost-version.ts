import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { CostVersionId } from "./cst-ids.js";
import { CstCostMethod } from "./cst-enums.js";
import { CostingEvents } from "./cst-events.js";

export interface CostVersionState {
  id: string;
  code: string;
  name: string;
  costMethod: string;
  fiscalYearId: string;
  effectiveFrom: Date;
  effectiveTo: Date | null;
  isActive: boolean;
  isLocked: boolean;
  description: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class CostVersion extends AggregateRoot<CostVersionId> {
  private constructor(
    private _id: CostVersionId,
    private _code: string,
    private _name: string,
    private _costMethod: CstCostMethod,
    private _fiscalYearId: string,
    private _effectiveFrom: Date,
    private _effectiveTo: Date | null,
    private _isActive: boolean,
    private _isLocked: boolean,
    private _description: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
    private _deletedAt: Date | null,
  ) { super(); }

  static create(p: {
    code: string; name: string; costMethod: CstCostMethod; fiscalYearId: string;
    effectiveFrom: Date; effectiveTo?: Date | null; description?: string | null;
  }): CostVersion {
    const cv = new CostVersion(
      CostVersionId.new(), p.code, p.name, p.costMethod, p.fiscalYearId,
      p.effectiveFrom, p.effectiveTo ?? null, true, false,
      p.description ?? null, 1, new Date(), new Date(), null,
    );
    cv.addEvent(CostingEvents.CostVersionCreated(cv._id.value, { code: p.code, costMethod: p.costMethod }));
    return cv;
  }

  static load(s: CostVersionState): CostVersion {
    return new CostVersion(
      new CostVersionId(s.id), s.code, s.name, s.costMethod as CstCostMethod,
      s.fiscalYearId, s.effectiveFrom, s.effectiveTo, s.isActive, s.isLocked,
      s.description, s.version, s.createdAt, s.updatedAt, s.deletedAt,
    );
  }

  get id() { return this._id; }
  get code() { return this._code; }
  get costMethod() { return this._costMethod; }
  get isLocked() { return this._isLocked; }
  get version() { return this._version; }

  lock(): void {
    if (this._isLocked) throw new DomainError("BusinessRule", "Cost version already locked");
    this._isLocked = true;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.CostVersionLocked(this._id.value, { code: this._code }));
  }

  update(p: Partial<{ name: string; effectiveTo: Date | null; description: string | null }>): void {
    if (this._isLocked) throw new DomainError("BusinessRule", "Cannot update locked cost version");
    if (p.name !== undefined) this._name = p.name;
    if (p.effectiveTo !== undefined) this._effectiveTo = p.effectiveTo;
    if (p.description !== undefined) this._description = p.description;
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): CostVersionState {
    return {
      id: this._id.value, code: this._code, name: this._name,
      costMethod: this._costMethod, fiscalYearId: this._fiscalYearId,
      effectiveFrom: this._effectiveFrom, effectiveTo: this._effectiveTo,
      isActive: this._isActive, isLocked: this._isLocked,
      description: this._description, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
