import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { IsString, IsOptional, IsNumber, IsBoolean, IsDateString, Min, Max, IsEnum } from "class-validator";

// ─── Item DTOs ──────────────────────────────────────────────────────────────

export class CreateItemDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() sku!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiProperty() @IsString() uomId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() itemType?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() category?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() barcode?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() plu?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() itemGroupId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() brandId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() valuationMethod?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() lotControl?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() shelfLifeDays?: number;
  @ApiPropertyOptional() @IsOptional() @IsBoolean() isHazardous?: boolean;
  @ApiPropertyOptional() @IsOptional() @IsString() glInventoryAccountId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() glCogsAccountId?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() standardCost?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() minStock?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() maxStock?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() reorderPoint?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() leadTimeDays?: number;
}

export class UpdateItemDto {
  @ApiPropertyOptional() @IsOptional() @IsString() name?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() barcode?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() valuationMethod?: string;
  @ApiPropertyOptional() @IsOptional() @IsNumber() standardCost?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() minStock?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() maxStock?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() reorderPoint?: number;
  @ApiPropertyOptional() @IsOptional() @IsNumber() leadTimeDays?: number;
  @ApiPropertyOptional() @IsOptional() @IsString() glInventoryAccountId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() glCogsAccountId?: string;
}

export class ChangeItemStatusDto {
  @ApiProperty() @IsString() status!: string;
}

// ─── Warehouse DTOs ─────────────────────────────────────────────────────────

export class CreateWarehouseDto {
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() branchId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() type?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() storageType?: string;
  @ApiPropertyOptional() @IsOptional() @IsBoolean() allowNegative?: boolean;
  @ApiPropertyOptional() @IsOptional() @IsString() phone?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() email?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() managerName?: string;
}

export class UpdateWarehouseDto {
  @ApiPropertyOptional() @IsOptional() @IsString() name?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() type?: string;
  @ApiPropertyOptional() @IsOptional() @IsBoolean() allowNegative?: boolean;
  @ApiPropertyOptional() @IsOptional() @IsString() phone?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() email?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() managerName?: string;
}

// ─── Location DTOs ──────────────────────────────────────────────────────────

export class CreateLocationDto {
  @ApiProperty() @IsString() warehouseId!: string;
  @ApiProperty() @IsString() code!: string;
  @ApiProperty() @IsString() name!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() type?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() parentId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() storageType?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() barcode?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() putawayZone?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() pickingZone?: string;
}

// ─── Transaction DTOs ───────────────────────────────────────────────────────

export class CreateTransactionDto {
  @ApiProperty() @IsString() transactionNumber!: string;
  @ApiProperty() @IsString() transactionType!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() warehouseId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() branchId?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() transactionDate?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() postingDate?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() referenceType?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() referenceId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() createdById?: string;
}

export class CreateTransactionLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemId!: string;
  @ApiProperty() @IsString() warehouseId!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiProperty() @IsNumber() unitCost!: number;
  @ApiProperty() @IsNumber() totalCost!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() locationId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() lotId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() description?: string;
}

export class ReverseTransactionDto {
  @ApiProperty() @IsString() reason!: string;
}

export class CancelTransactionDto {
  @ApiProperty() @IsString() reason!: string;
}

// ─── Stock Count DTOs ───────────────────────────────────────────────────────

export class CreateStockCountDto {
  @ApiProperty() @IsString() countNumber!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiProperty() @IsString() warehouseId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() countType?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() locationId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() notes?: string;
}

export class CreateCountLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemId!: string;
  @ApiProperty() @IsString() warehouseId!: string;
  @ApiProperty() @IsNumber() expectedQty!: number;
  @ApiProperty() @IsNumber() unitCost!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() locationId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() lotId?: string;
}

export class RecordCountDto {
  @ApiProperty() @IsNumber() actualQty!: number;
  @ApiProperty() @IsString() countedById!: string;
}

export class CancelCountDto {
  @ApiProperty() @IsString() reason!: string;
}

// ─── Reservation DTOs ───────────────────────────────────────────────────────

export class CreateReservationDto {
  @ApiProperty() @IsString() reservationNumber!: string;
  @ApiProperty() @IsString() orderType!: string;
  @ApiProperty() @IsString() orderId!: string;
  @ApiProperty() @IsString() companyId!: string;
  @ApiPropertyOptional() @IsOptional() @IsString() orderLineId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() customerId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() warehouseId?: string;
  @ApiPropertyOptional() @IsOptional() @IsDateString() expiresAt?: string;
}

export class CreateReservationLineDto {
  @ApiProperty() @IsNumber() lineNumber!: number;
  @ApiProperty() @IsString() itemId!: string;
  @ApiProperty() @IsString() warehouseId!: string;
  @ApiProperty() @IsNumber() quantity!: number;
  @ApiPropertyOptional() @IsOptional() @IsString() locationId?: string;
  @ApiPropertyOptional() @IsOptional() @IsString() lotId?: string;
}

export class CancelReservationDto {
  @ApiProperty() @IsString() reason!: string;
}
