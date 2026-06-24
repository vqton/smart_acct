import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PurchasingOrderService } from "../../application/purchasing/purchasing-order-service.js";
import { DomainError } from "../../shared/domain-error.js";
import { PurchaseRequisitionId, PurchaseOrderId, GoodsReceiptId, SupplierInvoiceId, ImportDeclarationId } from "../../domain/purchasing/purchasing-ids.js";
import { RequisitionItem } from "../../domain/purchasing/purchasing-requisition.js";
import { POLine } from "../../domain/purchasing/purchasing-order.js";
import { ReceiptLine } from "../../domain/purchasing/purchasing-receiving.js";
import { InvoiceLine } from "../../domain/purchasing/purchasing-invoice.js";
import { LandedCost } from "../../domain/purchasing/purchasing-import.js";
import {
  CreateRequisitionDto, CreateRequisitionItemDto, AddRequisitionItemsDto,
  CreateRFQDto, CreateRFQItemDto, SubmitQuotationDto,
  CreatePurchaseOrderDto, CreatePOLineDto, AddPOLinesDto, CreateContractDto,
  CreateGoodsReceiptDto, CreateReceiptLineDto, AddReceiptLinesDto,
  CreateInvoiceDto, CreateInvoiceLineDto, AddInvoiceLinesDto,
  CreateImportDeclarationDto, AddLandedCostDto,
  ApproveDto, RejectDto,
} from "./dto/purchasing.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Purchasing - Procurement")
@Controller("api/purchasing")
export class PurchasingOrderController {
  constructor(private readonly svc: PurchasingOrderService) {}

  // ─── Purchase Requisition ─────────────────────────────────────────────────────

  @Post("requisitions")
  @ApiOperation({ summary: "Create purchase requisition" })
  async createRequisition(@Body() dto: CreateRequisitionDto) {
    try {
      const pr = await this.svc.createRequisition(dto);
      await this.svc.saveRequisition(pr);
      return pr.toState();
    } catch (e) { handleError(e); }
  }

  @Get("requisitions")
  @ApiOperation({ summary: "List purchase requisitions" })
  async listRequisitions(@Query("status") status?: string) {
    return (await this.svc.listRequisitions(status)).map(r => r.toState());
  }

  @Get("requisitions/:id")
  @ApiOperation({ summary: "Get requisition by ID" })
  async getRequisition(@Param("id") id: string) {
    const pr = await this.svc.getRequisition(id);
    if (!pr) throw new NotFoundException("Requisition not found");
    return pr.toState();
  }

  @Post("requisitions/:id/items")
  @ApiOperation({ summary: "Add items to requisition" })
  async addRequisitionItems(@Param("id") id: string, @Body() dto: AddRequisitionItemsDto) {
    try {
      const pr = await this.svc.getRequisition(id);
      if (!pr) throw new NotFoundException("Requisition not found");
      for (const itemDto of dto.items) {
        const item = RequisitionItem.create({
          requisitionId: id, ...itemDto,
          requestedDate: itemDto.requestedDate ? new Date(itemDto.requestedDate) : undefined,
        });
        pr.addItem(item);
      }
      await this.svc.saveRequisition(pr);
      return pr.toState();
    } catch (e) { handleError(e); }
  }

