import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsEnum, IsNumber, IsBoolean, IsDateString, Min, MaxLength, MinLength, ValidateNested, IsArray, ArrayMinSize, IsUUID } from "class-validator";
import { Type } from "class-transformer";
import {
  SlsCustomerStatus, SlsCustomerType, SlsCustomerCategory, SlsPriceGroup, SlsDiscountGroup,
  SlsOrderStatus, SlsOrderType, SlsOrderSource, SlsQuotationStatus,
  SlsDeliveryStatus, SlsInvoiceStatus, SlsInvoiceType,
  SlsReturnStatus, SlsReturnReason, SlsPaymentStatus, SlsPaymentMethod,
} from "../../../domain/sales/sales-enums.js";

// ─── Customer ────────────────────────────────────────────────────────────────────

export class CreateCustomerDto {
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(20) code!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(255) name!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() nameEn?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() groupId?: string;
  @ApiPropertyOptional({ enum: SlsCustomerType }) @IsOptional() @IsEnum(SlsCustomerType) customerType?: SlsCustomerType;
  @ApiPropertyOptional({ enum: SlsCustomerCategory }) @IsOptional() @IsEnum(SlsCustomerCategory) category?: SlsCustomerCategory;
  @ApiPropertyOptional() @IsString() @IsOptional() taxCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() email?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() address?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() ward?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() district?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() province?: string;
  @ApiPropertyOptional({ enum: SlsPriceGroup }) @IsOptional() @IsEnum(SlsPriceGroup) priceGroup?: SlsPriceGroup;
  @ApiPropertyOptional({ enum: SlsDiscountGroup }) @IsOptional() @IsEnum(SlsDiscountGroup) discountGroup?: SlsDiscountGroup;
  @ApiPropertyOptional() @IsNumber() @IsOptional() creditLimit?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() paymentTermCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() storeId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() salespersonId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
}

export class UpdateCustomerDto {
  @ApiPropertyOptional() @IsString() @IsOptional() name?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() nameEn?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() email?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() address?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() ward?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() district?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() province?: string;
  @ApiPropertyOptional({ enum: SlsPriceGroup }) @IsOptional() @IsEnum(SlsPriceGroup) priceGroup?: SlsPriceGroup;
  @ApiPropertyOptional({ enum: SlsDiscountGroup }) @IsOptional() @IsEnum(SlsDiscountGroup) discountGroup?: SlsDiscountGroup;
  @ApiPropertyOptional() @IsString() @IsOptional() paymentTermCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() salespersonId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
}

export class CustomerSearchDto {
  @ApiPropertyOptional() @IsString() @IsOptional() code?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() name?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() taxCode?: string;
  @ApiPropertyOptional({ enum: SlsCustomerStatus }) @IsOptional() @IsEnum(SlsCustomerStatus) status?: SlsCustomerStatus;
  @ApiPropertyOptional() @IsString() @IsOptional() phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() email?: string;
}

export class CustomerActionDto {
  @ApiProperty() @IsString() reason!: string;
}

export class SetCreditLimitDto {
  @ApiProperty() @IsNumber() creditLimit!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() reason?: string;
}

// ─── Order ───────────────────────────────────────────────────────────────────────

export class CreateSalesOrderDto {
  @ApiProperty() @IsString() orderNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() customerId!: string;
  @ApiProperty() @IsString() customerName!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() storeId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() salespersonId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() customerTaxCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() customerAddress?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() customerPhone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() customerEmail?: string;
  @ApiPropertyOptional({ enum: SlsOrderType }) @IsOptional() @IsEnum(SlsOrderType) orderType?: SlsOrderType;
  @ApiPropertyOptional({ enum: SlsOrderSource }) @IsOptional() @IsEnum(SlsOrderSource) orderSource?: SlsOrderSource;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() exchangeRate?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryAddress?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryWard?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryDistrict?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryProvince?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryContact?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryPhone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() paymentTermCode?: string;
  @ApiPropertyOptional({ enum: SlsPaymentMethod }) @IsOptional() @IsEnum(SlsPaymentMethod) paymentMethod?: SlsPaymentMethod;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() internalNotes?: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() quotationId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() quotationNumber?: string;
}

