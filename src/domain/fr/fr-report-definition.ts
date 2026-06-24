import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { FrReportDefinitionId } from "./fr-ids.js";
import { FrReportStatus, FrRowType, FrReportCategoryType } from "./fr-enums.js";
import { ReportDefinitionCreated, ReportDefinitionActivated } from "./fr-events.js";
import type { ReportRowDefinition } from "./fr-value-objects.js";

export interface ReportDefinitionState {
  id: string;
  code: string;
  name: string;
  nameEn: string | null;
  category: FrReportCategoryType;
  status: FrReportStatus;
  description: string | null;
  displayCurrency: string;
  displayScale: number;
  displayDecimals: number;
  isComparative: boolean;
  comparativePeriods: number;
  isConsolidated: boolean;
  defaultFiscalYearId: string | null;
  rows: ReportRowDefinition[];
  createdById: string;
  createdAt: Date;
  updatedAt: Date;
  version: number;
  deletedAt: Date | null;
}

export class ReportDefinition extends AggregateRoot<FrReportDefinitionId> {
  private _id!: FrReportDefinitionId;
  private _code!: string;
  private _name!: string;
  private _nameEn: string | null = null;
  private _category!: FrReportCategoryType;
  private _status: FrReportStatus = FrReportStatus.Draft;
  private _description: string | null = null;
  private _displayCurrency = "VND";
  private _displayScale = 0;
  private _displayDecimals = 0;
  private _isComparative = false;
  private _comparativePeriods = 1;
  private _isConsolidated = false;
  private _defaultFiscalYearId: string | null = null;
  private _rows: ReportRowDefinition[] = [];
  private _createdById!: string;
  private _createdAt: Date = new Date();
  private _updatedAt: Date = new Date();
  private _version = 1;
  private _deletedAt: Date | null = null;

  private constructor(id: FrReportDefinitionId) { super(); this._id = id; }

  static create(params: {
    code: string;
    name: string;
    nameEn?: string;
    category: FrReportCategoryType;
    description?: string;
    displayCurrency?: string;
    isComparative?: boolean;
    createdById: string;
  }): ReportDefinition {
    const def = new ReportDefinition(FrReportDefinitionId.new());
    def._code = params.code;
    def._name = params.name;
    def._nameEn = params.nameEn ?? null;
    def._category = params.category;
    def._description = params.description ?? null;
    def._displayCurrency = params.displayCurrency ?? "VND";
    def._isComparative = params.isComparative ?? false;
    def._createdById = params.createdById;

    def.addEvent(new ReportDefinitionCreated(def._id.value, new Date(), {
      code: def._code,
      name: def._name,
      category: def._category,
      createdById: def._createdById,
    }));

    return def;
  }

  static load(state: ReportDefinitionState): ReportDefinition {
    const def = new ReportDefinition(new FrReportDefinitionId(state.id));
    def._code = state.code;
    def._name = state.name;
    def._nameEn = state.nameEn;
    def._category = state.category;
    def._status = state.status;
    def._description = state.description;
    def._displayCurrency = state.displayCurrency;
    def._displayScale = state.displayScale;
    def._displayDecimals = state.displayDecimals;
    def._isComparative = state.isComparative;
    def._comparativePeriods = state.comparativePeriods;
    def._isConsolidated = state.isConsolidated;
    def._defaultFiscalYearId = state.defaultFiscalYearId;
    def._rows = state.rows;
    def._createdById = state.createdById;
    def._createdAt = state.createdAt;
    def._updatedAt = state.updatedAt;
    def._version = state.version;
    def._deletedAt = state.deletedAt;
    return def;
  }

  get id(): FrReportDefinitionId { return this._id; }
  get code(): string { return this._code; }
  get name(): string { return this._name; }
  get nameEn(): string | null { return this._nameEn; }
  get category(): FrReportCategoryType { return this._category; }
  get status(): FrReportStatus { return this._status; }
  get description(): string | null { return this._description; }
  get displayCurrency(): string { return this._displayCurrency; }
  get isComparative(): boolean { return this._isComparative; }
  get comparativePeriods(): number { return this._comparativePeriods; }
  get isConsolidated(): boolean { return this._isConsolidated; }
  get rows(): readonly ReportRowDefinition[] { return this._rows; }
  get createdById(): string { return this._createdById; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }
  get version(): number { return this._version; }
  get deletedAt(): Date | null { return this._deletedAt; }

  activate(): void {
    if (this._status === FrReportStatus.Active) return;
    if (this._status !== FrReportStatus.Draft && this._status !== FrReportStatus.Inactive) {
      throw new DomainError("BusinessRule", "Only draft or inactive reports can be activated");
    }
    this._status = FrReportStatus.Active;
    this._updatedAt = new Date();
    this._version++;
    this.addEvent(new ReportDefinitionActivated(this._id.value, new Date(), { code: this._code }));
  }

  deactivate(): void {
    if (this._status !== FrReportStatus.Active) {
      throw new DomainError("BusinessRule", "Only active reports can be deactivated");
    }
    this._status = FrReportStatus.Inactive;
    this._updatedAt = new Date();
    this._version++;
  }

  addRow(row: ReportRowDefinition): void {
    if (row.parentRowCode) {
      const parent = this._rows.find(r => r.rowCode === row.parentRowCode);
      if (!parent) throw new DomainError("Validation", `Parent row ${row.parentRowCode} not found`);
    }
    this._rows.push(row);
    this._updatedAt = new Date();
    this._version++;
  }

  removeRow(rowCode: string): void {
    const idx = this._rows.findIndex(r => r.rowCode === rowCode);
    if (idx < 0) throw new DomainError("NotFound", `Row ${rowCode} not found`);
    const hasChildren = this._rows.some(r => r.parentRowCode === rowCode);
    if (hasChildren) throw new DomainError("BusinessRule", "Cannot remove row with children");
    this._rows.splice(idx, 1);
    this._updatedAt = new Date();
    this._version++;
  }

  modify(params: { name?: string; description?: string | null }): void {
    if (params.name !== undefined) this._name = params.name;
    if (params.description !== undefined) this._description = params.description;
    this._updatedAt = new Date();
    this._version++;
  }

  markDeleted(): void {
    this._deletedAt = new Date();
    this._updatedAt = new Date();
    this._version++;
  }

  toState(): ReportDefinitionState {
    return {
      id: this._id.value,
      code: this._code,
      name: this._name,
      nameEn: this._nameEn,
      category: this._category,
      status: this._status,
      description: this._description,
      displayCurrency: this._displayCurrency,
      displayScale: this._displayScale,
      displayDecimals: this._displayDecimals,
      isComparative: this._isComparative,
      comparativePeriods: this._comparativePeriods,
      isConsolidated: this._isConsolidated,
      defaultFiscalYearId: this._defaultFiscalYearId,
      rows: [...this._rows],
      createdById: this._createdById,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
      version: this._version,
      deletedAt: this._deletedAt,
    };
  }
}
