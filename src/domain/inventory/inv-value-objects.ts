export class ItemDimensions {
  constructor(
    readonly lengthCm: number | null,
    readonly widthCm: number | null,
    readonly heightCm: number | null,
    readonly weightKg: number | null,
    readonly volumeCm3: number | null,
  ) {}
}

export class UomConversion {
  constructor(
    readonly fromUomId: string,
    readonly toUomId: string,
    readonly conversionRate: number,
  ) {
    if (conversionRate <= 0) throw new Error("Conversion rate must be positive");
  }
}

export class WarehouseAddress {
  constructor(
    readonly address: string,
    readonly city: string | null,
    readonly district: string | null,
    readonly ward: string | null,
    readonly country: string,
  ) {}
}

export class LocationCapacity {
  constructor(
    readonly maxWeightKg: number | null,
    readonly maxVolumeCm3: number | null,
    readonly maxPalletCount: number | null,
  ) {}
}

export class CostLayerKey {
  constructor(
    readonly itemId: string,
    readonly warehouseId: string,
    readonly lotId: string | null,
  ) {}
}

export class InventoryValuation {
  constructor(
    readonly quantity: number,
    readonly unitCost: number,
    readonly totalCost: number,
    readonly currencyCode: string,
    readonly exchangeRate: number,
  ) {}
}

export class CountVariance {
  constructor(
    readonly expectedQty: number,
    readonly actualQty: number,
    readonly varianceQty: number,
    readonly varianceValue: number,
  ) {}
}

export class ReservationKey {
  constructor(
    readonly itemId: string,
    readonly warehouseId: string,
    readonly locationId: string | null,
    readonly lotId: string | null,
  ) {}
}
