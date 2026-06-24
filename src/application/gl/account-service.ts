import { DomainError } from "../../shared/domain-error.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { Account, AccountState } from "../../domain/gl/account.js";
import { AccountCategory, AccountNature } from "../../domain/gl/account-category.js";
import { AccountRepository, UnitOfWork } from "../../domain/gl/repositories.js";

export interface CreateAccountDTO {
  code: string;
  name: string;
  category: AccountCategory;
  nature: AccountNature;
  parentId?: string;
  currencyCode?: string;
  description?: string;
  isControl?: boolean;
  isPosting?: boolean;
}

export interface UpdateAccountDTO {
  name?: string;
  nameEn?: string;
  description?: string;
  isActive?: boolean;
}

export interface AccountTreeNode {
  id: string;
  code: string;
  name: string;
  category: AccountCategory;
  nature: AccountNature;
  balance: number;
  children: AccountTreeNode[];
}

export class AccountService {
  constructor(
    private readonly accountRepo: AccountRepository,
    private readonly uow: UnitOfWork,
  ) {}

  async create(dto: CreateAccountDTO): Promise<AccountState> {
    const existing = await this.accountRepo.findByCode(dto.code);
    if (existing) throw new DomainError("Conflict", `Account code ${dto.code} already exists`);

    if (dto.parentId) {
      const parent = await this.accountRepo.findById(new AccountId(dto.parentId));
      if (!parent) throw new DomainError("NotFound", `Parent account ${dto.parentId} not found`);
    }

    const account = Account.create(dto);
    await this.accountRepo.save(account);
    return account.toState();
  }

  async findById(id: string): Promise<AccountState> {
    const account = await this.accountRepo.findById(new AccountId(id));
    if (!account) throw new DomainError("NotFound", "Account not found");
    return account.toState();
  }

  async findByCode(code: string): Promise<AccountState | null> {
    const account = await this.accountRepo.findByCode(code);
    return account?.toState() ?? null;
  }

  async update(id: string, dto: UpdateAccountDTO): Promise<AccountState> {
    const account = await this.accountRepo.findById(new AccountId(id));
    if (!account) throw new DomainError("NotFound", "Account not found");

    account.modify(dto);
    await this.accountRepo.save(account);
    return account.toState();
  }

  async deactivate(id: string): Promise<void> {
    const account = await this.accountRepo.findById(new AccountId(id));
    if (!account) throw new DomainError("NotFound", "Account not found");

    const children = await this.accountRepo.findChildren(id);
    for (const child of children) {
      child.deactivate();
      await this.accountRepo.save(child);
    }

    account.deactivate();
    await this.accountRepo.save(account);
  }

  async delete(id: string): Promise<void> {
    const account = await this.accountRepo.findById(new AccountId(id));
    if (!account) throw new DomainError("NotFound", "Account not found");
    account.markDeleted();
    await this.accountRepo.save(account);
  }

  async findAll(): Promise<AccountState[]> {
    const accounts = await this.accountRepo.findAll();
    return accounts.map(a => a.toState());
  }

  async findActive(): Promise<AccountState[]> {
    const accounts = await this.accountRepo.findActive();
    return accounts.map(a => a.toState());
  }

  async getTree(): Promise<AccountTreeNode[]> {
    const all = await this.accountRepo.findAll();
    const map = new Map<string, AccountTreeNode>();
    const roots: AccountTreeNode[] = [];

    for (const a of all) {
      map.set(a.id.value, {
        id: a.id.value,
        code: a.code,
        name: a.name,
        category: a.category,
        nature: a.nature,
        balance: a.balance.toNumber(),
        children: [],
      });
    }

    for (const a of all) {
      const node = map.get(a.id.value)!;
      if (a.parentId && map.has(a.parentId)) {
        map.get(a.parentId)!.children.push(node);
      } else {
        roots.push(node);
      }
    }

    return roots;
  }

  async importChartOfAccounts(accounts: CreateAccountDTO[]): Promise<AccountState[]> {
    const results: AccountState[] = [];
    for (const dto of accounts) {
      results.push(await this.create(dto));
    }
    return results;
  }
}
