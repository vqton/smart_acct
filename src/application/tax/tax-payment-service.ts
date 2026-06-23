import { DomainError } from "../../shared/domain-error.js";
import { TaxPayment, TaxPaymentId, TaxPaymentStatus, TaxPaymentMethod } from "../../domain/tax/tax-payment.js";
import { TaxPaymentRepository } from "../../domain/tax/tax-repositories.js";

export class TaxPaymentService {
  constructor(private readonly repo: TaxPaymentRepository) {}

  async create(params: {
    taxReturnId: string; taxpayerId: string; taxTypeId: string;
    amount: number; paymentMethod: TaxPaymentMethod; paymentDate: Date;
    referenceNumber: string; paidById: string; description?: string;
  }): Promise<TaxPayment> {
    const payment = TaxPayment.create(params);
    await this.repo.save(payment);
    return payment;
  }

  async complete(id: string, confirmationCode?: string): Promise<TaxPayment> {
    const p = await this.repo.findById(new TaxPaymentId(id));
    if (!p) throw new DomainError("NotFound", "Payment not found");
    p.complete(confirmationCode);
    await this.repo.save(p);
    return p;
  }

  async fail(id: string, reason: string): Promise<TaxPayment> {
    const p = await this.repo.findById(new TaxPaymentId(id));
    if (!p) throw new DomainError("NotFound", "Payment not found");
    p.fail(reason);
    await this.repo.save(p);
    return p;
  }

  async refund(id: string, amount: number, reason: string): Promise<TaxPayment> {
    const p = await this.repo.findById(new TaxPaymentId(id));
    if (!p) throw new DomainError("NotFound", "Payment not found");
    p.refund(amount, reason);
    await this.repo.save(p);
    return p;
  }

  async findById(id: string): Promise<TaxPayment | null> {
    return this.repo.findById(new TaxPaymentId(id));
  }

  async findByTaxReturn(taxReturnId: string): Promise<TaxPayment[]> {
    return this.repo.findByTaxReturn(taxReturnId);
  }

  async findByTaxpayer(taxpayerId: string): Promise<TaxPayment[]> {
    return this.repo.findByTaxpayer(taxpayerId);
  }

  async findAll(): Promise<TaxPayment[]> {
    return this.repo.findAll();
  }
}
