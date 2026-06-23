import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaBankRepository, PrismaBankAccountRepository, PrismaBankTransferRepository, PrismaBankStatementRepository, PrismaBankReconciliationRepository, PrismaChequeBookRepository } from "../../infrastructure/cm/cm-prisma-repos.js";
import { BankService } from "../../application/cm/cm-bank-service.js";
import { Bank, BankAccount } from "../../domain/cm/cm-bank.js";
import { BankTransfer } from "../../domain/cm/cm-bank-transfer.js";
import { BankStatement, BankReconciliation } from "../../domain/cm/cm-bank-statement.js";
import { ChequeBook } from "../../domain/cm/cm-cheque.js";
import { BankId, BankAccountId, BankTransferId, BankStatementId, BankReconciliationId, ChequeBookId } from "../../domain/cm/cm-ids.js";
import { DomainError } from "../../shared/domain-error.js";
import { CreateBankDto, CreateBankAccountDto, CreateBankTransferDto, ImportStatementDto, ApproveDto } from "./dto/cm.dto.js";

@ApiTags("CM - Bank Management")
@Controller("api/cm/banks")
export class BankController {
  constructor(
    private readonly bankRepo: PrismaBankRepository,
    private readonly accountRepo: PrismaBankAccountRepository,
    private readonly transferRepo: PrismaBankTransferRepository,
    private readonly statementRepo: PrismaBankStatementRepository,
    private readonly reconciliationRepo: PrismaBankReconciliationRepository,
    private readonly chequeBookRepo: PrismaChequeBookRepository,
    private readonly bankService: BankService,
  ) {}

  // ─── Bank CRUD ──────────────────────────────────────────────────────────────

  @Post()
  @ApiOperation({ summary: "Create a bank" })
  async createBank(@Body() dto: CreateBankDto) {
    const bank = Bank.create(dto);
    await this.bankRepo.save(bank);
    return bank.toState();
  }

  @Get()
  @ApiOperation({ summary: "List banks" })
  async listBanks() {
    return (await this.bankRepo.findAll()).map(b => b.toState());
  }

  @Get(":id")
  @ApiOperation({ summary: "Get bank by ID" })
  async getBank(@Param("id") id: string) {
    const b = await this.bankRepo.findById(new BankId(id));
    if (!b) throw new NotFoundException("Bank not found");
    return b.toState();
  }

  // ─── Bank Accounts ──────────────────────────────────────────────────────────

  @Post(":bankId/accounts")
  @ApiOperation({ summary: "Create bank account" })
  async createAccount(@Param("bankId") bankId: string, @Body() dto: CreateBankAccountDto) {
    const account = await this.bankService.createAccount({
      ...dto,
      bankId,
      openingDate: new Date(dto.openingDate),
    });
    return account.toState();
  }

  @Get("accounts")
  @ApiOperation({ summary: "List all bank accounts" })
  async listAccounts(@Query("companyId") companyId?: string) {
    if (companyId) return (await this.accountRepo.findByCompany(companyId)).map(a => a.toState());
    return (await this.accountRepo.findAll()).map(a => a.toState());
  }

  @Get("accounts/:id")
  @ApiOperation({ summary: "Get bank account by ID" })
  async getAccount(@Param("id") id: string) {
    const a = await this.accountRepo.findById(new BankAccountId(id));
    if (!a) throw new NotFoundException("Bank account not found");
    return a.toState();
  }

  // ─── Bank Transfers ─────────────────────────────────────────────────────────

