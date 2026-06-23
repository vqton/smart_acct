import { DomainError } from "../../shared/domain-error.js";
import { AccountState } from "../gl/account.js";
import { AccountExtensionState } from "./account-extension.js";
import { AccountEffectiveStatus, DimensionRequirement } from "./coa-enums.js";

export interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
  check(candidate: T): void;
}

export class PostingAccountSpec implements Specification<AccountState> {
  isSatisfiedBy(a: AccountState): boolean {
    return a.isActive && a.isPosting && !a.deletedAt;
  }

  check(a: AccountState): void {
    if (!a.isActive) throw new DomainError("BusinessRule", `Account ${a.code} is inactive`);
    if (!a.isPosting) throw new DomainError("BusinessRule", `Account ${a.code} is not a posting account`);
    if (a.deletedAt) throw new DomainError("BusinessRule", `Account ${a.code} is deleted`);
  }
}

export class ManualEntryAllowedSpec implements Specification<AccountState> {
  isSatisfiedBy(a: AccountState): boolean {
    return a.allowManualEntry && a.isPosting && a.isActive;
  }

  check(a: AccountState): void {
    if (!a.allowManualEntry) throw new DomainError("BusinessRule", `Account ${a.code} does not allow manual entry`);
    if (!a.isPosting) throw new DomainError("BusinessRule", `Account ${a.code} is not a posting account`);
    if (!a.isActive) throw new DomainError("BusinessRule", `Account ${a.code} is inactive`);
  }
}

export class AutoPostingAllowedSpec implements Specification<AccountExtensionState> {
  isSatisfiedBy(e: AccountExtensionState): boolean {
    return e.allowAutoPosting;
  }

  check(e: AccountExtensionState): void {
    if (!e.allowAutoPosting) throw new DomainError("BusinessRule", "Account does not allow auto-posting");
  }
}

export class ActiveStatusSpec implements Specification<AccountExtensionState> {
  isSatisfiedBy(e: AccountExtensionState): boolean {
    return e.effectiveStatus === AccountEffectiveStatus.Active;
  }

  check(e: AccountExtensionState): void {
    if (e.effectiveStatus === AccountEffectiveStatus.Draft) {
      throw new DomainError("BusinessRule", "Account is in draft status");
    }
    if (e.effectiveStatus === AccountEffectiveStatus.Suspended) {
      throw new DomainError("BusinessRule", `Account is suspended: ${e.statusReason ?? ""}`);
    }
    if (e.effectiveStatus === AccountEffectiveStatus.Closed) {
      throw new DomainError("BusinessRule", "Account is closed");
    }
    if (e.effectiveStatus === AccountEffectiveStatus.Archived) {
      throw new DomainError("BusinessRule", "Account is archived");
    }
  }
}

export class EffectiveDateSpec implements Specification<AccountExtensionState> {
  isSatisfiedBy(e: AccountExtensionState): boolean {
    const now = new Date();
    if (e.effectiveFrom && e.effectiveFrom > now) return false;
    if (e.effectiveTo && e.effectiveTo < now) return false;
    return true;
  }

  check(e: AccountExtensionState): void {
    const now = new Date();
    if (e.effectiveFrom && e.effectiveFrom > now) {
      throw new DomainError("BusinessRule", `Account not yet effective. Effective from: ${e.effectiveFrom.toISOString()}`);
    }
    if (e.effectiveTo && e.effectiveTo < now) {
      throw new DomainError("BusinessRule", `Account expired on ${e.effectiveTo.toISOString()}`);
    }
  }
}

export class UniqueCodeSpec {
  async check(code: string, existingCode: string | null, repo: {
    findByCode(code: string): Promise<{ id: string } | null>;
  }, excludeId?: string): Promise<void> {
    if (existingCode && existingCode !== code) {
      if (existingCode) {
        const dup = await repo.findByCode(code);
        if (dup && (!excludeId || dup.id !== excludeId)) {
          throw new DomainError("Conflict", `Account code ${code} already exists`);
        }
      }
    }
  }
}

export class ParentExistsSpec {
  async check(parentId: string | null | undefined, repo: {
    findById(id: { value: string }): Promise<{ code: string } | null>;
  }): Promise<void> {
    if (!parentId) return;
    const parent = await repo.findById({ value: parentId } as any);
    if (!parent) throw new DomainError("NotFound", `Parent account ${parentId} not found`);
  }
}

export function hasRequiredDimension(
  requirement: DimensionRequirement,
  value: string | null | undefined,
): void {
  if (requirement === DimensionRequirement.Required && !value) {
    throw new DomainError("Validation", "Required dimension is missing");
  }
}

export function validateAccountForPosting(
  account: AccountState,
  extension: AccountExtensionState | null,
): void {
  new PostingAccountSpec().check(account);
  if (extension) {
    new AutoPostingAllowedSpec().check(extension);
    new ActiveStatusSpec().check(extension);
    new EffectiveDateSpec().check(extension);

    if (extension.costCenterRequired === DimensionRequirement.Required) {
      throw new DomainError("Validation", `Cost center is required for account ${account.code}`);
    }
    if (extension.departmentRequired === DimensionRequirement.Required) {
      throw new DomainError("Validation", `Department is required for account ${account.code}`);
    }
  }
}

export function validateAccountCode(code: string): void {
  if (!/^\d{1,7}$/.test(code)) {
    throw new DomainError("Validation", `Invalid account code format: ${code}. Must be 1-7 digits`);
  }
}

export function validateHierarchyCycle(
  accountId: string,
  newParentId: string,
  allAccounts: AccountState[],
): void {
  if (accountId === newParentId) {
    throw new DomainError("BusinessRule", "Account cannot be its own parent");
  }
  const idSet = new Set<string>([accountId]);
  let current = newParentId;
  const lookup = new Map(allAccounts.map(a => [a.id, a]));
  while (current) {
    if (idSet.has(current)) {
      throw new DomainError("BusinessRule", "Circular hierarchy detected");
    }
    idSet.add(current);
    const parent = lookup.get(current);
    current = parent?.parentId ?? "";
  }
}
