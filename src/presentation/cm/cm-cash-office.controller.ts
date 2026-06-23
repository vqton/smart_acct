import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaCashBoxRepository, PrismaCashSessionRepository, PrismaCashReceiptRepository, PrismaCashPaymentRepository, PrismaPettyCashRepository, PrismaCashAdvanceRepository, PrismaCashTransferRepository } from "../../infrastructure/cm/cm-prisma-repos.js";
import { CashBoxService } from "../../application/cm/cm-cashbox-service.js";
import { CashBox } from "../../domain/cm/cm-cash-box.js";
import { CashSession } from "../../domain/cm/cm-session.js";
import { CashReceipt } from "../../domain/cm/cm-cash-receipt.js";
import { CashPayment } from "../../domain/cm/cm-cash-payment.js";
import { CashAdvance } from "../../domain/cm/cm-cash-advance.js";
import { CashTransfer } from "../../domain/cm/cm-cash-transfer.js";
import { PettyCash } from "../../domain/cm/cm-petty-cash.js";
import { CashBoxId, CashSessionId, CashReceiptId, CashPaymentId, CashAdvanceId, CashTransferId, PettyCashId } from "../../domain/cm/cm-ids.js";
import { DomainError } from "../../shared/domain-error.js";
import { CreateCashBoxDto, OpenSessionDto, CloseSessionDto, CreateReceiptDto, CreatePaymentDto, CreateCashAdvanceDto, CreateCashTransferDto, CreatePettyCashDto, ApproveDto, ReverseDto, RejectDto } from "./dto/cm.dto.js";

@ApiTags("CM - Cash Office")
@Controller("api/cm")
export class CashOfficeController {
  constructor(
    private readonly boxRepo: PrismaCashBoxRepository,
    private readonly sessionRepo: PrismaCashSessionRepository,
    private readonly receiptRepo: PrismaCashReceiptRepository,
    private readonly paymentRepo: PrismaCashPaymentRepository,
    private readonly advanceRepo: PrismaCashAdvanceRepository,
    private readonly transferRepo: PrismaCashTransferRepository,
    private readonly pettyCashRepo: PrismaPettyCashRepository,
    private readonly cashBoxService: CashBoxService,
  ) {}

  // ─── Cash Box CRUD ──────────────────────────────────────────────────────────

  @Post("cash-boxes")
  @ApiOperation({ summary: "Create a new cash box" })
  async createBox(@Body() dto: CreateCashBoxDto) {
    const box = await this.cashBoxService.createBox({
      locationId: dto.locationId,
      code: dto.code,
      name: dto.name,
      boxType: dto.boxType,
      currencyCode: dto.currencyCode,
      minBalance: dto.minBalance,
      maxBalance: dto.maxBalance,
      allowNegative: dto.allowNegative,
      description: dto.description,
    });
    return box.toState();
  }

  @Get("cash-boxes")
  @ApiOperation({ summary: "List all cash boxes" })
  async listBoxes() {
    const boxes = await this.boxRepo.findAll();
    return boxes.map(b => b.toState());
  }

  @Get("cash-boxes/:id")
  @ApiOperation({ summary: "Get cash box by ID" })
  async getBox(@Param("id") id: string) {
    const box = await this.boxRepo.findById(new CashBoxId(id));
    if (!box) throw new NotFoundException("Cash box not found");
    return box.toState();
  }

  // ─── Cash Session ───────────────────────────────────────────────────────────

