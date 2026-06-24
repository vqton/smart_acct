import { BgtScenarioId } from "./bgt-ids.js";
import { BgtScenarioType } from "./bgt-enums.js";
import { BgtDomainEvent } from "./bgt-events.js";

export interface BgtBudgetScenarioState {
  id: string;
  budgetPlanId: string;
  code: string;
  name: string;
  scenarioType: string;
  description: string | null;
  assumptions: string | null;
  isBase: boolean;
  confidencePct: number | null;
  weightPct: number | null;
  createdById: string | null;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export class BgtBudgetScenario {
  private _events: BgtDomainEvent[] = [];
  private _version: number;

  private constructor(
    private _id: BgtScenarioId,
    private _budgetPlanId: string,
    private _code: string,
    private _name: string,
    private _scenarioType: string,
    private _description: string | null,
    private _assumptions: string | null,
    private _isBase: boolean,
    private _confidencePct: number | null,
    private _weightPct: number | null,
    private _createdById: string | null,
    version: number,
  ) { this._version = version; }

  get id(): BgtScenarioId { return this._id; }
  get budgetPlanId(): string { return this._budgetPlanId; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get scenarioType(): string { return this._scenarioType; }
  get description(): string | null { return this._description; }
  get assumptions(): string | null { return this._assumptions; }
  get isBase(): boolean { return this._isBase; }
  get confidencePct(): number | null { return this._confidencePct; }
  get weightPct(): number | null { return this._weightPct; }
  get createdById(): string | null { return this._createdById; }
  get version(): number { return this._version; }
  get events(): BgtDomainEvent[] { return this._events; }
  clearEvents(): void { this._events = []; }

  static create(p: {
    budgetPlanId: string; code: string; name: string; scenarioType?: string;
    description?: string; assumptions?: string; isBase?: boolean;
    confidencePct?: number; weightPct?: number; createdById?: string;
  }): BgtBudgetScenario {
    return new BgtBudgetScenario(
      BgtScenarioId.generate(), p.budgetPlanId, p.code, p.name,
      p.scenarioType ?? BgtScenarioType.Base, p.description ?? null,
      p.assumptions ?? null, p.isBase ?? false, p.confidencePct ?? null,
      p.weightPct ?? null, p.createdById ?? null, 1,
    );
  }

  static load(state: BgtBudgetScenarioState): BgtBudgetScenario {
    return new BgtBudgetScenario(
      BgtScenarioId.from(state.id), state.budgetPlanId, state.code, state.name,
      state.scenarioType, state.description, state.assumptions, state.isBase,
      state.confidencePct, state.weightPct, state.createdById, state.version,
    );
  }

  toState(): BgtBudgetScenarioState {
    return {
      id: this._id.value, budgetPlanId: this._budgetPlanId,
      code: this._code, name: this._name, scenarioType: this._scenarioType,
      description: this._description, assumptions: this._assumptions,
      isBase: this._isBase, confidencePct: this._confidencePct,
      weightPct: this._weightPct, createdById: this._createdById,
      version: this._version, createdAt: "", updatedAt: "",
    };
  }

  setBase(): void {
    this._isBase = true;
  }

  setConfidence(pct: number): void {
    if (pct < 0 || pct > 100) throw new Error("Confidence must be 0-100");
    this._confidencePct = pct;
  }

  setWeight(pct: number): void {
    if (pct < 0 || pct > 100) throw new Error("Weight must be 0-100");
    this._weightPct = pct;
  }
}
