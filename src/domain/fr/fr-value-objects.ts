import { ValueObject } from "../../shared/value-object.js";

export interface ReportRowDefinition {
  rowCode: string;
  label: string;
  labelEn: string | null;
  rowType: string;
  indentLevel: number;
  displayOrder: number;
  isBold: boolean;
  isVisible: boolean;
  showSubtotal: boolean;
  pageBreakBefore: boolean;
  parentRowCode: string | null;
  cells: ReportCellDefinition[];
}

export interface ReportCellDefinition {
  columnId: string | null;
  cellType: string;
  formulaId: string | null;
  formulaText: string | null;
  accountCode: string | null;
  accountCategory: string | null;
  accountNature: string | null;
  aggregationFunction: string | null;
  periodOffset: number;
  periodCount: number;
  costCenterId: string | null;
  departmentId: string | null;
  projectId: string | null;
  branchId: string | null;
  legalEntityId: string | null;
  hideIfZero: boolean;
  hideIfNegative: boolean;
  staticValue: string | null;
  formatPattern: string | null;
  decimalPlaces: number;
}

export class ReportColumn {
  constructor(
    readonly id: string,
    readonly name: string,
    readonly displayOrder: number,
    readonly width: number | null,
    readonly align: "left" | "center" | "right",
  ) {}

  static create(params: {
    id: string;
    name: string;
    displayOrder: number;
    width?: number;
    align?: "left" | "center" | "right";
  }): ReportColumn {
    return new ReportColumn(params.id, params.name, params.displayOrder, params.width ?? null, params.align ?? "left");
  }
}

export class ConsolidationEliminationEntry {
  constructor(
    readonly eliminationType: string,
    readonly fromEntityId: string | null,
    readonly toEntityId: string | null,
    readonly accountCode: string,
    readonly debitAmount: number,
    readonly creditAmount: number,
    readonly description: string | null,
    readonly isAutoDetected: boolean,
    readonly sourceBatchId: string | null,
  ) {}

  get isBalanced(): boolean {
    return this.debitAmount === this.creditAmount;
  }
}

export class ConsolidationGroupMember {
  constructor(
    readonly legalEntityId: string,
    readonly legalEntityCode: string,
    readonly legalEntityName: string,
    readonly ownershipPercentage: number,
    readonly consolidationMethod: string,
    readonly consolidationDate: Date,
    readonly functionalCurrency: string,
    readonly goodwillAmount: number,
    readonly isActive: boolean,
  ) {}
}