export class CreateOrderLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiProperty() @IsString() uom!: string;
  @ApiProperty() @IsNumber() unitPrice!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() itemId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() taxCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() taxRate?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() discountPercent?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() discountAmount?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() unitCost?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() warehouseId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() projectId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() costCenterId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() departmentId?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() expectedDate?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() promisedDate?: string;
}

export class AddOrderLinesDto {
  @ApiProperty({ type: [CreateOrderLineDto] }) @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => CreateOrderLineDto) lines!: CreateOrderLineDto[];
}

export class ConvertQuotationDto {
  @ApiProperty() @IsString() orderNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() orderDate?: string;
}

export class OrderActionDto {
  @ApiProperty() @IsString() reason!: string;
}

export class ApproveOrderDto {
  @ApiProperty() @IsString() approvedBy!: string;
}

export class CancelOrderDto {
  @ApiProperty() @IsString() reason!: string;
}

// ─── Invoice ─────────────────────────────────────────────────────────────────────

export class CreateSalesInvoiceDto {
  @ApiProperty() @IsString() invoiceNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() customerId!: string;
  @ApiProperty() @IsString() customerName!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() customerTaxCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() customerAddress?: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() orderId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() orderNumber?: string;
  @ApiPropertyOptional({ enum: SlsInvoiceType }) @IsOptional() @IsEnum(SlsInvoiceType) invoiceType?: SlsInvoiceType;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() exchangeRate?: number;
  @ApiPropertyOptional() @IsDateString() @IsOptional() invoiceDate?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class CreateInvoiceLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiProperty() @IsString() uom!: string;
  @ApiProperty() @IsNumber() unitPrice!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() itemId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() orderLineId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() taxCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() taxRate?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() discountPercent?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() discountAmount?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() warehouseId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() projectId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() costCenterId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() departmentId?: string;
}

export class AddInvoiceLinesDto {
  @ApiProperty({ type: [CreateInvoiceLineDto] }) @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => CreateInvoiceLineDto) lines!: CreateInvoiceLineDto[];
}

export class CreateFromOrderInvoiceDto {
  @ApiProperty() @IsString() invoiceNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
}

export class PostInvoiceDto {
  @ApiProperty() @IsString() postedById!: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() dueDays?: number;
}

export class CreditNoteDto {
  @ApiProperty() @IsString() creditNoteNumber!: string;
  @ApiProperty() @IsString() reason!: string;
}

export class EinvoiceUpdateDto {
  @ApiProperty() @IsString() einvoiceNumber!: string;
  @ApiProperty() @IsString() einvoiceCode!: string;
  @ApiProperty() @IsString() verifyCode!: string;
  @ApiProperty() @IsDateString() issueDate!: string;
}

// ─── Delivery ────────────────────────────────────────────────────────────────────

export class CreateDeliveryDto {
  @ApiProperty() @IsString() deliveryNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() orderId!: string;
  @ApiProperty() @IsString() orderNumber!: string;
  @ApiProperty() @IsUUID() customerId!: string;
  @ApiProperty() @IsString() customerName!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryAddress?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryWard?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryDistrict?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryProvince?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryContact?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryPhone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() deliveryType?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() deliveryDate?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() carrierId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() carrierName?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() trackingNumber?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() shipmentMethod?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class CreateDeliveryLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiProperty() @IsNumber() quantityDelivered!: number;
  @ApiProperty() @IsString() uom!: string;
  @ApiProperty() @IsNumber() unitPrice!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() orderLineId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() itemId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() batchNumber?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() serialNumber?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() expiryDate?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() warehouseId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class AddDeliveryLinesDto {
  @ApiProperty({ type: [CreateDeliveryLineDto] }) @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => CreateDeliveryLineDto) lines!: CreateDeliveryLineDto[];
}

