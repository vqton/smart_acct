import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { CustomerReceiptId, SalesInvoiceId, SalesOrderId, CustomerId, SalesReturnId } from "../../domain/sales/sales-ids.js";
import { CustomerReceipt, ReceiptAllocation, type CustomerReceiptState } from "../../domain/sales/sales-payment.js";
import { SlsPaymentMethod, SlsPaymentStatus } from "../../domain/sales/sales-enums.js";
import { PrismaCustomerReceiptRepository, PrismaSalesInvoiceRepository, PrismaSalesOrderRepository, PrismaCustomerRepository, PrismaSalesReturnRepository } from "../../infrastructure/sales/sales-prisma-repos.js";
import { ReceivableService } from "./sales-receivable-service.js";
import { SalesGlService } from "./sales-gl-service.js";

@Injectable()
export class SalesPaymentService {
  constructor(
    private readonly receiptRepo: PrismaCustomerReceiptRepository,
    private readonly invRepo: PrismaSalesInvoiceRepository,
    private readonly orderRepo: PrismaSalesOrderRepository,
    private readonly custRepo: PrismaCustomerRepository,
    private readonly retRepo: PrismaSalesReturnRepository,
    private readonly receivableService: ReceivableService,
    private readonly glService: SalesGlService,
  ) {}

  async createReceipt(p: {
    receiptNumber: string; companyId: string; customerId: string; customerName: string;
    amount: number; paymentMethod: SlsPaymentMethod;
    branchId?: string; orderId?: string; orderNumber?: string;
    invoiceId?: string; invoiceNumber?: string;
    returnId?: string; returnNumber?: string;
    paymentDate?: Date; currencyCode?: string; exchangeRate?: number;
    paymentRef?: string; isSplitPayment?: boolean; splitCount?: number;
    notes?: string;
  }): Promise<CustomerReceipt> {
    const existing = await this.receiptRepo.findByReceiptNumber(p.receiptNumber);
    if (existing) throw new DomainError("Conflict", `Receipt ${p.receiptNumber} already exists`);
    const receipt = CustomerReceipt.create(p);
    await this.receiptRepo.save(receipt);
    return receipt;
  }

  async approveAndAllocate(id: string, approvedBy: string, allocateToInvoiceId?: string): Promise<CustomerReceipt> {
    const receipt = await this.getReceipt(id);
    receipt.approve(approvedBy);
    if (allocateToInvoiceId) {
      const invoice = await this.invRepo.findById(SalesInvoiceId.from(allocateToInvoiceId));
      if (!invoice) throw new DomainError("NotFound", "Invoice not found");
      const allocation = ReceiptAllocation.create(receipt.id.value, allocateToInvoiceId, invoice["_invoiceNumber"], receipt["_amount"]);
      receipt.addAllocation(allocation);
      await this.receiptRepo.saveAllocation(allocation);
      invoice.recordPayment(receipt["_amount"]);
      await this.invRepo.save(invoice);
      await this.receivableService.recordPayment(allocateToInvoiceId, receipt["_amount"], receipt["_paymentDate"]);
      if (receipt["_orderId"]) {
        const order = await this.orderRepo.findById(SalesOrderId.from(receipt["_orderId"]));
        if (order) {
          order.recordPayment(receipt["_amount"]);
          await this.orderRepo.save(order);
        }
      }
      await this.glService.postReceiptGl(receipt, approvedBy).catch((err) => {
        throw new DomainError("Infrastructure", `GL posting failed: ${err.message}`);
      });
    }
    await this.receiptRepo.save(receipt);
    return receipt;
  }

  async getReceipt(id: string): Promise<CustomerReceipt> {
    const r = await this.receiptRepo.findById(CustomerReceiptId.from(id));
    if (!r) throw new DomainError("NotFound", "Receipt not found");
    return r;
  }

  async findByCustomer(customerId: string): Promise<CustomerReceiptState[]> {
    return this.receiptRepo.findByCustomerId(customerId);
  }

  async findByInvoice(invoiceId: string): Promise<CustomerReceiptState[]> {
    return this.receiptRepo.findByInvoiceId(invoiceId);
  }

  async findByDateRange(from: Date, to: Date): Promise<CustomerReceiptState[]> {
    return this.receiptRepo.findByDateRange(from, to);
  }
}
