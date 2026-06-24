import { DomainError } from "../../shared/domain-error.js";
import { FaAssetStatus } from "./fa-enums.js";

export interface FaSpecification {
  check(context: Record<string, unknown>): void;
}

export class AssetMustBeCapitalized implements FaSpecification {
  check(ctx: Record<string, unknown>): void {
    const status = ctx.status as FaAssetStatus;
    if (status !== FaAssetStatus.Capitalized && status !== FaAssetStatus.InUse) {
      throw new DomainError("BusinessRule", "Asset must be capitalized or in use");
    }
  }
}

export class AssetMustNotBeDisposed implements FaSpecification {
  check(ctx: Record<string, unknown>): void {
    const status = ctx.status as FaAssetStatus;
    if (
      status === FaAssetStatus.Disposed ||
      status === FaAssetStatus.Retired ||
      status === FaAssetStatus.Sold ||
      status === FaAssetStatus.Scrapped ||
      status === FaAssetStatus.Donated ||
      status === FaAssetStatus.WrittenOff ||
      status === FaAssetStatus.Decommissioned ||
      status === FaAssetStatus.Archived
    ) {
      throw new DomainError("BusinessRule", "Asset has been disposed and cannot be modified");
    }
  }
}

export class AssetMustNotBeFullyDepreciated implements FaSpecification {
  check(ctx: Record<string, unknown>): void {
    if (ctx.isFullyDepreciated) {
      throw new DomainError("BusinessRule", "Asset is fully depreciated");
    }
  }
}

export class AssetMustHavePositiveValue implements FaSpecification {
  check(ctx: Record<string, unknown>): void {
    const originalCost = ctx.originalCost as number;
    if (!originalCost || originalCost <= 0) {
      throw new DomainError("BusinessRule", "Asset original cost must be positive");
    }
  }
}

export class DepreciationStartDateMustBeSet implements FaSpecification {
  check(ctx: Record<string, unknown>): void {
    if (!ctx.depreciationStartDate) {
      throw new DomainError("BusinessRule", "Depreciation start date must be set");
    }
  }
}

export class UsefulLifeMustBePositive implements FaSpecification {
  check(ctx: Record<string, unknown>): void {
    const totalMonths = (ctx.usefulLifeYears as number) * 12 + (ctx.usefulLifeMonths as number);
    if (totalMonths <= 0) {
      throw new DomainError("BusinessRule", "Useful life must be positive");
    }
  }
}

export class DisposalMustBeAfterAcquisition implements FaSpecification {
  check(ctx: Record<string, unknown>): void {
    const disposalDate = ctx.disposalDate as Date;
    const acquisitionDate = ctx.acquisitionDate as Date;
    if (disposalDate < acquisitionDate) {
      throw new DomainError("BusinessRule", "Disposal date cannot be before acquisition date");
    }
  }
}

export class LeaseEndMustBeAfterStart implements FaSpecification {
  check(ctx: Record<string, unknown>): void {
    const start = ctx.startDate as Date;
    const end = ctx.endDate as Date;
    if (end <= start) {
      throw new DomainError("BusinessRule", "Lease end date must be after start date");
    }
  }
}

export class VerificationMustHaveAssets implements FaSpecification {
  check(ctx: Record<string, unknown>): void {
    const count = ctx.assetCount as number;
    if (!count || count <= 0) {
      throw new DomainError("BusinessRule", "Verification must have at least one asset");
    }
  }
}
