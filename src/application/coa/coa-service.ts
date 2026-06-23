import { DomainError } from "../../shared/domain-error.js";
import { AccountState } from "../../domain/gl/account.js";
import { AccountNature } from "../../domain/gl/account-category.js";
import { AccountClass } from "../../domain/coa/account-class.js";
import { AccountType } from "../../domain/coa/account-type.js";
import { AccountMapping } from "../../domain/coa/account-mapping.js";
import { AccountExtension } from "../../domain/coa/account-extension.js";
import { AccountClassId, AccountTypeId, AccountMappingId } from "../../domain/coa/coa-ids.js";
import {
  AccountClassRepository, AccountTypeRepository,
  AccountMappingRepository, AccountExtensionRepository,
} from "../../domain/coa/coa-repositories.js";
import { validateAccountCode, validateHierarchyCycle, validateAccountForPosting } from "../../domain/coa/coa-specifications.js";
import {
  AccountClassType, AccountTypeCategory, AccountSubType,
  AccountMappingStandard, AccountMappingType,
  AccountEffectiveStatus, AccountControlLevel, DimensionRequirement,
} from "../../domain/coa/coa-enums.js";

export interface CreateAccountClassDTO {
  code: string;
  name: string;
  classType: AccountClassType;
  displayOrder?: number;
  description?: string;
}

export interface CreateAccountTypeDTO {
  classId: string;
  code: string;
  name: string;
  category: AccountTypeCategory;
  nature: AccountNature;
  subType?: AccountSubType;
  description?: string;
  parentTypeId?: string;
}

export interface CreateAccountMappingDTO {
  accountId: string;
  mappingStandard: AccountMappingStandard;
  mappingType: AccountMappingType;
  targetCode: string;
  targetName?: string;
  mappingRule?: string;
  percentage?: number;
  effectiveFrom: Date;
  effectiveTo?: Date;
  description?: string;
}

export interface UpdateAccountExtensionDTO {
  typeId?: string;
  effectiveStatus?: AccountEffectiveStatus;
  effectiveFrom?: Date;
  effectiveTo?: Date;
  statusReason?: string;
  allowAutoPosting?: boolean;
  requireApproval?: boolean;
  budgetControlLevel?: AccountControlLevel;
  budgetCheckMessage?: string;
  defaultCostCenterId?: string;
  defaultDepartmentId?: string;
  defaultProjectId?: string;
  defaultBranchId?: string;
  costCenterRequired?: DimensionRequirement;
  departmentRequired?: DimensionRequirement;
  projectRequired?: DimensionRequirement;
  branchRequired?: DimensionRequirement;
  profitCenterRequired?: DimensionRequirement;
  isCashAccount?: boolean;
  isBankAccount?: boolean;
  isTaxAccount?: boolean;
  isInventoryAccount?: boolean;
  isReceivableAccount?: boolean;
  isPayableAccount?: boolean;
  isIntercompanyAccount?: boolean;
  defaultTaxCodeId?: string;
  defaultTaxRateId?: string;
  cashFlowCode?: string;
  financialStatementCode?: string;
  financialStatementNote?: string;
}

export interface AccountWithExtension {
  account: AccountState;
  extension: AccountExtension | null;
  mappings: AccountMapping[];
}

export interface AccountTreeNode {
  id: string;
  code: string;
  name: string;
  category: string;
  nature: string;
  balance: number;
  type: { id: string; code: string; name: string } | null;
  status: string;
  children: AccountTreeNode[];
}

export class CoaService {
  constructor(
    private readonly classRepo: AccountClassRepository,
    private readonly typeRepo: AccountTypeRepository,
    private readonly mappingRepo: AccountMappingRepository,
    private readonly extRepo: AccountExtensionRepository,
  ) {}

  // ─── Account Classes ──────────────────────────────────────────────────

  async createClass(dto: CreateAccountClassDTO) {
    const existing = await this.classRepo.findByCode(dto.code);
    if (existing) throw new DomainError("Conflict", `Account class ${dto.code} already exists`);
    const entity = AccountClass.create(dto);
    await this.classRepo.save(entity);
    return entity.toState();
  }

  async getClass(id: string) {
    const entity = await this.classRepo.findById(new AccountClassId(id));
    if (!entity) throw new DomainError("NotFound", "Account class not found");
    return entity.toState();
  }

