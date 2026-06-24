import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsEnum, IsNumber, IsBoolean, IsDateString, Min, MaxLength, MinLength, ValidateNested, IsArray, ArrayMinSize, IsUUID } from "class-validator";
import { Type } from "class-transformer";
import {
  VendorStatus, VendorType, RequisitionStatus, RequisitionPriority, POStatus, POType,
  ContractStatus, ContractType, InvoiceStatus, InvoiceMatchStatus, Incoterm, MatchingRule,
  ApprovalStatus, WorkflowEntityType,
} from "../../../domain/purchasing/purchasing-enums.js";

// ─── Vendor ──────────────────────────────────────────────────────────────────────

export class CreateVendorDto {
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(20) code!: string;
  @ApiProperty() @IsString() @MinLength(1) @MaxLength(255) name!: string;
  @ApiProperty() @IsString() @MaxLength(2) country!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() nameEn?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() taxCode?: string;
  @ApiPropertyOptional({ enum: VendorType }) @IsOptional() @IsEnum(VendorType) vendorType?: VendorType;
  @ApiPropertyOptional() @IsString() @IsOptional() category?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() classification?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() email?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() address?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() ward?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() district?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() province?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() postalCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() paymentTermCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
}

export class UpdateVendorDto {
  @ApiPropertyOptional() @IsString() @IsOptional() name?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() nameEn?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() taxCode?: string;
  @ApiPropertyOptional({ enum: VendorType }) @IsOptional() @IsEnum(VendorType) vendorType?: VendorType;
  @ApiPropertyOptional() @IsString() @IsOptional() category?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() phone?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() email?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() address?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() paymentTermCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
}

export class VendorActionDto {
  @ApiProperty() @IsString() reason!: string;
}

export class VendorSearchDto {
  @ApiPropertyOptional() @IsString() @IsOptional() code?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() name?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() taxCode?: string;
  @ApiPropertyOptional({ enum: VendorStatus }) @IsOptional() @IsEnum(VendorStatus) status?: VendorStatus;
  @ApiPropertyOptional() @IsString() @IsOptional() category?: string;
}

export class EvaluateVendorDto {
  @ApiProperty() @IsString() evaluator!: string;
  @ApiProperty() @IsString() score!: string;
  @ApiProperty() @IsString() criteria!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() comments?: string;
}

// ─── Purchase Requisition ────────────────────────────────────────────────────────

export class CreateRequisitionDto {
  @ApiProperty() @IsString() prNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() requesterId!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() departmentId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional({ enum: RequisitionPriority }) @IsOptional() @IsEnum(RequisitionPriority) priority?: RequisitionPriority;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class CreateRequisitionItemDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiProperty() @IsString() uom!: string;
  @ApiProperty() @IsNumber() estimatedUnitPrice!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() itemId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() requestedDate?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() projectId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() costCenterId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() warehouseId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class AddRequisitionItemsDto {
  @ApiProperty({ type: [CreateRequisitionItemDto] }) @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => CreateRequisitionItemDto) items!: CreateRequisitionItemDto[];
}

// ─── RFQ ─────────────────────────────────────────────────────────────────────────

export class CreateRFQDto {
  @ApiProperty() @IsString() rfqNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() title!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() responseDeadline?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class CreateRFQItemDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiProperty() @IsString() uom!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() itemId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() expectedUnitPrice?: number;
  @ApiPropertyOptional() @IsDateString() @IsOptional() requiredDate?: string;
}

export class SubmitQuotationDto {
  @ApiProperty() @IsUUID() rfqId!: string;
  @ApiProperty() @IsUUID() vendorId!: string;
  @ApiProperty() @IsString() vendorName!: string;
  @ApiProperty() @IsString() quotationNumber!: string;
  @ApiProperty() @IsNumber() totalAmount!: number;
  @ApiPropertyOptional() @IsDateString() @IsOptional() validUntil?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

// ─── Purchase Order ──────────────────────────────────────────────────────────────

export class CreatePurchaseOrderDto {
  @ApiProperty() @IsString() poNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() vendorId!: string;
  @ApiProperty() @IsString() vendorName!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional({ enum: POType }) @IsOptional() @IsEnum(POType) poType?: POType;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() paymentTermCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() incoterm?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() requestedDate?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() sourceDocumentType?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() sourceDocumentId?: string;
}

export class CreatePOLineDto {
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
  @ApiPropertyOptional() @IsDateString() @IsOptional() expectedDate?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() warehouseId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() projectId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() costCenterId?: string;
}

export class AddPOLinesDto {
  @ApiProperty({ type: [CreatePOLineDto] }) @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => CreatePOLineDto) lines!: CreatePOLineDto[];
}

