import { AccountClass, AccountClassState } from "./account-class.js";
import { AccountType, AccountTypeState } from "./account-type.js";
import { AccountMapping, AccountMappingState } from "./account-mapping.js";
import { AccountExtension, AccountExtensionState } from "./account-extension.js";
import {
  AccountClassId, AccountTypeId, AccountMappingId, AccountExtensionId,
} from "./coa-ids.js";
import { AccountMappingStandard, AccountEffectiveStatus } from "./coa-enums.js";

export interface AccountClassRepository {
  save(entity: AccountClass): Promise<void>;
  findById(id: AccountClassId): Promise<AccountClass | null>;
  findByCode(code: string): Promise<AccountClass | null>;
  findAll(): Promise<AccountClass[]>;
  findActive(): Promise<AccountClass[]>;
}

export interface AccountTypeRepository {
  save(entity: AccountType): Promise<void>;
  findById(id: AccountTypeId): Promise<AccountType | null>;
  findByCode(code: string): Promise<AccountType | null>;
  findByClass(classId: string): Promise<AccountType[]>;
  findAll(): Promise<AccountType[]>;
  findActive(): Promise<AccountType[]>;
  findByCategory(category: string): Promise<AccountType[]>;
}

export interface AccountMappingRepository {
  save(entity: AccountMapping): Promise<void>;
  findById(id: AccountMappingId): Promise<AccountMapping | null>;
  findByAccount(accountId: string): Promise<AccountMapping[]>;
  findByStandard(standard: AccountMappingStandard): Promise<AccountMapping[]>;
  findByAccountAndStandard(accountId: string, standard: AccountMappingStandard): Promise<AccountMapping | null>;
  findActiveByAccount(accountId: string): Promise<AccountMapping[]>;
  findAll(): Promise<AccountMapping[]>;
  delete(id: AccountMappingId): Promise<void>;
}

export interface AccountExtensionRepository {
  save(entity: AccountExtension): Promise<void>;
  findByAccountId(accountId: string): Promise<AccountExtension | null>;
  findById(id: AccountExtensionId): Promise<AccountExtension | null>;
  findByType(typeId: string): Promise<AccountExtension[]>;
  findByStatus(status: AccountEffectiveStatus): Promise<AccountExtension[]>;
  findCashAccounts(): Promise<AccountExtension[]>;
  findBankAccounts(): Promise<AccountExtension[]>;
  findTaxAccounts(): Promise<AccountExtension[]>;
  findInventoryAccounts(): Promise<AccountExtension[]>;
}

export interface CoaUnitOfWork {
  begin(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  isActive(): boolean;
}
