import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class CustomerId extends Identifier { static new(): CustomerId { return new CustomerId(IdGenerator.uuid()); } static from(id: string): CustomerId { return new CustomerId(id); } }
export class CustomerGroupId extends Identifier { static new(): CustomerGroupId { return new CustomerGroupId(IdGenerator.uuid()); } }
export class CustomerContactId extends Identifier { static new(): CustomerContactId { return new CustomerContactId(IdGenerator.uuid()); } }
export class CustomerAddressId extends Identifier { static new(): CustomerAddressId { return new CustomerAddressId(IdGenerator.uuid()); } }
export class CustomerTaxInfoId extends Identifier { static new(): CustomerTaxInfoId { return new CustomerTaxInfoId(IdGenerator.uuid()); } }
export class CustomerWalletId extends Identifier { static new(): CustomerWalletId { return new CustomerWalletId(IdGenerator.uuid()); } }
export class WalletTransactionId extends Identifier { static new(): WalletTransactionId { return new WalletTransactionId(IdGenerator.uuid()); } }
export class StoreId extends Identifier { static new(): StoreId { return new StoreId(IdGenerator.uuid()); } }
export class SalespersonId extends Identifier { static new(): SalespersonId { return new SalespersonId(IdGenerator.uuid()); } }
export class PriceListId extends Identifier { static new(): PriceListId { return new PriceListId(IdGenerator.uuid()); } }
export class PriceListItemId extends Identifier { static new(): PriceListItemId { return new PriceListItemId(IdGenerator.uuid()); } }
export class PromotionId extends Identifier { static new(): PromotionId { return new PromotionId(IdGenerator.uuid()); } }
export class CouponId extends Identifier { static new(): CouponId { return new CouponId(IdGenerator.uuid()); } }
export class GiftCardId extends Identifier { static new(): GiftCardId { return new GiftCardId(IdGenerator.uuid()); } }
export class GiftCardTransactionId extends Identifier { static new(): GiftCardTransactionId { return new GiftCardTransactionId(IdGenerator.uuid()); } }
export class LoyaltyAccountId extends Identifier { static new(): LoyaltyAccountId { return new LoyaltyAccountId(IdGenerator.uuid()); } }
export class LoyaltyTransactionId extends Identifier { static new(): LoyaltyTransactionId { return new LoyaltyTransactionId(IdGenerator.uuid()); } }
export class MembershipId extends Identifier { static new(): MembershipId { return new MembershipId(IdGenerator.uuid()); } }
export class QuotationId extends Identifier { static new(): QuotationId { return new QuotationId(IdGenerator.uuid()); } static from(id: string): QuotationId { return new QuotationId(id); } }
export class QuotationLineId extends Identifier { static new(): QuotationLineId { return new QuotationLineId(IdGenerator.uuid()); } }
export class SalesOrderId extends Identifier { static new(): SalesOrderId { return new SalesOrderId(IdGenerator.uuid()); } static from(id: string): SalesOrderId { return new SalesOrderId(id); } }
export class OrderLineId extends Identifier { static new(): OrderLineId { return new OrderLineId(IdGenerator.uuid()); } }
export class InventoryReservationId extends Identifier { static new(): InventoryReservationId { return new InventoryReservationId(IdGenerator.uuid()); } }
export class DeliveryOrderId extends Identifier { static new(): DeliveryOrderId { return new DeliveryOrderId(IdGenerator.uuid()); } static from(id: string): DeliveryOrderId { return new DeliveryOrderId(id); } }
export class DeliveryLineId extends Identifier { static new(): DeliveryLineId { return new DeliveryLineId(IdGenerator.uuid()); } }
export class SalesInvoiceId extends Identifier { static new(): SalesInvoiceId { return new SalesInvoiceId(IdGenerator.uuid()); } static from(id: string): SalesInvoiceId { return new SalesInvoiceId(id); } }
export class InvoiceLineId extends Identifier { static new(): InvoiceLineId { return new InvoiceLineId(IdGenerator.uuid()); } }
export class SalesReturnId extends Identifier { static new(): SalesReturnId { return new SalesReturnId(IdGenerator.uuid()); } static from(id: string): SalesReturnId { return new SalesReturnId(id); } }
export class ReturnLineId extends Identifier { static new(): ReturnLineId { return new ReturnLineId(IdGenerator.uuid()); } }
export class CustomerReceiptId extends Identifier { static new(): CustomerReceiptId { return new CustomerReceiptId(IdGenerator.uuid()); } static from(id: string): CustomerReceiptId { return new CustomerReceiptId(id); } }
export class ReceiptAllocationId extends Identifier { static new(): ReceiptAllocationId { return new ReceiptAllocationId(IdGenerator.uuid()); } }
export class ReceivableAccountId extends Identifier { static new(): ReceivableAccountId { return new ReceivableAccountId(IdGenerator.uuid()); } static from(id: string): ReceivableAccountId { return new ReceivableAccountId(id); } }
export class DunningHistoryId extends Identifier { static new(): DunningHistoryId { return new DunningHistoryId(IdGenerator.uuid()); } }
export class SlsBranchId extends Identifier { static new(): SlsBranchId { return new SlsBranchId(IdGenerator.uuid()); } }