  async getAllClasses() {
    const entities = await this.classRepo.findAll();
    return entities.map(e => e.toState());
  }

  // ─── Account Types ────────────────────────────────────────────────────

  async createType(dto: CreateAccountTypeDTO) {
    const existing = await this.typeRepo.findByCode(dto.code);
    if (existing) throw new DomainError("Conflict", `Account type ${dto.code} already exists`);
    const entity = AccountType.create(dto);
    await this.typeRepo.save(entity);
    return entity.toState();
  }

  async getType(id: string) {
    const entity = await this.typeRepo.findById(new AccountTypeId(id));
    if (!entity) throw new DomainError("NotFound", "Account type not found");
    return entity.toState();
  }

  async getTypesByClass(classId: string) {
    const entities = await this.typeRepo.findByClass(classId);
    return entities.map(e => e.toState());
  }

  async getAllTypes() {
    const entities = await this.typeRepo.findAll();
    return entities.map(e => e.toState());
  }

  // ─── Account Mappings ─────────────────────────────────────────────────

  async createMapping(dto: CreateAccountMappingDTO) {
    const entity = AccountMapping.create(dto);
    await this.mappingRepo.save(entity);
    return entity.toState();
  }

  async getMappingsByAccount(accountId: string) {
    const entities = await this.mappingRepo.findByAccount(accountId);
    return entities.map(e => e.toState());
  }

  async getMappingsByStandard(standard: AccountMappingStandard) {
    const entities = await this.mappingRepo.findByStandard(standard);
    return entities.map(e => e.toState());
  }

  async deleteMapping(id: string) {
    const entity = await this.mappingRepo.findById(new AccountMappingId(id));
    if (!entity) throw new DomainError("NotFound", "Account mapping not found");
    entity.deactivate();
    await this.mappingRepo.save(entity);
  }

  // ─── Account Extensions ───────────────────────────────────────────────

  async getOrCreateExtension(accountId: string) {
    let ext = await this.extRepo.findByAccountId(accountId);
    if (!ext) {
      ext = AccountExtension.create(accountId);
      await this.extRepo.save(ext);
    }
    return ext;
  }

  async updateExtension(accountId: string, dto: UpdateAccountExtensionDTO) {
    const ext = await this.extRepo.findByAccountId(accountId);
    if (!ext) throw new DomainError("NotFound", "Account extension not found");
    ext.modify(dto as any);
    await this.extRepo.save(ext);
    return ext.toState();
  }

  async getExtension(accountId: string) {
    const ext = await this.extRepo.findByAccountId(accountId);
    return ext?.toState() ?? null;
  }

  // ─── Account Validation ───────────────────────────────────────────────

  async validateAccountForPosting(accountId: string, accountState: AccountState): Promise<void> {
    const ext = await this.extRepo.findByAccountId(accountId);
    validateAccountForPosting(accountState, ext?.toState() ?? null);
  }

  // ─── Account Hierarchy ────────────────────────────────────────────────

  buildTree(
    accounts: AccountState[],
    extensions: Map<string, AccountExtension>,
    types: Map<string, { code: string; name: string }>,
  ): AccountTreeNode[] {
    const map = new Map<string, AccountTreeNode>();
    const roots: AccountTreeNode[] = [];

    for (const a of accounts) {
      const ext = extensions.get(a.id);
      const t = ext?.typeId ? types.get(ext.typeId) : undefined;
      map.set(a.id, {
        id: a.id,
        code: a.code,
        name: a.name,
        category: a.category,
        nature: a.nature,
        balance: a.balance,
        type: t ? { id: ext!.typeId!, code: t.code, name: t.name } : null,
        status: ext?.toState().effectiveStatus ?? AccountEffectiveStatus.Active,
        children: [],
      });
    }

    for (const a of accounts) {
      const node = map.get(a.id)!;
      if (a.parentId && map.has(a.parentId)) {
        map.get(a.parentId)!.children.push(node);
      } else {
        roots.push(node);
      }
    }

    return roots;
  }

  validateAccountCode(code: string): void {
    validateAccountCode(code);
  }

  validateHierarchy(accountId: string, newParentId: string, allAccounts: AccountState[]): void {
    validateHierarchyCycle(accountId, newParentId, allAccounts);
  }
}
