import { CustomerId, QuotationId, SalesOrderId, DeliveryOrderId, SalesInvoiceId, SalesReturnId, CustomerReceiptId, ReceivableAccountId, PromotionId, GiftCardId, LoyaltyAccountId, PriceListId } from "./sales-ids.js";
import { Customer, CustomerState } from "./sales-customer.js";
import { Quotation, QuotationLine, QuotationState } from "./sales-quotation.js";
import { SalesOrder, OrderLine, SalesOrderState } from "./sales-order.js";
import { DeliveryOrder, DeliveryLine, DeliveryOrderState } from "./sales-delivery.js";
import { SalesInvoice, InvoiceLine, SalesInvoiceState } from "./sales-invoice.js";
import { SalesReturn, ReturnLine, SalesReturnState } from "./sales-return.js";
import { CustomerReceipt, ReceiptAllocation, CustomerReceiptState } from "./sales-payment.js";
import { ReceivableAccount, ReceivableAccountState } from "./sales-receivable.js";

export interface CustomerRepository {
  save(customer: Customer): Promise<void>;
  findById(id: CustomerId): Promise<Customer | null>;
  findByCode(code: string): Promise<Customer | null>;
  findByTaxCode(taxCode: string): Promise<Customer | null>;
  findAll(): Promise<CustomerState[]>;
  search(criteria: Partial<{ code: string; name: string; taxCode: string; status: string; phone: string; email: string }>): Promise<CustomerState[]>;
}

export interface QuotationRepository {
  save(q: Quotation): Promise<void>;
  findById(id: QuotationId): Promise<Quotation | null>;
  findByQuotationNumber(number: string): Promise<Quotation | null>;
  findByCustomerId(customerId: string): Promise<QuotationState[]>;
  findOpen(): Promise<QuotationState[]>;
  findExpired(): Promise<QuotationState[]>;
  saveLine(line: QuotationLine): Promise<void>;
}

export interface SalesOrderRepository {
  save(order: SalesOrder): Promise<void>;
  findById(id: SalesOrderId): Promise<SalesOrder | null>;
  findByOrderNumber(orderNumber: string): Promise<SalesOrder | null>;
  findByCustomerId(customerId: string): Promise<SalesOrderState[]>;
  findByStatus(status: string): Promise<SalesOrderState[]>;
  findOpen(): Promise<SalesOrderState[]>;
  findByStoreId(storeId: string): Promise<SalesOrderState[]>;
  findBySalespersonId(salespersonId: string): Promise<SalesOrderState[]>;
  findByDateRange(from: Date, to: Date): Promise<SalesOrderState[]>;
  findBySourceDocument(sourceType: string, sourceId: string): Promise<SalesOrderState[]>;
  saveLine(line: OrderLine): Promise<void>;
}

export interface DeliveryOrderRepository {
  save(delivery: DeliveryOrder): Promise<void>;
  findById(id: DeliveryOrderId): Promise<DeliveryOrder | null>;
  findByDeliveryNumber(number: string): Promise<DeliveryOrder | null>;
  findByOrderId(orderId: string): Promise<DeliveryOrderState[]>;
  findByStatus(status: string): Promise<DeliveryOrderState[]>;
  saveLine(line: DeliveryLine): Promise<void>;
}

export interface SalesInvoiceRepository {
  save(invoice: SalesInvoice): Promise<void>;
  findById(id: SalesInvoiceId): Promise<SalesInvoice | null>;
  findByInvoiceNumber(invoiceNumber: string): Promise<SalesInvoice | null>;
  findByCustomerId(customerId: string): Promise<SalesInvoiceState[]>;
  findByOrderId(orderId: string): Promise<SalesInvoiceState[]>;
  findByStatus(status: string): Promise<SalesInvoiceState[]>;
  findPending(): Promise<SalesInvoiceState[]>;
  saveLine(line: InvoiceLine): Promise<void>;
}

export interface SalesReturnRepository {
  save(ret: SalesReturn): Promise<void>;
  findById(id: SalesReturnId): Promise<SalesReturn | null>;
  findByReturnNumber(returnNumber: string): Promise<SalesReturn | null>;
  findByCustomerId(customerId: string): Promise<SalesReturnState[]>;
  findByOrderId(orderId: string): Promise<SalesReturnState[]>;
  findByInvoiceId(invoiceId: string): Promise<SalesReturnState[]>;
  findByStatus(status: string): Promise<SalesReturnState[]>;
  saveLine(line: ReturnLine): Promise<void>;
}

export interface CustomerReceiptRepository {
  save(receipt: CustomerReceipt): Promise<void>;
  findById(id: CustomerReceiptId): Promise<CustomerReceipt | null>;
  findByReceiptNumber(number: string): Promise<CustomerReceipt | null>;
  findByCustomerId(customerId: string): Promise<CustomerReceiptState[]>;
  findByInvoiceId(invoiceId: string): Promise<CustomerReceiptState[]>;
  findByDateRange(from: Date, to: Date): Promise<CustomerReceiptState[]>;
  saveAllocation(allocation: ReceiptAllocation): Promise<void>;
}

export interface ReceivableAccountRepository {
  save(account: ReceivableAccount): Promise<void>;
  findById(id: ReceivableAccountId): Promise<ReceivableAccount | null>;
  findByCustomerId(customerId: string): Promise<ReceivableAccountState[]>;
  findByInvoiceId(invoiceId: string): Promise<ReceivableAccountState[]>;
  findOverdue(): Promise<ReceivableAccountState[]>;
  findByAgingBucket(bucket: string): Promise<ReceivableAccountState[]>;
}

export interface SalesUnitOfWork {
  begin(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  getCustomerRepo(): CustomerRepository;
  getQuotationRepo(): QuotationRepository;
  getOrderRepo(): SalesOrderRepository;
  getDeliveryRepo(): DeliveryOrderRepository;
  getInvoiceRepo(): SalesInvoiceRepository;
  getReturnRepo(): SalesReturnRepository;
  getReceiptRepo(): CustomerReceiptRepository;
  getReceivableRepo(): ReceivableAccountRepository;
}
