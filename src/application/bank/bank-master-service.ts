import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { Bank, BankGroup, BankBranch, CorrespondentBank } from "../../domain/bank/bank-master.js";
import { BankGroupType, CorrespondentType } from "../../domain/bank/bank-enums.js";
import { PrismaBankGroupRepository, PrismaBankRepository, PrismaBankBranchRepository, PrismaCorrespondentBankRepository } from "../../infrastructure/bank/bank-prisma-repos.js";
import { BankGroupId, BankId, BankBranchId, CorrespondentBankId } from "../../domain/bank/bank-ids.js";

@Injectable()
export class BankMasterService {
  constructor(
    private readonly bankGroupRepo: PrismaBankGroupRepository,
    private readonly bankRepo: PrismaBankRepository,
    private readonly branchRepo: PrismaBankBranchRepository,
    private readonly correspondentRepo: PrismaCorrespondentBankRepository,
  ) {}

  // ─── Bank Group ──────────────────────────────────────────────────────────────

  async createGroup(p: { code: string; name: string; nameEn?: string; groupType: BankGroupType }): Promise<BankGroup> {
    const g = BankGroup.create(p);
    await this.bankGroupRepo.save(g);
    return g;
  }

  async getGroup(id: string): Promise<BankGroup | null> {
    return this.bankGroupRepo.findById(new BankGroupId(id));
  }

  async listGroups(): Promise<BankGroup[]> {
    return this.bankGroupRepo.findAll();
  }

  async deactivateGroup(id: string): Promise<BankGroup> {
    const g = await this.bankGroupRepo.findById(new BankGroupId(id));
    if (!g) throw new DomainError("NotFound", "Bank group not found");
    g.deactivate();
    await this.bankGroupRepo.save(g);
    return g;
  }

  // ─── Bank ────────────────────────────────────────────────────────────────────

  async createBank(p: {
    code: string; name: string; countryCode: string; nameEn?: string; shortName?: string;
    swiftCode?: string; routingNumber?: string; bankCode?: string; groupId?: string;
    address?: string; phone?: string; email?: string; website?: string;
  }): Promise<Bank> {
    const b = Bank.create(p);
    if (p.address) b.update({ address: p.address });
    if (p.phone) b.update({ phone: p.phone });
    if (p.email) b.update({ email: p.email });
    if (p.website) b.update({ website: p.website });
    await this.bankRepo.save(b);
    return b;
  }

  async getBank(id: string): Promise<Bank | null> {
    return this.bankRepo.findById(new BankId(id));
  }

  async getBankByCode(code: string): Promise<Bank | null> {
    return this.bankRepo.findByCode(code);
  }

  async listBanks(): Promise<Bank[]> {
    return this.bankRepo.findAll();
  }

  async updateBank(id: string, p: Partial<{ name: string; nameEn: string | null; swiftCode: string | null; routingNumber: string | null; address: string | null; phone: string | null; email: string | null; website: string | null; }>): Promise<Bank> {
    const b = await this.bankRepo.findById(new BankId(id));
    if (!b) throw new DomainError("NotFound", "Bank not found");
    b.update(p);
    await this.bankRepo.save(b);
    return b;
  }

  async deactivateBank(id: string): Promise<Bank> {
    const b = await this.bankRepo.findById(new BankId(id));
    if (!b) throw new DomainError("NotFound", "Bank not found");
    b.deactivate();
    await this.bankRepo.save(b);
    return b;
  }

  async activateBank(id: string): Promise<Bank> {
    const b = await this.bankRepo.findById(new BankId(id));
    if (!b) throw new DomainError("NotFound", "Bank not found");
    b.activate();
    await this.bankRepo.save(b);
    return b;
  }

  // ─── Bank Branch ─────────────────────────────────────────────────────────────

  async createBranch(p: { bankId: string; code: string; name: string; nameEn?: string; address?: string; phone?: string; email?: string; managerName?: string }): Promise<BankBranch> {
    const b = BankBranch.create(p);
    await this.branchRepo.save(b);
    return b;
  }

  async listBranches(bankId?: string): Promise<BankBranch[]> {
    if (bankId) return this.branchRepo.findByBank(bankId);
    return this.branchRepo.findAll();
  }

  async deactivateBranch(id: string): Promise<BankBranch> {
    const b = await this.branchRepo.findById(new BankBranchId(id));
    if (!b) throw new DomainError("NotFound", "Branch not found");
    b.deactivate();
    await this.branchRepo.save(b);
    return b;
  }

  // ─── Correspondent Bank ──────────────────────────────────────────────────────

  async createCorrespondent(p: { bankId: string; correspondentBankId: string; accountNumber?: string; correspondentType: CorrespondentType; currencyCode: string }): Promise<CorrespondentBank> {
    const c = CorrespondentBank.create(p);
    await this.correspondentRepo.save(c);
    return c;
  }

  async listCorrespondents(bankId?: string): Promise<CorrespondentBank[]> {
    if (bankId) return this.correspondentRepo.findByBank(bankId);
    return this.correspondentRepo.findAll();
  }
}