  @Post("transfers")
  @ApiOperation({ summary: "Create bank transfer" })
  async createTransfer(@Body() dto: CreateBankTransferDto) {
    try {
      const transfer = await this.bankService.createTransfer({
        ...dto,
        transferDate: new Date(dto.transferDate),
      });
      return transfer.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Get("transfers")
  @ApiOperation({ summary: "List bank transfers" })
  async listTransfers() {
    return (await this.transferRepo.findAll()).map(t => t.toState());
  }

  @Get("transfers/:id")
  @ApiOperation({ summary: "Get bank transfer by ID" })
  async getTransfer(@Param("id") id: string) {
    const t = await this.transferRepo.findById(new BankTransferId(id));
    if (!t) throw new NotFoundException("Transfer not found");
    return t.toState();
  }

  @Put("transfers/:id/approve")
  @ApiOperation({ summary: "Approve bank transfer" })
  async approveTransfer(@Param("id") id: string, @Body() dto: ApproveDto) {
    const t = await this.transferRepo.findById(new BankTransferId(id));
    if (!t) throw new NotFoundException("Transfer not found");
    try {
      t.approve(dto.userId);
      await this.transferRepo.save(t);
      return t.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Put("transfers/:id/complete")
  @ApiOperation({ summary: "Complete bank transfer (debit/credit accounts)" })
  async completeTransfer(@Param("id") id: string, @Body() dto: ApproveDto) {
    try {
      const transfer = await this.bankService.completeTransfer(id, dto.userId);
      return transfer.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  // ─── Bank Statements ────────────────────────────────────────────────────────

  @Post("statements/import")
  @ApiOperation({ summary: "Import bank statement" })
  async importStatement(@Body() dto: ImportStatementDto) {
    try {
      const statement = await this.bankService.importStatement({
        bankAccountId: dto.bankAccountId,
        statementNumber: dto.statementNumber,
        periodStart: new Date(dto.periodStart),
        periodEnd: new Date(dto.periodEnd),
        openingBalance: dto.openingBalance,
        closingBalance: dto.closingBalance,
        lines: dto.lines.map(l => ({
          lineDate: new Date(l.lineDate),
          description: l.description ?? null,
          reference: l.reference ?? null,
          chequeNumber: l.chequeNumber ?? null,
          lineType: l.lineType,
          amount: l.amount,
          runningBalance: l.runningBalance,
        })),
      });
      return statement.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }

  @Get("statements")
  @ApiOperation({ summary: "List bank statements" })
  async listStatements(@Query("bankAccountId") bankAccountId?: string) {
    if (bankAccountId) return (await this.statementRepo.findByBankAccount(bankAccountId)).map(s => s.toState());
    return (await this.statementRepo.findAll()).map(s => s.toState());
  }

  @Get("statements/:id")
  @ApiOperation({ summary: "Get bank statement by ID" })
  async getStatement(@Param("id") id: string) {
    const s = await this.statementRepo.findById(new BankStatementId(id));
    if (!s) throw new NotFoundException("Statement not found");
    return s.toState();
  }

  // ─── Bank Reconciliation ────────────────────────────────────────────────────

  @Post("reconciliations")
  @ApiOperation({ summary: "Create bank reconciliation" })
  async createReconciliation(@Body() body: { bankAccountId: string; bankStatementId: string; reconciliationNumber: string; reconciliationDate: string; statementBalance: number; bookBalance: number }) {
    const rec = await this.bankService.createReconciliation({
      bankAccountId: body.bankAccountId,
      bankStatementId: body.bankStatementId,
      reconciliationNumber: body.reconciliationNumber,
      reconciliationDate: new Date(body.reconciliationDate),
      statementBalance: body.statementBalance,
      bookBalance: body.bookBalance,
    });
    return rec.toState();
  }

  @Get("reconciliations")
  @ApiOperation({ summary: "List reconciliations" })
  async listReconciliations() {
    return (await this.reconciliationRepo.findAll()).map(r => r.toState());
  }

  @Put("reconciliations/:id/approve")
  @ApiOperation({ summary: "Approve bank reconciliation" })
  async approveReconciliation(@Param("id") id: string, @Body() dto: ApproveDto) {
    try {
      const rec = await this.bankService.approveReconciliation(id, dto.userId);
      return rec.toState();
    } catch (e) {
      if (e instanceof DomainError) throw new BadRequestException(e.message);
      throw e;
    }
  }
}
