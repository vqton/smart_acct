import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { InventoryService } from "../../application/inventory/inventory-service.js";
import { DomainError } from "../../shared/domain-error.js";
import { TransactionLine } from "../../domain/inventory/inv-transaction.js";
import { CountLine } from "../../domain/inventory/inv-count.js";
import { ReservationLine } from "../../domain/inventory/inv-reservation.js";
import {
  CreateItemDto, UpdateItemDto, ChangeItemStatusDto,
  CreateWarehouseDto, UpdateWarehouseDto,
  CreateLocationDto,
  CreateTransactionDto, CreateTransactionLineDto, ReverseTransactionDto, CancelTransactionDto,
  CreateStockCountDto, CreateCountLineDto, RecordCountDto, CancelCountDto,
  CreateReservationDto, CreateReservationLineDto, CancelReservationDto,
} from "./dto/inventory.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) {
    if (e.kind === "NotFound") throw new NotFoundException(e.message);
    throw new BadRequestException(e.message);
  }
  throw e;
}

@ApiTags("Inventory")
@Controller("api/inventory")
export class InventoryController {
  constructor(private readonly svc: InventoryService) {}

  // ─── Items ────────────────────────────────────────────────────────────────

  @Post("items")
  @ApiOperation({ summary: "Create item" })
  async createItem(@Body() dto: CreateItemDto) {
    try { return (await this.svc.createItem(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("items")
  @ApiOperation({ summary: "List items" })
  async listItems(@Query("status") status?: string) {
    return (await this.svc.listItems(status)).map(i => i.toState());
  }

  @Get("items/:id")
  @ApiOperation({ summary: "Get item by ID" })
  async getItem(@Param("id") id: string) {
    const item = await this.svc.getItem(id);
    if (!item) throw new NotFoundException("Item not found");
    return item.toState();
  }

  @Get("items/code/:code")
  @ApiOperation({ summary: "Get item by code" })
  async getItemByCode(@Param("code") code: string) {
    const item = await this.svc.getItemByCode(code);
    if (!item) throw new NotFoundException("Item not found");
    return item.toState();
  }

  @Put("items/:id")
  @ApiOperation({ summary: "Update item" })
  async updateItem(@Param("id") id: string, @Body() dto: UpdateItemDto) {
    try { return (await this.svc.updateItem(id, dto as any)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("items/:id/status")
  @ApiOperation({ summary: "Change item status" })
  async changeItemStatus(@Param("id") id: string, @Body() dto: ChangeItemStatusDto) {
    try { return (await this.svc.changeItemStatus(id, dto.status)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("items/:id/delete")
  @ApiOperation({ summary: "Delete item" })
  async deleteItem(@Param("id") id: string) {
    try { await this.svc.deleteItem(id); return { deleted: true }; }
    catch (e) { handleError(e); }
  }

  // ─── Warehouses ───────────────────────────────────────────────────────────

  @Post("warehouses")
  @ApiOperation({ summary: "Create warehouse" })
  async createWarehouse(@Body() dto: CreateWarehouseDto) {
    try { return (await this.svc.createWarehouse(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("warehouses")
  @ApiOperation({ summary: "List warehouses" })
  async listWarehouses() {
    return (await this.svc.listWarehouses()).map(w => w.toState());
  }

  @Get("warehouses/:id")
  @ApiOperation({ summary: "Get warehouse by ID" })
  async getWarehouse(@Param("id") id: string) {
    const wh = await this.svc.getWarehouse(id);
    if (!wh) throw new NotFoundException("Warehouse not found");
    return wh.toState();
  }

  @Put("warehouses/:id")
  @ApiOperation({ summary: "Update warehouse" })
  async updateWarehouse(@Param("id") id: string, @Body() dto: UpdateWarehouseDto) {
    try { return (await this.svc.updateWarehouse(id, dto as any)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Locations ────────────────────────────────────────────────────────────

  @Post("locations")
  @ApiOperation({ summary: "Create location" })
  async createLocation(@Body() dto: CreateLocationDto) {
    try { return (await this.svc.createLocation(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("locations")
  @ApiOperation({ summary: "List locations by warehouse" })
  async listLocations(@Query("warehouseId") warehouseId: string) {
    if (!warehouseId) throw new BadRequestException("warehouseId required");
    return (await this.svc.listLocations(warehouseId)).map(l => l.toState());
  }

  @Get("locations/:id")
  @ApiOperation({ summary: "Get location by ID" })
  async getLocation(@Param("id") id: string) {
    const loc = await this.svc.getLocation(id);
    if (!loc) throw new NotFoundException("Location not found");
    return loc.toState();
  }

  // ─── Stock Balances ───────────────────────────────────────────────────────

  @Get("stock")
  @ApiOperation({ summary: "Query stock balance" })
  async getStock(
    @Query("itemId") itemId?: string,
    @Query("warehouseId") warehouseId?: string,
  ) {
    if (itemId && warehouseId) {
      const bal = await this.svc.getStockBalance(itemId, warehouseId);
      return bal ? bal.toState() : { itemId, warehouseId, quantity: 0 };
    }
    if (itemId) return (await this.svc.listStockByItem(itemId)).map(b => b.toState());
    if (warehouseId) return (await this.svc.listStockByWarehouse(warehouseId)).map(b => b.toState());
    throw new BadRequestException("Provide itemId or warehouseId");
  }

  @Get("stock/low")
  @ApiOperation({ summary: "Find low stock items" })
  async findLowStock(@Query("threshold") threshold?: number) {
    return (await this.svc.findLowStock(threshold ?? 10)).map(b => b.toState());
  }

  // ─── Transactions ─────────────────────────────────────────────────────────

  @Post("transactions")
  @ApiOperation({ summary: "Create transaction" })
  async createTransaction(@Body() dto: CreateTransactionDto) {
    try {
      const txn = await this.svc.createTransaction({
        ...dto,
        transactionDate: dto.transactionDate ? new Date(dto.transactionDate) : undefined,
        postingDate: dto.postingDate ? new Date(dto.postingDate) : undefined,
      });
      return txn.toState();
    }
    catch (e) { handleError(e); }
  }

  @Get("transactions")
  @ApiOperation({ summary: "List transactions" })
  async listTransactions(
    @Query("warehouseId") warehouseId?: string,
    @Query("status") status?: string,
  ) {
    return (await this.svc.listTransactions(warehouseId, status)).map(t => t.toState());
  }

  @Get("transactions/:id")
  @ApiOperation({ summary: "Get transaction by ID" })
  async getTransaction(@Param("id") id: string) {
    const tx = await this.svc.getTransaction(id);
    if (!tx) throw new NotFoundException("Transaction not found");
    return tx.toState();
  }

  @Post("transactions/:id/lines")
  @ApiOperation({ summary: "Add line to transaction" })
  async addTransactionLine(@Param("id") id: string, @Body() dto: CreateTransactionLineDto) {
    try {
      const tx = await this.svc.getTransaction(id);
      if (!tx) throw new NotFoundException("Transaction not found");
      const line = TransactionLine.create({ transactionId: id, ...dto });
      tx.addLine(line);
      await this.svc.saveTransaction(tx);
      return tx.toState();
    } catch (e) { handleError(e); }
  }

  @Post("transactions/:id/submit")
  @ApiOperation({ summary: "Submit transaction" })
  async submitTransaction(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.svc.submitTransaction(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("transactions/:id/approve")
  @ApiOperation({ summary: "Approve transaction" })
  async approveTransaction(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.svc.approveTransaction(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("transactions/:id/post")
  @ApiOperation({ summary: "Post transaction (updates stock & cost layers)" })
  async postTransaction(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.svc.postTransaction(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("transactions/:id/reverse")
  @ApiOperation({ summary: "Reverse transaction" })
  async reverseTransaction(@Param("id") id: string, @Body() dto: ReverseTransactionDto) {
    try { return (await this.svc.reverseTransaction(id, "system", dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("transactions/:id/cancel")
  @ApiOperation({ summary: "Cancel transaction" })
  async cancelTransaction(@Param("id") id: string, @Body() dto: CancelTransactionDto) {
    try { await this.svc.cancelTransaction(id, "system", dto.reason); return { cancelled: true }; }
    catch (e) { handleError(e); }
  }

  // ─── Stock Counts ─────────────────────────────────────────────────────────

  @Post("counts")
  @ApiOperation({ summary: "Create stock count" })
  async createStockCount(@Body() dto: CreateStockCountDto) {
    try { return (await this.svc.createStockCount(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("counts")
  @ApiOperation({ summary: "List stock counts" })
  async listStockCounts(
    @Query("warehouseId") warehouseId?: string,
    @Query("status") status?: string,
  ) {
    return (await this.svc.listStockCounts(warehouseId, status)).map(c => c.toState());
  }

  @Get("counts/:id")
  @ApiOperation({ summary: "Get stock count by ID" })
  async getStockCount(@Param("id") id: string) {
    const sc = await this.svc.getStockCount(id);
    if (!sc) throw new NotFoundException("Stock count not found");
    return sc.toState();
  }

  @Post("counts/:id/lines")
  @ApiOperation({ summary: "Add line to stock count" })
  async addCountLine(@Param("id") id: string, @Body() dto: CreateCountLineDto) {
    try {
      const sc = await this.svc.getStockCount(id);
      if (!sc) throw new NotFoundException("Stock count not found");
      const line = CountLine.create({ countId: id, ...dto });
      sc.addLine(line);
      await this.svc.saveStockCount(sc);
      return sc.toState();
    } catch (e) { handleError(e); }
  }

  @Post("counts/:id/freeze")
  @ApiOperation({ summary: "Freeze stock count" })
  async freezeStockCount(@Param("id") id: string) {
    try { return (await this.svc.freezeStockCount(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("counts/:id/lines/:lineId/count")
  @ApiOperation({ summary: "Record count for line" })
  async recordCount(@Param("id") id: string, @Param("lineId") lineId: string, @Body() dto: RecordCountDto) {
    try {
      const sc = await this.svc.getStockCount(id);
      if (!sc) throw new NotFoundException("Stock count not found");
      const line = sc.lines.find(l => l.id.value === lineId);
      if (!line) throw new NotFoundException("Count line not found");
      line.recordCount(dto.actualQty, dto.countedById);
      await this.svc.saveStockCount(sc);
      return sc.toState();
    } catch (e) { handleError(e); }
  }

  @Post("counts/:id/complete")
  @ApiOperation({ summary: "Complete stock count" })
  async completeStockCount(@Param("id") id: string) {
    try { return (await this.svc.completeStockCount(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("counts/:id/approve")
  @ApiOperation({ summary: "Approve stock count (adjusts stock)" })
  async approveStockCount(@Param("id") id: string, @Body("userId") userId: string) {
    try { return (await this.svc.approveStockCount(id, userId || "system")).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("counts/:id/cancel")
  @ApiOperation({ summary: "Cancel stock count" })
  async cancelStockCount(@Param("id") id: string, @Body() dto: CancelCountDto) {
    try { await this.svc.cancelStockCount(id, dto.reason); return { cancelled: true }; }
    catch (e) { handleError(e); }
  }

  // ─── Reservations ─────────────────────────────────────────────────────────

  @Post("reservations")
  @ApiOperation({ summary: "Create reservation" })
  async createReservation(@Body() dto: CreateReservationDto) {
    try {
      const resv = await this.svc.createReservation({
        ...dto,
        expiresAt: dto.expiresAt ? new Date(dto.expiresAt) : undefined,
      });
      return resv.toState();
    }
    catch (e) { handleError(e); }
  }

  @Get("reservations")
  @ApiOperation({ summary: "List active reservations" })
  async listReservations() {
    return (await this.svc.listActiveReservations()).map(r => r.toState());
  }

  @Get("reservations/:id")
  @ApiOperation({ summary: "Get reservation by ID" })
  async getReservation(@Param("id") id: string) {
    const resv = await this.svc.getReservation(id);
    if (!resv) throw new NotFoundException("Reservation not found");
    return resv.toState();
  }

  @Post("reservations/:id/lines")
  @ApiOperation({ summary: "Add line to reservation" })
  async addReservationLine(@Param("id") id: string, @Body() dto: CreateReservationLineDto) {
    try {
      const line = ReservationLine.create({ reservationId: id, ...dto });
      return (await this.svc.addReservationLine(id, line)).toState();
    } catch (e) { handleError(e); }
  }

  @Post("reservations/:id/fulfill")
  @ApiOperation({ summary: "Fulfill reservation" })
  async fulfillReservation(@Param("id") id: string) {
    try { return (await this.svc.fulfillReservation(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("reservations/:id/cancel")
  @ApiOperation({ summary: "Cancel reservation" })
  async cancelReservation(@Param("id") id: string, @Body() dto: CancelReservationDto) {
    try { await this.svc.cancelReservation(id, dto.reason); return { cancelled: true }; }
    catch (e) { handleError(e); }
  }
}