  @Post("sessions/open")
  @ApiOperation({ summary: "Open a cash session" })
  async openSession(@Body() dto: OpenSessionDto) {
    try {
      const session = await this.cashBoxService.openSession({
        cashBoxId: dto.cashBoxId,
        cashierId: dto.cashierId,
        openedBalance: dto.openedBalance,
        currencyCode: dto.currencyCode,
      });
      return session.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Put("sessions/:id/close")
  @ApiOperation({ summary: "Close a cash session with count" })
  async closeSession(@Param("id") id: string, @Body() dto: CloseSessionDto) {
    try {
      const session = await this.cashBoxService.closeSession({
        sessionId: id,
        countedBalance: dto.countedBalance,
        notes: dto.notes,
      });
      return session.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Get("sessions")
  @ApiOperation({ summary: "List cash sessions" })
  async listSessions(
    @Query("cashBoxId") cashBoxId?: string,
    @Query("cashierId") cashierId?: string,
    @Query("fromDate") fromDate?: string,
    @Query("toDate") toDate?: string,
  ) {
    if (cashBoxId) return (await this.sessionRepo.findByCashBox(cashBoxId)).map(s => s.toState());
    if (cashierId) return (await this.sessionRepo.findByCashier(cashierId)).map(s => s.toState());
    if (fromDate || toDate) {
      return (await this.sessionRepo.findByDateRange(
        fromDate ? new Date(fromDate) : new Date(0),
        toDate ? new Date(toDate) : new Date("2100-01-01"),
      )).map(s => s.toState());
    }
    return (await this.sessionRepo.findAll()).map(s => s.toState());
  }

  @Get("sessions/:id")
  @ApiOperation({ summary: "Get session by ID" })
  async getSession(@Param("id") id: string) {
    const s = await this.sessionRepo.findById(new CashSessionId(id));
    if (!s) throw new NotFoundException("Session not found");
    return s.toState();
  }

  // ─── Cash Receipts ──────────────────────────────────────────────────────────

  @Post("receipts")
  @ApiOperation({ summary: "Record a cash receipt" })
  async createReceipt(@Body() dto: CreateReceiptDto) {
    try {
      const receipt = await this.cashBoxService.recordReceipt({
        receiptNumber: dto.receiptNumber,
        receiptDate: new Date(dto.receiptDate),
        cashBoxId: dto.cashBoxId,
        cashierId: dto.cashierId,
        amount: dto.amount,
        currencyCode: dto.currencyCode,
        paymentMethod: dto.paymentMethod,
        sessionId: dto.sessionId,
        paidBy: dto.paidBy,
        reference: dto.reference,
        description: dto.description,
      });
      return receipt.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Get("receipts")
  @ApiOperation({ summary: "List cash receipts" })
  async listReceipts(
    @Query("cashBoxId") cashBoxId?: string,
    @Query("sessionId") sessionId?: string,
    @Query("fromDate") fromDate?: string,
    @Query("toDate") toDate?: string,
  ) {
    if (cashBoxId) return (await this.receiptRepo.findByCashBox(cashBoxId)).map(r => r.toState());
    if (sessionId) return (await this.receiptRepo.findBySession(sessionId)).map(r => r.toState());
    if (fromDate || toDate) {
      return (await this.receiptRepo.findByDateRange(
        fromDate ? new Date(fromDate) : new Date(0),
        toDate ? new Date(toDate) : new Date("2100-01-01"),
      )).map(r => r.toState());
    }
    return (await this.receiptRepo.findAll()).map(r => r.toState());
  }

  @Get("receipts/:id")
  @ApiOperation({ summary: "Get receipt by ID" })
  async getReceipt(@Param("id") id: string) {
    const r = await this.receiptRepo.findById(new CashReceiptId(id));
    if (!r) throw new NotFoundException("Receipt not found");
    return r.toState();
  }

  @Put("receipts/:id/reverse")
  @ApiOperation({ summary: "Reverse a posted receipt" })
  async reverseReceipt(@Param("id") id: string, @Body() dto: ReverseDto) {
    const r = await this.receiptRepo.findById(new CashReceiptId(id));
    if (!r) throw new NotFoundException("Receipt not found");
    try {
      r.reverse(dto.userId, dto.reason);
      await this.receiptRepo.save(r);
      return r.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  // ─── Cash Payments ──────────────────────────────────────────────────────────

  @Post("payments")
  @ApiOperation({ summary: "Record a cash payment" })
  async createPayment(@Body() dto: CreatePaymentDto) {
    try {
      const payment = await this.cashBoxService.recordPayment({
        paymentNumber: dto.paymentNumber,
        paymentDate: new Date(dto.paymentDate),
        cashBoxId: dto.cashBoxId,
        cashierId: dto.cashierId,
        payeeName: dto.payeeName,
        amount: dto.amount,
        currencyCode: dto.currencyCode,
        paymentMethod: dto.paymentMethod,
        sessionId: dto.sessionId,
        reference: dto.reference,
        description: dto.description,
      });
      return payment.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Get("payments")
  @ApiOperation({ summary: "List cash payments" })
  async listPayments(
    @Query("cashBoxId") cashBoxId?: string,
    @Query("fromDate") fromDate?: string,
    @Query("toDate") toDate?: string,
  ) {
    if (cashBoxId) return (await this.paymentRepo.findByCashBox(cashBoxId)).map(p => p.toState());
    if (fromDate || toDate) {
      return (await this.paymentRepo.findByDateRange(
        fromDate ? new Date(fromDate) : new Date(0),
        toDate ? new Date(toDate) : new Date("2100-01-01"),
      )).map(p => p.toState());
    }
    return (await this.paymentRepo.findAll()).map(p => p.toState());
  }

  @Get("payments/:id")
  @ApiOperation({ summary: "Get payment by ID" })
  async getPayment(@Param("id") id: string) {
    const p = await this.paymentRepo.findById(new CashPaymentId(id));
    if (!p) throw new NotFoundException("Payment not found");
    return p.toState();
  }

  @Put("payments/:id/reverse")
  @ApiOperation({ summary: "Reverse a posted payment" })
  async reversePayment(@Param("id") id: string, @Body() dto: ReverseDto) {
    const p = await this.paymentRepo.findById(new CashPaymentId(id));
    if (!p) throw new NotFoundException("Payment not found");
    try {
      p.reverse(dto.userId, dto.reason);
      await this.paymentRepo.save(p);
      return p.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  // ─── Cash Advances ──────────────────────────────────────────────────────────

  @Post("advances")
  @ApiOperation({ summary: "Create cash advance" })
  async createAdvance(@Body() dto: CreateCashAdvanceDto) {
    const advance = CashAdvance.create({
      advanceNumber: dto.advanceNumber,
      companyId: dto.companyId,
      employeeId: dto.employeeId,
      employeeName: dto.employeeName,
      amount: dto.amount,
      advanceDate: new Date(dto.advanceDate),
      purpose: dto.purpose,
      currencyCode: dto.currencyCode,
      expectedSettleDate: dto.expectedSettleDate ? new Date(dto.expectedSettleDate) : null,
    });
    await this.advanceRepo.save(advance);
    return advance.toState();
  }

  @Get("advances")
  @ApiOperation({ summary: "List cash advances" })
  async listAdvances(@Query("employeeId") employeeId?: string) {
    if (employeeId) return (await this.advanceRepo.findByEmployee(employeeId)).map(a => a.toState());
    return (await this.advanceRepo.findAll()).map(a => a.toState());
  }

  @Get("advances/:id")
  @ApiOperation({ summary: "Get advance by ID" })
  async getAdvance(@Param("id") id: string) {
    const a = await this.advanceRepo.findById(new CashAdvanceId(id));
    if (!a) throw new NotFoundException("Advance not found");
    return a.toState();
  }

  @Put("advances/:id/approve")
  @ApiOperation({ summary: "Approve cash advance" })
  async approveAdvance(@Param("id") id: string, @Body() dto: ApproveDto) {
    const a = await this.advanceRepo.findById(new CashAdvanceId(id));
    if (!a) throw new NotFoundException("Advance not found");
    try {
      a.approve(dto.userId);
      await this.advanceRepo.save(a);
      return a.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Put("advances/:id/disburse")
  @ApiOperation({ summary: "Disburse cash advance" })
  async disburseAdvance(@Param("id") id: string, @Body() dto: ApproveDto) {
    const a = await this.advanceRepo.findById(new CashAdvanceId(id));
    if (!a) throw new NotFoundException("Advance not found");
    try {
      a.disburse(dto.userId);
      await this.advanceRepo.save(a);
      return a.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  // ─── Cash Transfers ─────────────────────────────────────────────────────────

  @Post("transfers")
  @ApiOperation({ summary: "Create cash transfer" })
  async createTransfer(@Body() dto: CreateCashTransferDto) {
    try {
      const transfer = CashTransfer.create({
        transferNumber: dto.transferNumber,
        fromLocationId: dto.fromLocationId,
        toLocationId: dto.toLocationId,
        amount: dto.amount,
        transferDate: new Date(dto.transferDate),
        currencyCode: dto.currencyCode,
        reference: dto.reference,
      });
      await this.transferRepo.save(transfer);
      return transfer.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Get("transfers")
  @ApiOperation({ summary: "List cash transfers" })
  async listTransfers() {
    return (await this.transferRepo.findAll()).map(t => t.toState());
  }

  @Put("transfers/:id/send")
  @ApiOperation({ summary: "Send cash transfer" })
  async sendTransfer(@Param("id") id: string, @Body() dto: ApproveDto) {
    const t = await this.transferRepo.findById(new CashTransferId(id));
    if (!t) throw new NotFoundException("Transfer not found");
    try {
      t.approve(dto.userId);
      t.send(dto.userId);
      await this.transferRepo.save(t);
      return t.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Put("transfers/:id/receive")
  @ApiOperation({ summary: "Receive cash transfer" })
  async receiveTransfer(@Param("id") id: string, @Body() dto: ApproveDto) {
    const t = await this.transferRepo.findById(new CashTransferId(id));
    if (!t) throw new NotFoundException("Transfer not found");
    try {
      t.receive(dto.userId);
      await this.transferRepo.save(t);
      return t.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  // ─── Petty Cash ─────────────────────────────────────────────────────────────

  @Post("petty-cash")
  @ApiOperation({ summary: "Create petty cash fund" })
  async createPettyCash(@Body() dto: CreatePettyCashDto) {
    const fund = PettyCash.create({
      locationId: dto.locationId,
      fundCode: dto.fundCode,
      fundName: dto.fundName,
      maximumBalance: dto.maximumBalance,
      minimumBalance: dto.minimumBalance,
      currencyCode: dto.currencyCode,
      holderId: dto.holderId,
    });
    await this.pettyCashRepo.save(fund);
    return fund.toState();
  }

  @Get("petty-cash")
  @ApiOperation({ summary: "List petty cash funds" })
  async listPettyCash() {
    return (await this.pettyCashRepo.findAll()).map(f => f.toState());
  }

  @Get("petty-cash/:id")
  @ApiOperation({ summary: "Get petty cash fund" })
  async getPettyCash(@Param("id") id: string) {
    const f = await this.pettyCashRepo.findById(new PettyCashId(id));
    if (!f) throw new NotFoundException("Petty cash fund not found");
    return f.toState();
  }
}
