import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { ReceivableAccountId, CustomerId, SalesInvoiceId, CustomerReceiptId } from "../../domain/sales/sales-ids.js";
import { ReceivableAccount, type ReceivableAccountState } from "../../domain/sales/sales-receivable.js";
import { PrismaReceivableAccountRepository, PrismaCustomerReceiptRepository, PrismaSalesInvoiceRepository, PrismaCustomerRepository } from "../../infrastructure/sales/sales-prisma-repos.js";

@Injectable()
export class ReceivableService {
  constructor(
    private readonly recvRepo: PrismaReceivableAccountRepository,
    private readonly receiptRepo: PrismaCustomerReceiptRepository,
    private readonly invRepo: PrismaSalesInvoiceRepository,
    private readonly custRepo: PrismaCustomerRepository,
  ) {}

  async createReceivable(customerId: string, invoiceId: string, invoiceNumber: string, companyId: string, amount: number, dueDate: Date, branchId?: string): Promise<ReceivableAccount> {
    const ar = ReceivableAccount.create(customerId, invoiceId, invoiceNumber, companyId, amount, dueDate, branchId);
    await this.recvRepo.save(ar);
    return ar;
  }

  async recordPayment(invoiceId: string, amount: number, paymentDate: Date): Promise<ReceivableAccount> {
    const accounts = await this.recvRepo.findByInvoiceId(invoiceId);
    if (accounts.length === 0) throw new DomainError("NotFound", "Receivable account not found");
    const ar = await this.recvRepo.findById(ReceivableAccountId.from(accounts[0].id));
    if (!ar) throw new DomainError("NotFound", "Receivable account not found");
    ar.recordPayment(amount, paymentDate);
    await this.recvRepo.save(ar);
    const invoice = await this.invRepo.findById(SalesInvoiceId.from(invoiceId));
    if (invoice) {
      invoice.recordPayment(amount);
      await this.invRepo.save(invoice);
    }
    const customer = await this.custRepo.findById(CustomerId.from(ar["_customerId"]));
    if (customer) {
      customer.recordPayment(amount);
      await this.custRepo.save(customer);
    }
    return ar;
  }

  async writeOff(id: string, amount: number, reason: string, approvedBy: string): Promise<ReceivableAccount> {
    const ar = await this.recvRepo.findById(ReceivableAccountId.from(id));
    if (!ar) throw new DomainError("NotFound", "Receivable account not found");
    ar.writeOff(amount, reason, approvedBy);
    await this.recvRepo.save(ar);
    return ar;
  }

  async findByCustomer(customerId: string): Promise<ReceivableAccountState[]> {
    return this.recvRepo.findByCustomerId(customerId);
  }

  async findOverdue(): Promise<ReceivableAccountState[]> {
    return this.recvRepo.findOverdue();
  }

  async findByAgingBucket(bucket: string): Promise<ReceivableAccountState[]> {
    return this.recvRepo.findByAgingBucket(bucket);
  }

  async markDisputed(id: string): Promise<ReceivableAccount> {
    const ar = await this.recvRepo.findById(ReceivableAccountId.from(id));
    if (!ar) throw new DomainError("NotFound", "Receivable account not found");
    ar.markDisputed();
    await this.recvRepo.save(ar);
    return ar;
  }

  async recordDunning(id: string, level: number): Promise<ReceivableAccount> {
    const ar = await this.recvRepo.findById(ReceivableAccountId.from(id));
    if (!ar) throw new DomainError("NotFound", "Receivable account not found");
    ar.recordDunning(level);
    await this.recvRepo.save(ar);
    return ar;
  }
}