  @Post("requisitions/:id/submit")
  @ApiOperation({ summary: "Submit requisition for approval" })
  async submitRequisition(@Param("id") id: string) {
    try { return (await this.svc.submitRequisition(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("requisitions/:id/approve")
  @ApiOperation({ summary: "Approve requisition" })
  async approveRequisition(@Param("id") id: string, @Body() dto: ApproveDto) {
    try { return (await this.svc.approveRequisition(id, dto.approvedBy)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── RFQ ──────────────────────────────────────────────────────────────────────

  @Post("rfqs")
  @ApiOperation({ summary: "Create RFQ" })
  async createRFQ(@Body() dto: CreateRFQDto) {
    try {
      const rfq = await this.svc.createRFQ({
        ...dto,
        responseDeadline: dto.responseDeadline ? new Date(dto.responseDeadline) : undefined,
      });
      await this.svc.saveRFQ(rfq);
      return rfq.toState();
    } catch (e) { handleError(e); }
  }

  @Get("rfqs")
  @ApiOperation({ summary: "List RFQs" })
  async listRFQs() {
    // simplified - would use proper repo method
    return [];
  }

  @Post("rfqs/:id/send")
  @ApiOperation({ summary: "Send RFQ to vendors" })
  async sendRFQ(@Param("id") id: string) {
    try { return (await this.svc.sendRFQ(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("quotations")
  @ApiOperation({ summary: "Submit quotation" })
  async submitQuotation(@Body() dto: SubmitQuotationDto) {
    try {
      const q = await this.svc.submitQuotation({
        ...dto, validUntil: dto.validUntil ? new Date(dto.validUntil) : undefined,
      });
      return q.toState();
    } catch (e) { handleError(e); }
  }

  // ─── Purchase Order ───────────────────────────────────────────────────────────

  @Post("orders")
  @ApiOperation({ summary: "Create purchase order" })
  async createPO(@Body() dto: CreatePurchaseOrderDto) {
    try {
      const po = await this.svc.createPO({
        ...dto,
        requestedDate: dto.requestedDate ? new Date(dto.requestedDate) : undefined,
      });
      await this.svc.savePO(po);
      return po.toState();
    } catch (e) { handleError(e); }
  }

  @Get("orders")
  @ApiOperation({ summary: "List purchase orders" })
  async listPOs(@Query("status") status?: string) {
    return (await this.svc.listPOs(status)).map(po => po.toState());
  }

  @Get("orders/:id")
  @ApiOperation({ summary: "Get purchase order" })
  async getPO(@Param("id") id: string) {
    const po = await this.svc.getPO(id);
    if (!po) throw new NotFoundException("Purchase order not found");
    return po.toState();
  }

  @Post("orders/:id/lines")
  @ApiOperation({ summary: "Add lines to PO" })
  async addPOLines(@Param("id") id: string, @Body() dto: AddPOLinesDto) {
    try {
      const po = await this.svc.getPO(id);
      if (!po) throw new NotFoundException("PO not found");
      for (const lineDto of dto.lines) {
        const line = POLine.create({
          poId: id, ...lineDto,
          expectedDate: lineDto.expectedDate ? new Date(lineDto.expectedDate) : undefined,
        });
        po.addLine(line);
      }
      await this.svc.savePO(po);
      return po.toState();
    } catch (e) { handleError(e); }
  }

  @Post("orders/:id/submit")
  @ApiOperation({ summary: "Submit PO for approval" })
  async submitPO(@Param("id") id: string) {
    try { return (await this.svc.submitPO(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("orders/:id/approve")
  @ApiOperation({ summary: "Approve purchase order" })
  async approvePO(@Param("id") id: string, @Body() dto: ApproveDto) {
    try { return (await this.svc.approvePO(id, dto.approvedBy)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("orders/:id/send")
  @ApiOperation({ summary: "Send PO to vendor" })
  async sendPO(@Param("id") id: string) {
    try { return (await this.svc.sendPO(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("orders/:id/confirm")
  @ApiOperation({ summary: "Confirm PO" })
  async confirmPO(@Param("id") id: string, @Body() dto: { confirmedBy: string }) {
    try { return (await this.svc.confirmPO(id, dto.confirmedBy)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("orders/:id/cancel")
  @ApiOperation({ summary: "Cancel PO" })
  async cancelPO(@Param("id") id: string, @Body() dto: { reason: string }) {
    try { return (await this.svc.cancelPO(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("orders/:id/close")
  @ApiOperation({ summary: "Close PO" })
  async closePO(@Param("id") id: string) {
    try { return (await this.svc.closePO(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("orders/:id/hold")
  @ApiOperation({ summary: "Hold PO" })
  async holdPO(@Param("id") id: string, @Body() dto: { reason: string }) {
    try { return (await this.svc.holdPO(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("orders/:id/release")
  @ApiOperation({ summary: "Release PO from hold" })
  async releasePO(@Param("id") id: string) {
    try { return (await this.svc.releasePO(id)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Contract ─────────────────────────────────────────────────────────────────

  @Post("contracts")
  @ApiOperation({ summary: "Create purchase contract" })
  async createContract(@Body() dto: CreateContractDto) {
    try {
      const c = await this.svc.createContract({
        ...dto,
        startDate: new Date(dto.startDate),
        endDate: new Date(dto.endDate),
      });
      await this.svc.activateContract(c.id.value);
      return c.toState();
    } catch (e) { handleError(e); }
  }

  @Get("contracts/:id")
  @ApiOperation({ summary: "Get contract" })
  async getContract(@Param("id") id: string) {
    return { id, message: "Contract endpoint" }; // placeholder
  }

  // ─── Goods Receipt ────────────────────────────────────────────────────────────

  @Post("receipts")
  @ApiOperation({ summary: "Create goods receipt" })
  async createReceipt(@Body() dto: CreateGoodsReceiptDto) {
    try {
      const gr = await this.svc.createReceipt({
        ...dto,
        receiptDate: new Date(dto.receiptDate),
      });
      await this.svc.saveReceipt(gr);
      return gr.toState();
    } catch (e) { handleError(e); }
  }

  @Get("receipts/:id")
  @ApiOperation({ summary: "Get goods receipt" })
  async getReceipt(@Param("id") id: string) {
    const gr = await this.svc["grRepo"].findById(GoodsReceiptId.from(id));
    if (!gr) throw new NotFoundException("Receipt not found");
    return gr.toState();
  }

  @Post("receipts/:id/lines")
  @ApiOperation({ summary: "Add lines to receipt" })
  async addReceiptLines(@Param("id") id: string, @Body() dto: AddReceiptLinesDto) {
    try {
      const gr = await this.svc["grRepo"].findById(GoodsReceiptId.from(id));
      if (!gr) throw new NotFoundException("Receipt not found");
      for (const lineDto of dto.lines) {
        const line = ReceiptLine.create({
          receiptId: id, poId: gr.poId, ...lineDto,
          expiryDate: lineDto.expiryDate ? new Date(lineDto.expiryDate) : undefined,
        });
        gr.addLine(line);
      }
      await this.svc.saveReceipt(gr);
      return gr.toState();
    } catch (e) { handleError(e); }
  }

  @Post("receipts/:id/reverse")
  @ApiOperation({ summary: "Reverse goods receipt" })
  async reverseReceipt(@Param("id") id: string, @Body() dto: { reason: string }) {
    try { return (await this.svc.reverseReceipt(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Supplier Invoice ─────────────────────────────────────────────────────────

  @Post("invoices")
  @ApiOperation({ summary: "Create supplier invoice" })
  async createInvoice(@Body() dto: CreateInvoiceDto) {
    try {
      const inv = await this.svc.createInvoice({
        ...dto,
        invoiceDate: new Date(dto.invoiceDate),
        dueDate: dto.dueDate ? new Date(dto.dueDate) : undefined,
      });
      await this.svc.saveInvoice(inv);
      return inv.toState();
    } catch (e) { handleError(e); }
  }

  @Get("invoices")
  @ApiOperation({ summary: "List invoices" })
  async listInvoices(@Query("status") status?: string) {
    const repo = this.svc["invRepo"];
    const invoices = status ? await repo.findByStatus(status) : await repo.findAll();
    return invoices.map(i => i.toState());
  }

  @Get("invoices/:id")
  @ApiOperation({ summary: "Get invoice" })
  async getInvoice(@Param("id") id: string) {
    const inv = await this.svc["invRepo"].findById(SupplierInvoiceId.from(id));
    if (!inv) throw new NotFoundException("Invoice not found");
    return inv.toState();
  }

  @Post("invoices/:id/lines")
  @ApiOperation({ summary: "Add lines to invoice" })
  async addInvoiceLines(@Param("id") id: string, @Body() dto: AddInvoiceLinesDto) {
    try {
      const inv = await this.svc["invRepo"].findById(SupplierInvoiceId.from(id));
      if (!inv) throw new NotFoundException("Invoice not found");
      for (const lineDto of dto.lines) {
        const line = InvoiceLine.create({ invoiceId: id, ...lineDto });
        inv.addLine(line);
      }
      await this.svc.saveInvoice(inv);
      return inv.toState();
    } catch (e) { handleError(e); }
  }

  @Post("invoices/:id/verify")
  @ApiOperation({ summary: "Verify invoice" })
  async verifyInvoice(@Param("id") id: string) {
    try { return (await this.svc.verifyInvoice(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("invoices/:id/approve")
  @ApiOperation({ summary: "Approve invoice" })
  async approveInvoice(@Param("id") id: string, @Body() dto: ApproveDto) {
    try { return (await this.svc.approveInvoice(id, dto.approvedBy)).toState(); }
    catch (e) { handleError(e); }
  }

  @Post("invoices/:id/cancel")
  @ApiOperation({ summary: "Cancel invoice" })
  async cancelInvoice(@Param("id") id: string, @Body() dto: { reason: string }) {
    try { return (await this.svc.cancelInvoice(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Import ────────────────────────────────────────────────────────────────────

  @Post("imports")
  @ApiOperation({ summary: "Create import declaration" })
  async createImport(@Body() dto: CreateImportDeclarationDto) {
    try {
      const d = await this.svc.createImportDeclaration(dto);
      await this.svc["importRepo"].save(d);
      return d.toState();
    } catch (e) { handleError(e); }
  }

  @Post("imports/:id/landed-costs")
  @ApiOperation({ summary: "Add landed cost to import" })
  async addLandedCost(@Param("id") id: string, @Body() dto: AddLandedCostDto) {
    try {
      const lc = LandedCost.create({ importDeclarationId: id, ...dto } as any);
      const d = await this.svc.addLandedCost(id, lc);
      return d.toState();
    } catch (e) { handleError(e); }
  }
}
