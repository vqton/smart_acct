import { DomainError } from "../../shared/domain-error.js";

export interface InventorySpecification {
  check(context: Record<string, unknown>): void;
}

export class NegativeInventorySpec implements InventorySpecification {
  constructor(private readonly allowNegative: boolean) {}
  check(ctx: Record<string, unknown>): void {
    if (!this.allowNegative && (ctx.newBalance as number) < 0) {
      throw new DomainError("BusinessRule", "Negative inventory not allowed");
    }
  }
}

export class ExpiredLotSpec implements InventorySpecification {
  check(ctx: Record<string, unknown>): void {
    if (ctx.expirationDate && new Date(ctx.expirationDate as Date) < new Date()) {
      throw new DomainError("BusinessRule", "Cannot transact expired inventory");
    }
  }
}

export class BlockedInventorySpec implements InventorySpecification {
  check(ctx: Record<string, unknown>): void {
    if (ctx.stockStatus === "blocked" || ctx.stockStatus === "quality_hold") {
      throw new DomainError("BusinessRule", "Cannot transact blocked inventory");
    }
  }
}

export class ClosedPeriodSpec implements InventorySpecification {
  constructor(private readonly isPeriodClosed: boolean) {}
  check(_ctx: Record<string, unknown>): void {
    if (this.isPeriodClosed) {
      throw new DomainError("BusinessRule", "Cannot post to closed inventory period");
    }
  }
}

export class SerialUniquenessSpec implements InventorySpecification {
  constructor(private readonly existingSerials: Set<string>) {}
  check(ctx: Record<string, unknown>): void {
    const serial = ctx.serialNumber as string;
    if (serial && this.existingSerials.has(serial)) {
      throw new DomainError("BusinessRule", `Serial number ${serial} already exists`);
    }
  }
}

export class LotRequiredSpec implements InventorySpecification {
  constructor(private readonly lotRequired: boolean) {}
  check(ctx: Record<string, unknown>): void {
    if (this.lotRequired && !ctx.lotId) {
      throw new DomainError("BusinessRule", "Lot-controlled items require lot assignment");
    }
  }
}
