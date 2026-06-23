import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { BankAccount, AuthorizedSigner, AccountLimit, AccountMapping } from "../../domain/bank/bank-account.js";
import { BankAccountCategory, BankAccountStatus, SignatureRule, AccountLimitType } from "../../domain/bank/bank-enums.js";
import { BankAccountId, AuthorizedSignerId, AccountLimitId } from "../../domain/bank/bank-ids.js";
import { ActiveAccountSpec, NonClosedAccountSpec } from "../../domain/bank/bank-specifications.js";
import {
  PrismaBankAccountRepository, PrismaAuthorizedSignerRepository,
  PrismaAccountLimitRepository, PrismaAccountMappingRepository,
} from "../../infrastructure/bank/bank-prisma-repos.js";

@Injectable()
export class BankAccountService {
  constructor(
    private readonly accountRepo: PrismaBankAccountRepository,
    private readonly signerRepo: PrismaAuthorizedSignerRepository,
    private readonly limitRepo: PrismaAccountLimitRepository,
    private readonly mappingRepo: PrismaAccountMappingRepository,
  ) {}

  async createAccount(p: {
    companyId: string; bankId: string; accountNumber: string; accountName: string;
    accountCategory?: BankAccountCategory; currencyCode?: string; branchId?: string | null;
    iban?: string | null; swiftCode?: string | null; glAccountId?: string | null;
    openingDate?: Date; notes?: string | null;
  }): Promise<BankAccount> {
    const a = BankAccount.create(p);
    await this.accountRepo.save(a);
    return a;
  }

  async getAccount(id: string): Promise<BankAccount | null> {
    return this.accountRepo.findById(BankAccountId.from(id));
  }

  async listAccounts(companyId?: string): Promise<BankAccount[]> {
    if (companyId) return this.accountRepo.findByCompany(companyId);
    return this.accountRepo.findAll();
  }

  async activateAccount(id: string): Promise<BankAccount> {
    const a = await this.getAccountOrThrow(id);
    a.activate();
    await this.accountRepo.save(a);
    return a;
  }

  async suspendAccount(id: string, reason: string): Promise<BankAccount> {
    const a = await this.getAccountOrThrow(id);
    a.suspend(reason);
    await this.accountRepo.save(a);
    return a;
  }

  async blockAccount(id: string, reason: string): Promise<BankAccount> {
    const a = await this.getAccountOrThrow(id);
    a.block(reason);
    await this.accountRepo.save(a);
    return a;
  }

  async closeAccount(id: string, force: boolean = false): Promise<BankAccount> {
    const a = await this.getAccountOrThrow(id);
    a.close(force);
    await this.accountRepo.save(a);
    return a;
  }

  async addSigner(accountId: string, p: {
    userId: string; name: string; title?: string; signatureRule?: SignatureRule;
    signingLimit?: number; currencyCode?: string;
  }): Promise<AuthorizedSigner> {
    const signer = AuthorizedSigner.create({ bankAccountId: accountId, ...p });
    await this.signerRepo.save(signer);
    return signer;
  }

  async listSigners(accountId: string): Promise<AuthorizedSigner[]> {
    return this.signerRepo.findByAccount(accountId);
  }

  async deactivateSigner(id: string): Promise<AuthorizedSigner> {
    const s = await this.signerRepo.findById(new AuthorizedSignerId(id));
    if (!s) throw new DomainError("NotFound", "Signer not found");
    s.deactivate();
    await this.signerRepo.save(s);
    return s;
  }

  async addLimit(accountId: string, p: {
    limitType: AccountLimitType; maxAmount?: number; minAmount?: number;
    currencyCode?: string; isEnforced?: boolean;
  }): Promise<AccountLimit> {
    const limit = AccountLimit.create({ bankAccountId: accountId, ...p });
    await this.limitRepo.save(limit);
    return limit;
  }

  async listLimits(accountId: string): Promise<AccountLimit[]> {
    return this.limitRepo.findByAccount(accountId);
  }

  async addMapping(accountId: string, p: {
    mappingType: string; glAccountId?: string; branchId?: string;
    costCenterId?: string; departmentId?: string; projectId?: string; isDefault?: boolean;
  }): Promise<AccountMapping> {
    const m = AccountMapping.create({ bankAccountId: accountId, ...p });
    await this.mappingRepo.save(m);
    return m;
  }

  private async getAccountOrThrow(id: string): Promise<BankAccount> {
    const a = await this.accountRepo.findById(BankAccountId.from(id));
    if (!a) throw new DomainError("NotFound", "Bank account not found");
    return a;
  }
}
