import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PettyCashId, PettyCashReplenishmentId } from "./cm-ids.js";
import { PettyCashStatus } from "./cm-enums.js";
import { PettyCashReplenished } from "./cm-domain-events.js";

export interface PettyCashState {
  id: string;
  locationId: string;
  fundCode: string;
  fundName: string;
  fundBalance: number;
  maximumBalance: number;
  minimumBalance: number;
  replenishThreshold: number;
  currencyCode: string;
  holderId: string | null;
  status: string;
  description: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class PettyCash extends AggregateRoot<PettyCashId> {
  private _id: PettyCashId;
  private _locationId: string;
  private _fundCode: string;
  private _fundName: string;
  private _fundBalance: number;
  private _maximumBalance: number;
  private _minimumBalance: number;
  private _replenishThreshold: number;
  private _currencyCode: string;
  private _holderId: string | null;
  private _status: PettyCashStatus;
  private _description: string | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  constructor(
    id: PettyCashId,
    locationId: string,
    fundCode: string,
    fundName: string,
    maximumBalance: number,
    minimumBalance: number,
    currencyCode: string,
    holderId: string | null = null,
  ) {
    super();
    this._id = id;
    this._locationId = locationId;
    this._fundCode = fundCode;
    this._fundName = fundName;
    this._fundBalance = 0;
    this._maximumBalance = maximumBalance;
    this._minimumBalance = minimumBalance;
    this._replenishThreshold = maximumBalance * 0.2;
    this._currencyCode = currencyCode;
    this._holderId = holderId;
    this._status = PettyCashStatus.Active;
    this._description = null;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    locationId: string;
    fundCode: string;
    fundName: string;
    maximumBalance: number;
    minimumBalance: number;
    currencyCode?: string;
    holderId?: string | null;
    description?: string | null;
  }): PettyCash {
    const fund = new PettyCash(
      PettyCashId.new(),
      params.locationId,
      params.fundCode,
      params.fundName,
      params.maximumBalance,
      params.minimumBalance,
      params.currencyCode ?? "VND",
      params.holderId ?? null,
    );
    fund._description = params.description ?? null;
    return fund;
  }

  static load(state: PettyCashState): PettyCash {
    const f = new PettyCash(
      new PettyCashId(state.id),
      state.locationId,
      state.fundCode,
      state.fundName,
      state.maximumBalance,
      state.minimumBalance,
      state.currencyCode,
      state.holderId,
    );
    f._fundBalance = state.fundBalance;
    f._replenishThreshold = state.replenishThreshold;
    f._status = state.status as PettyCashStatus;
    f._description = state.description;
    f._version = state.version;
    f._createdAt = state.createdAt;
    f._updatedAt = state.updatedAt;
    f._deletedAt = state.deletedAt;
    return f;
  }

  get id(): PettyCashId { return this._id; }
  get locationId(): string { return this._locationId; }
  get fundCode(): string { return this._fundCode; }
  get fundName(): string { return this._fundName; }
  get fundBalance(): number { return this._fundBalance; }
  get maximumBalance(): number { return this._maximumBalance; }
  get minimumBalance(): number { return this._minimumBalance; }
  get replenishThreshold(): number { return this._replenishThreshold; }
  get currencyCode(): string { return this._currencyCode; }
  get holderId(): string | null { return this._holderId; }
  get status(): PettyCashStatus { return this._status; }
  get description(): string | null { return this._description; }
  get version(): number { return this._version; }

  needsReplenishment(): boolean {
    return this._fundBalance <= this._replenishThreshold;
  }

  replenish(amount: number, reference: string): PettyCashReplenishment {
    if (this._status !== PettyCashStatus.Active && this._status !== PettyCashStatus.Replenishing) {
      throw new DomainError("BusinessRule", "Petty cash fund is not active");
    }
    if (amount <= 0) throw new DomainError("BusinessRule", "Replenishment amount must be positive");
    this._fundBalance += amount;
    if (this._fundBalance > this._maximumBalance) {
      throw new DomainError("BusinessRule", `Replenishment would exceed maximum balance ${this._maximumBalance}`);
    }
    this._status = PettyCashStatus.Active;
    this._updatedAt = new Date();
    this._version++;

    const replenishment = new PettyCashReplenishment(
      PettyCashReplenishmentId.new(),
      this._id.value,
      amount,
      new Date(),
      reference,
    );

    this.addEvent(new PettyCashReplenished(this._id.value, new Date(), {
      fundCode: this._fundCode,
      amount,
      reference,
      newBalance: this._fundBalance,
    }));

    return replenishment;
  }

  disburse(amount: number): void {
    if (this._status !== PettyCashStatus.Active) {
      throw new DomainError("BusinessRule", "Petty cash fund is not active");
    }
    if (amount <= 0) throw new DomainError("BusinessRule", "Disbursement amount must be positive");
    if (amount > this._fundBalance) {
      throw new DomainError("BusinessRule", `Insufficient petty cash. Available: ${this._fundBalance}`);
    }
    this._fundBalance -= amount;
    this._updatedAt = new Date();
    this._version++;

    if (this._fundBalance <= this._replenishThreshold) {
      this._status = PettyCashStatus.Replenishing;
    }
  }

  toState(): PettyCashState {
    return {
      id: this._id.value,
      locationId: this._locationId,
      fundCode: this._fundCode,
      fundName: this._fundName,
      fundBalance: this._fundBalance,
      maximumBalance: this._maximumBalance,
      minimumBalance: this._minimumBalance,
      replenishThreshold: this._replenishThreshold,
      currencyCode: this._currencyCode,
      holderId: this._holderId,
      status: this._status,
      description: this._description,
      version: this._version,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      deletedAt: this._deletedAt,
    };
  }
}

export interface PettyCashReplenishmentState {
  id: string;
  fundId: string;
  replenishNumber: string;
  amount: number;
  replenishDate: Date;
  receivedById: string | null;
  reference: string | null;
  notes: string | null;
  postedToGL: boolean;
  glBatchId: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class PettyCashReplenishment {
  private _id: PettyCashReplenishmentId;
  private _fundId: string;
  private _amount: number;
  private _replenishDate: Date;
  private _reference: string | null;

  constructor(
    id: PettyCashReplenishmentId,
    fundId: string,
    amount: number,
    replenishDate: Date,
    reference: string | null = null,
  ) {
    this._id = id;
    this._fundId = fundId;
    this._amount = amount;
    this._replenishDate = replenishDate;
    this._reference = reference;
  }

  get id(): PettyCashReplenishmentId { return this._id; }
  get fundId(): string { return this._fundId; }
  get amount(): number { return this._amount; }
  get replenishDate(): Date { return this._replenishDate; }
  get reference(): string | null { return this._reference; }
}
