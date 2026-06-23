import { TaxReturn, TaxReturnId, TaxReturnStatus, TaxReturnType, TaxLineItem } from "../../domain/tax/tax-return.js";
import { TaxReturnRepository } from "../../domain/tax/tax-repositories.js";

export class TaxReturnService {
  constructor(private readonly repo: TaxReturnRepository) {}

  async createDraft(params: {
    returnNumber: string; taxTypeId: string; taxpayerId: string; taxAuthorityId: string;
    periodId: string; fiscalYearId: string; returnType: TaxReturnType;
    filingDate: Date; dueDate: Date; createdById: string;
  }): Promise<TaxReturn> {
    const existing = await this.repo.findByReturnNumber(params.returnNumber);
    if (existing) throw new Error(`Return number ${params.returnNumber} already exists`);

    const tr = TaxReturn.create(params);
    await this.repo.save(tr);
    return tr;
  }

  async addLine(returnId: string, line: Omit<TaxLineItem, "id" | "lineOrder">): Promise<TaxReturn> {
    const tr = await this.repo.findById(new TaxReturnId(returnId));
    if (!tr) throw new Error(`Tax return ${returnId} not found`);
    tr.addLine(line);
    await this.repo.save(tr);
    return tr;
  }

  async submit(returnId: string): Promise<TaxReturn> {
    const tr = await this.repo.findById(new TaxReturnId(returnId));
    if (!tr) throw new Error(`Tax return ${returnId} not found`);
    tr.submit();
    await this.repo.save(tr);
    return tr;
  }

  async accept(returnId: string): Promise<TaxReturn> {
    const tr = await this.repo.findById(new TaxReturnId(returnId));
    if (!tr) throw new Error(`Tax return ${returnId} not found`);
    tr.accept();
    await this.repo.save(tr);
    return tr;
  }

  async reject(returnId: string, reason: string): Promise<TaxReturn> {
    const tr = await this.repo.findById(new TaxReturnId(returnId));
    if (!tr) throw new Error(`Tax return ${returnId} not found`);
    tr.reject(reason);
    await this.repo.save(tr);
    return tr;
  }

  async getById(returnId: string): Promise<TaxReturn | null> {
    return this.repo.findById(new TaxReturnId(returnId));
  }

  async findByTaxpayer(taxpayerId: string): Promise<TaxReturn[]> {
    return this.repo.findByTaxpayer(taxpayerId);
  }

  async findByPeriod(periodId: string): Promise<TaxReturn[]> {
    return this.repo.findByPeriod(periodId);
  }

  async findPending(): Promise<TaxReturn[]> {
    return this.repo.findPending();
  }

  async findAll(): Promise<TaxReturn[]> {
    return this.repo.findAll();
  }
}