// ─── Contract ────────────────────────────────────────────────────────────────────

export class CreateContractDto {
  @ApiProperty() @IsString() contractNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() vendorId!: string;
  @ApiProperty() @IsString() vendorName!: string;
  @ApiProperty() @IsString() title!: string;
  @ApiProperty() @IsDateString() startDate!: string;
  @ApiProperty() @IsDateString() endDate!: string;
  @ApiPropertyOptional({ enum: ContractType }) @IsOptional() @IsEnum(ContractType) contractType?: ContractType;
  @ApiPropertyOptional() @IsNumber() @IsOptional() totalValue?: number;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() paymentTermCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

// ─── Goods Receipt ───────────────────────────────────────────────────────────────

export class CreateGoodsReceiptDto {
  @ApiProperty() @IsString() receiptNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() vendorId!: string;
  @ApiProperty() @IsString() vendorName!: string;
  @ApiProperty() @IsUUID() poId!: string;
  @ApiProperty() @IsString() poNumber!: string;
  @ApiProperty() @IsDateString() receiptDate!: string;
  @ApiProperty() @IsString() receivedBy!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() branchId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() warehouseId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class CreateReceiptLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() poLineId!: string;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiProperty() @IsNumber() quantityReceived!: number;
  @ApiProperty() @IsString() uom!: string;
  @ApiProperty() @IsNumber() unitPrice!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() itemId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() batchNumber?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() locationId?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() expiryDate?: string;
}

export class AddReceiptLinesDto {
  @ApiProperty({ type: [CreateReceiptLineDto] }) @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => CreateReceiptLineDto) lines!: CreateReceiptLineDto[];
}

// ─── Supplier Invoice ────────────────────────────────────────────────────────────

export class CreateInvoiceDto {
  @ApiProperty() @IsString() invoiceNumber!: string;
  @ApiProperty() @IsDateString() invoiceDate!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() vendorId!: string;
  @ApiProperty() @IsString() vendorName!: string;
  @ApiPropertyOptional() @IsUUID() @IsOptional() poId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() poNumber?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() matchingRule?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() paymentTermCode?: string;
  @ApiPropertyOptional() @IsDateString() @IsOptional() dueDate?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() description?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class CreateInvoiceLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemCode!: string;
  @ApiProperty() @IsString() itemName!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiProperty() @IsString() uom!: string;
  @ApiProperty() @IsNumber() unitPrice!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() poLineId?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() taxCode?: string;
  @ApiPropertyOptional() @IsNumber() @IsOptional() taxRate?: number;
}

export class AddInvoiceLinesDto {
  @ApiProperty({ type: [CreateInvoiceLineDto] }) @IsArray() @ArrayMinSize(1) @ValidateNested({ each: true }) @Type(() => CreateInvoiceLineDto) lines!: CreateInvoiceLineDto[];
}

// ─── Import ──────────────────────────────────────────────────────────────────────

export class CreateImportDeclarationDto {
  @ApiProperty() @IsString() declarationNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsUUID() poId!: string;
  @ApiProperty() @IsString() poNumber!: string;
  @ApiProperty() @IsUUID() vendorId!: string;
  @ApiProperty() @IsString() vendorName!: string;
  @ApiPropertyOptional({ enum: Incoterm }) @IsOptional() @IsEnum(Incoterm) incoterm?: Incoterm;
  @ApiPropertyOptional() @IsString() @IsOptional() portOfLoading?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() portOfDischarge?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class AddLandedCostDto {
  @ApiProperty() @IsString() costType!: string;
  @ApiProperty() @IsString() description!: string;
  @ApiProperty() @IsNumber() amount!: number;
  @ApiPropertyOptional() @IsString() @IsOptional() currencyCode?: string;
  @ApiPropertyOptional() @IsString() @IsOptional() allocationBasis?: string;
}

// ─── Approval ────────────────────────────────────────────────────────────────────

export class ApproveDto {
  @ApiProperty() @IsString() approvedBy!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() notes?: string;
}

export class RejectDto {
  @ApiProperty() @IsString() reason!: string;
  @ApiPropertyOptional() @IsString() @IsOptional() rejectedBy?: string;
}