export class CreateFromOrderDeliveryDto {
  @ApiProperty() @IsString() deliveryNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
}

export class MarkDeliveredDto {
  @ApiPropertyOptional() @IsString() @IsOptional() podReceivedBy?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() podNotes?: string;
}

export class DeliveryExceptionDto {
  @ApiProperty() @IsString() exceptionType!: string;
  @ApiProperty() @IsString() reason!: string;
}

export class DeliveryCancelDto {
  @ApiProperty() @IsString() reason!: string;
}

// ─── Return ──────────────────────────────────────────────────────────────────────

export class CreateSalesReturnDto {
  @ApiProperty() @IsString() returnNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() customerId!: string;
  @ApiProperty() @IsString() customerName!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() orderId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() orderNumber?: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() invoiceId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() invoiceNumber?: string;
  @ApiProperty({ enum: SlsReturnReason }) @IsEnum(SlsReturnReason) returnReason!: SlsReturnReason;
  @ApiPropertyOptional() @IsString() @IsOptional() reasonDetail?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() returnType?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class CreateReturnLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiProperty() @IsNumber() quantityReturned!: number;
  @ApiProperty() @IsString() uom!: string;
  @ApiProperty() @IsNumber() unitPrice!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() orderLineId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() taxCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() taxRate?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() discountPercent?: number;
  @ApiPropertyOptional() @IsNumber() @IsOptional() discountAmount?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() warehouseId?: string;
}

export class AddReturnLinesDto {
  @ApiProperty({ type: [CreateReturnLineDto] }) @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => CreateReturnLineDto) lines!: CreateReturnLineDto[];
}

export class CreateFromOrderReturnDto {
  @ApiProperty() @IsString() returnNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty({ enum: SlsReturnReason }) @IsEnum(SlsReturnReason) returnReason!: SlsReturnReason;
  @ApiPropertyOptional() @IsString() @IsOptional() reasonDetail?: string;
}

export class InspectReturnDto {
  @ApiProperty() @IsString() result!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class ApproveReturnDto {
  @ApiProperty() @IsString() approvedBy!: string;
}

// ─── Payment / Receipt ───────────────────────────────────────────────────────────

export class CreateReceiptDto {
  @ApiProperty() @IsString() receiptNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() customerId!: string;
  @ApiProperty() @IsString() customerName!: string;
  @ApiProperty() @IsNumber() amount!: number;
  @ApiProperty({ enum: SlsPaymentMethod }) @IsEnum(SlsPaymentMethod) paymentMethod!: SlsPaymentMethod;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() orderId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() orderNumber?: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() invoiceId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() invoiceNumber?: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() returnId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() returnNumber?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() paymentDate?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() exchangeRate?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() paymentRef?: string;
  @ApiPropertyOptional() @IsBoolean() @IsOptional() isSplitPayment?: boolean;
  @ApiPropertyOptional() @IsNumber() @IsOptional() splitCount?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class ApproveReceiptDto {
  @ApiProperty() @IsString() approvedBy!: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() allocateToInvoiceId?: string;
}

// ─── Receivable ──────────────────────────────────────────────────────────────────

export class WriteOffDto {
  @ApiProperty() @IsNumber() amount!: number;
  @ApiProperty() @IsString() reason!: string;
  @ApiProperty() @IsString() approvedBy!: string;
}

export class DunningDto {
  @ApiProperty() @IsNumber() level!: number;
}

// ─── Pricing ─────────────────────────────────────────────────────────────────────

export class GetPriceDto {
  @ApiProperty() @IsString() itemId!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() customerGroupId?: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() priceListId?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() quantity?: number;
}

export class GetPriceForCustomerDto {
  @ApiProperty() @IsString() itemId!: string;
  @ApiProperty() @IsUUID() customerId!: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() quantity?: number;
}

// ─── Shared ──────────────────────────────────────────────────────────────────────

export class ApproveDto {
  @ApiProperty() @IsString() approvedBy!: string;
}

export class CancelWithReasonDto {
  @ApiProperty() @IsString() reason!: string;
}
