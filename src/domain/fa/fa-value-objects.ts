import { Money } from "../shared/money.js";
import { FaAssetType, FaDepreciationMethod } from "./fa-enums.js";

export class AssetDimensions {
  constructor(
    readonly lengthCm: number | null,
    readonly widthCm: number | null,
    readonly heightCm: number | null,
    readonly weightKg: number | null,
    readonly volumeM3: number | null,
  ) {}
}

export class AssetLocation {
  constructor(
    readonly address: string | null,
    readonly ward: string | null,
    readonly district: string | null,
    readonly province: string | null,
    readonly country: string,
    readonly building: string | null,
    readonly floor: string | null,
    readonly room: string | null,
    readonly gpsCoordinates: string | null,
  ) {}
}

export class DepreciationSchedule {
  constructor(
    readonly method: FaDepreciationMethod,
    readonly usefulLifeYears: number,
    readonly usefulLifeMonths: number,
    readonly usefulLifeUnits: number | null,
    readonly residualValue: Money,
    readonly depreciationRate: number | null,
  ) {}

  get totalMonths(): number {
    return this.usefulLifeYears * 12 + this.usefulLifeMonths;
  }
}

export class DepreciationResult {
  constructor(
    readonly periodNumber: number,
    readonly depreciationAmount: Money,
    readonly accumulatedDepreciation: Money,
    readonly netBookValueBefore: Money,
    readonly netBookValueAfter: Money,
  ) {}
}

export class RevaluationResult {
  constructor(
    readonly previousValue: Money,
    readonly revaluedAmount: Money,
    readonly newValue: Money,
    readonly revaluationReserve: Money,
  ) {}
}

export class DisposalResult {
  constructor(
    readonly proceeds: Money,
    readonly costs: Money,
    readonly gainOrLoss: Money,
  ) {}

  get isGain(): boolean {
    return this.gainOrLoss.greaterThan(Money.zero());
  }

  get isLoss(): boolean {
    return this.gainOrLoss.lessThan(Money.zero());
  }
}

export class LeaseScheduleItem {
  constructor(
    readonly paymentNumber: number,
    readonly dueDate: Date,
    readonly totalAmount: Money,
    readonly interestAmount: Money,
    readonly principalAmount: Money,
    readonly balanceAfter: Money,
  ) {}
}

export class AssetTagInfo {
  constructor(
    readonly tagType: "barcode" | "qr_code" | "rfid",
    readonly tagValue: string,
    readonly assignedAt: Date,
  ) {}
}

export class CipProgressSummary {
  constructor(
    readonly totalBudget: Money,
    readonly totalCost: Money,
    readonly capitalizedAmount: Money,
    readonly completionPercent: number,
  ) {}
}

export class MaintenanceCostSummary {
  constructor(
    readonly totalCost: Money,
    readonly count: number,
    readonly averageCost: Money,
    readonly lastMaintenanceDate: Date | null,
  ) {}
}
