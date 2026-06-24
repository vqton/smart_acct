import { Entity } from "../../shared/entity.js";
import { ProductionVarianceId } from "./cst-ids.js";
import { CstVarianceType, CstCostElementType } from "./cst-enums.js";

export interface ProductionVarianceState {
  id: string;
  orderId: string;
  varianceType: string;
  costElement: string;
  standardAmount: number;
  actualAmount: number;
  varianceAmount: number;
  variancePercent: number;
  quantityVariance: number | null;
  priceVariance: number | null;
  description: string | null;
  periodId: string | null;
  fiscalYearId: string | null;
  glBatchId: string | null;
  postedToGL: boolean;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class ProductionVariance extends Entity<ProductionVarianceId> {
  private constructor(
    private _id: ProductionVarianceId,
    private _orderId: string,
    private _varianceType: CstVarianceType,
    private _costElement: CstCostElementType,
    private _standardAmount: number,
    private _actualAmount: number,
    private _varianceAmount: number,
    private _variancePercent: number,
    private _quantityVariance: number | null,
    private _priceVariance: number | null,
    private _description: string | null,
    private _periodId: string | null,
    private _fiscalYearId: string | null,
    private _glBatchId: string | null,
    private _postedToGL: boolean,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
  ) { super(); }

  static create(p: {
    orderId: string; varianceType: CstVarianceType; costElement: CstCostElementType;
    standardAmount: number; actualAmount: number;
    quantityVariance?: number | null; priceVariance?: number | null;
    description?: string | null; periodId?: string | null;
    fiscalYearId?: string | null;
  }): ProductionVariance {
    const va = p.actualAmount - p.standardAmount;
    const vp = p.standardAmount !== 0 ? (va / p.standardAmount) * 100 : 0;
    return new ProductionVariance(
      ProductionVarianceId.new(), p.orderId, p.varianceType, p.costElement,
      p.standardAmount, p.actualAmount, va, vp,
      p.quantityVariance ?? null, p.priceVariance ?? null,
      p.description ?? null, p.periodId ?? null, p.fiscalYearId ?? null,
      null, false, 1, new Date(), new Date(),
    );
  }

  static load(s: ProductionVarianceState): ProductionVariance {
    return new ProductionVariance(
      new ProductionVarianceId(s.id), s.orderId,
      s.varianceType as CstVarianceType,
      s.costElement as CstCostElementType,
      s.standardAmount, s.actualAmount, s.varianceAmount,
      s.variancePercent, s.quantityVariance, s.priceVariance,
      s.description, s.periodId, s.fiscalYearId, s.glBatchId,
      s.postedToGL, s.version, s.createdAt, s.updatedAt,
    );
  }

  get id() { return this._id; }
  get varianceAmount() { return this._varianceAmount; }
  get varianceType() { return this._varianceType; }

  toState(): ProductionVarianceState {
    return {
      id: this._id.value, orderId: this._orderId,
      varianceType: this._varianceType, costElement: this._costElement,
      standardAmount: this._standardAmount,
      actualAmount: this._actualAmount,
      varianceAmount: this._varianceAmount,
      variancePercent: this._variancePercent,
      quantityVariance: this._quantityVariance,
      priceVariance: this._priceVariance,
      description: this._description, periodId: this._periodId,
      fiscalYearId: this._fiscalYearId, glBatchId: this._glBatchId,
      postedToGL: this._postedToGL, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
