import { Controller, Get, Post, Body, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { SalesPricingService } from "../../application/sales/sales-pricing-service.js";
import { DomainError } from "../../shared/domain-error.js";
import { GetPriceDto, GetPriceForCustomerDto } from "./dto/sales.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Sales - Pricing")
@Controller("api/sales/pricing")
export class SalesPricingController {
  constructor(private readonly svc: SalesPricingService) {}

  @Post("unit-price")
  @ApiOperation({ summary: "Get unit price by item and optional price list" })
  async getUnitPrice(@Body() dto: GetPriceDto) {
    try {
      const result = await this.svc.getUnitPrice(dto.itemId, dto.customerGroupId, dto.priceListId, dto.quantity);
      if (!result) throw new BadRequestException("Price not found");
      return result;
    } catch (e) { handleError(e); }
  }

  @Post("customer-price")
  @ApiOperation({ summary: "Get price for customer" })
  async getCustomerPrice(@Body() dto: GetPriceForCustomerDto) {
    try {
      const result = await this.svc.getPriceForCustomer(dto.itemId, dto.customerId, dto.quantity);
      if (!result) throw new BadRequestException("Price not found");
      return result;
    } catch (e) { handleError(e); }
  }
}
