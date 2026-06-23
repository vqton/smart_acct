import { Controller, Get, Post, Put, Param, Body, Query, NotFoundException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { BankMasterService } from "../../application/bank/bank-master-service.js";
import { BankAccountService } from "../../application/bank/bank-account-service.js";
import { BankTransactionService } from "../../application/bank/bank-transaction-service.js";
import { DomainError } from "../../shared/domain-error.js";
import {
  CreateBankGroupDto, CreateBankDto, UpdateBankDto, CreateBankBranchDto,
  CreateCorrespondentBankDto, CreateBankAccountDto, SuspendAccountDto,
  BlockAccountDto, CloseAccountDto, AddSignerDto, AddAccountLimitDto,
  AddAccountMappingDto, CreateTransactionDto, ImportStatementDto,
  CreateReconciliationDto, MatchReconciliationItemDto, CreatePaymentRequestDto,
  RejectPaymentRequestDto, CreatePaymentBatchDto, CreateRecurringPaymentDto,
  CreateCashPositionDto, CreateFXRevaluationDto, UserActionDto, ReasonDto,
} from "./dto/bank.dto.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) throw new BadRequestException(e.message);
  throw e;
}

@ApiTags("Bank Management")
@Controller("api/bank")
export class BankMasterController {
  constructor(
    private readonly masterService: BankMasterService,
    private readonly accountService: BankAccountService,
    private readonly txService: BankTransactionService,
  ) {}

  // ─── Bank Groups ─────────────────────────────────────────────────────────────

  @Post("groups")
  @ApiOperation({ summary: "Create bank group" })
  async createGroup(@Body() dto: CreateBankGroupDto) {
    try { return (await this.masterService.createGroup(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("groups")
  @ApiOperation({ summary: "List bank groups" })
  async listGroups() {
    return (await this.masterService.listGroups()).map(g => g.toState());
  }

  @Get("groups/:id")
  @ApiOperation({ summary: "Get bank group by ID" })
  async getGroup(@Param("id") id: string) {
    const g = await this.masterService.getGroup(id);
    if (!g) throw new NotFoundException("Bank group not found");
    return g.toState();
  }

  @Put("groups/:id/deactivate")
  @ApiOperation({ summary: "Deactivate bank group" })
  async deactivateGroup(@Param("id") id: string) {
    try { return (await this.masterService.deactivateGroup(id)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Banks ───────────────────────────────────────────────────────────────────

  @Post("banks")
  @ApiOperation({ summary: "Create bank" })
  async createBank(@Body() dto: CreateBankDto) {
    try { return (await this.masterService.createBank(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("banks")
  @ApiOperation({ summary: "List banks" })
  async listBanks() {
    return (await this.masterService.listBanks()).map(b => b.toState());
  }

  @Get("banks/:id")
  @ApiOperation({ summary: "Get bank by ID" })
  async getBank(@Param("id") id: string) {
    const b = await this.masterService.getBank(id);
    if (!b) throw new NotFoundException("Bank not found");
    return b.toState();
  }

  @Put("banks/:id")
  @ApiOperation({ summary: "Update bank" })
  async updateBank(@Param("id") id: string, @Body() dto: UpdateBankDto) {
    try { return (await this.masterService.updateBank(id, dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("banks/:id/activate")
  @ApiOperation({ summary: "Activate bank" })
  async activateBank(@Param("id") id: string) {
    try { return (await this.masterService.activateBank(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("banks/:id/deactivate")
  @ApiOperation({ summary: "Deactivate bank" })
  async deactivateBank(@Param("id") id: string) {
    try { return (await this.masterService.deactivateBank(id)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Bank Branches ───────────────────────────────────────────────────────────

  @Post("branches")
  @ApiOperation({ summary: "Create bank branch" })
  async createBranch(@Body() dto: CreateBankBranchDto) {
    try { return (await this.masterService.createBranch(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("branches")
  @ApiOperation({ summary: "List branches" })
  async listBranches(@Query("bankId") bankId?: string) {
    return (await this.masterService.listBranches(bankId)).map(b => b.toState());
  }

  @Put("branches/:id/deactivate")
  @ApiOperation({ summary: "Deactivate branch" })
  async deactivateBranch(@Param("id") id: string) {
    try { return (await this.masterService.deactivateBranch(id)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Correspondent Banks ──────────────────────────────────────────────────────

  @Post("correspondents")
  @ApiOperation({ summary: "Create correspondent bank relationship" })
  async createCorrespondent(@Body() dto: CreateCorrespondentBankDto) {
    try { return (await this.masterService.createCorrespondent(dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("correspondents")
  @ApiOperation({ summary: "List correspondent banks" })
  async listCorrespondents(@Query("bankId") bankId?: string) {
    return (await this.masterService.listCorrespondents(bankId)).map(c => c.toState());
  }

  // ─── Bank Accounts ────────────────────────────────────────────────────────────

  @Post("accounts")
  @ApiOperation({ summary: "Create bank account" })
  async createAccount(@Body() dto: CreateBankAccountDto) {
    try {
      return (await this.accountService.createAccount({
        ...dto, openingDate: dto.openingDate ? new Date(dto.openingDate) : new Date(),
      })).toState();
    } catch (e) { handleError(e); }
  }

  @Get("accounts")
  @ApiOperation({ summary: "List bank accounts" })
  async listAccounts(@Query("companyId") companyId?: string) {
    return (await this.accountService.listAccounts(companyId)).map(a => a.toState());
  }

  @Get("accounts/:id")
  @ApiOperation({ summary: "Get bank account by ID" })
  async getAccount(@Param("id") id: string) {
    const a = await this.accountService.getAccount(id);
    if (!a) throw new NotFoundException("Bank account not found");
    return a.toState();
  }

  @Put("accounts/:id/activate")
  @ApiOperation({ summary: "Activate bank account" })
  async activateAccount(@Param("id") id: string) {
    try { return (await this.accountService.activateAccount(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("accounts/:id/suspend")
  @ApiOperation({ summary: "Suspend bank account" })
  async suspendAccount(@Param("id") id: string, @Body() dto: SuspendAccountDto) {
    try { return (await this.accountService.suspendAccount(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("accounts/:id/block")
  @ApiOperation({ summary: "Block bank account" })
  async blockAccount(@Param("id") id: string, @Body() dto: BlockAccountDto) {
    try { return (await this.accountService.blockAccount(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("accounts/:id/close")
  @ApiOperation({ summary: "Close bank account" })
  async closeAccount(@Param("id") id: string, @Body() dto: CloseAccountDto) {
    try { return (await this.accountService.closeAccount(id, dto?.force ?? false)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Authorized Signers ─────────────────────────────────────────────────────

  @Post("accounts/:accountId/signers")
  @ApiOperation({ summary: "Add authorized signer" })
  async addSigner(@Param("accountId") accountId: string, @Body() dto: AddSignerDto) {
    try { return (await this.accountService.addSigner(accountId, dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("accounts/:accountId/signers")
  @ApiOperation({ summary: "List authorized signers" })
  async listSigners(@Param("accountId") accountId: string) {
    return (await this.accountService.listSigners(accountId)).map(s => s.toState());
  }

  @Put("signers/:id/deactivate")
  @ApiOperation({ summary: "Deactivate authorized signer" })
  async deactivateSigner(@Param("id") id: string) {
    try { return (await this.accountService.deactivateSigner(id)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Account Limits ─────────────────────────────────────────────────────────

  @Post("accounts/:accountId/limits")
  @ApiOperation({ summary: "Add account limit" })
  async addLimit(@Param("accountId") accountId: string, @Body() dto: AddAccountLimitDto) {
    try { return (await this.accountService.addLimit(accountId, dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Get("accounts/:accountId/limits")
  @ApiOperation({ summary: "List account limits" })
  async listLimits(@Param("accountId") accountId: string) {
    return (await this.accountService.listLimits(accountId)).map(l => l.toState());
  }

  // ─── Account Mappings ───────────────────────────────────────────────────────

  @Post("accounts/:accountId/mappings")
  @ApiOperation({ summary: "Add account mapping" })
  async addMapping(@Param("accountId") accountId: string, @Body() dto: AddAccountMappingDto) {
    try { return (await this.accountService.addMapping(accountId, dto)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Transactions ───────────────────────────────────────────────────────────

  @Post("transactions")
  @ApiOperation({ summary: "Create bank transaction" })
  async createTransaction(@Body() dto: CreateTransactionDto) {
    try {
      return (await this.txService.createTransaction({
        ...dto, transactionDate: new Date(dto.transactionDate),
      })).toState();
    } catch (e) { handleError(e); }
  }

  @Get("transactions")
  @ApiOperation({ summary: "List transactions" })
  async listTransactions(@Query("accountId") accountId?: string) {
    return (await this.txService.listTransactions(accountId)).map(t => t.toState());
  }

  @Get("transactions/:id")
  @ApiOperation({ summary: "Get transaction by ID" })
  async getTransaction(@Param("id") id: string) {
    const t = await this.txService.getTransaction(id);
    if (!t) throw new NotFoundException("Transaction not found");
    return t.toState();
  }

  @Put("transactions/:id/authorize")
  @ApiOperation({ summary: "Authorize transaction" })
  async authorizeTransaction(@Param("id") id: string, @Body() dto: UserActionDto) {
    try { return (await this.txService.authorizeTransaction(id, dto.userId)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("transactions/:id/approve")
  @ApiOperation({ summary: "Approve transaction" })
  async approveTransaction(@Param("id") id: string, @Body() dto: UserActionDto) {
    try { return (await this.txService.approveTransaction(id, dto.userId)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("transactions/:id/execute")
  @ApiOperation({ summary: "Execute transaction (debit source)" })
  async executeTransaction(@Param("id") id: string, @Body() dto: UserActionDto) {
    try { return (await this.txService.executeTransaction(id, dto.userId)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("transactions/:id/complete")
  @ApiOperation({ summary: "Complete transaction (credit destination)" })
  async completeTransaction(@Param("id") id: string) {
    try { return (await this.txService.completeTransaction(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("transactions/:id/fail")
  @ApiOperation({ summary: "Mark transaction as failed" })
  async failTransaction(@Param("id") id: string, @Body() dto: ReasonDto) {
    try { return (await this.txService.failTransaction(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("transactions/:id/reverse")
  @ApiOperation({ summary: "Reverse transaction" })
  async reverseTransaction(@Param("id") id: string, @Body() dto: ReasonDto) {
    try { return (await this.txService.reverseTransaction(id, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Bank Statements ─────────────────────────────────────────────────────────

  @Post("statements/import")
  @ApiOperation({ summary: "Import bank statement" })
  async importStatement(@Body() dto: ImportStatementDto) {
    try {
      return (await this.txService.importStatement({
        ...dto,
        periodStart: new Date(dto.periodStart), periodEnd: new Date(dto.periodEnd),
        lines: dto.lines.map(l => ({ ...l, lineDate: new Date(l.lineDate) })),
      })).toState();
    } catch (e) { handleError(e); }
  }

  @Get("statements")
  @ApiOperation({ summary: "List bank statements" })
  async listStatements(@Query("bankAccountId") bankAccountId?: string) {
    return (await this.txService.listStatements(bankAccountId)).map(s => s.toState());
  }

  @Get("statements/:id")
  @ApiOperation({ summary: "Get bank statement by ID" })
  async getStatement(@Param("id") id: string) {
    const s = await this.txService.getStatement(id);
    if (!s) throw new NotFoundException("Statement not found");
    return s.toState();
  }

  @Put("statements/:id/lock")
  @ApiOperation({ summary: "Lock bank statement" })
  async lockStatement(@Param("id") id: string) {
    try { return (await this.txService.lockStatement(id)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("statements/:id/unlock")
  @ApiOperation({ summary: "Unlock bank statement" })
  async unlockStatement(@Param("id") id: string) {
    try { return (await this.txService.unlockStatement(id)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Bank Reconciliation ─────────────────────────────────────────────────────

  @Post("reconciliations")
  @ApiOperation({ summary: "Create reconciliation" })
  async createReconciliation(@Body() dto: CreateReconciliationDto) {
    try {
      return (await this.txService.createReconciliation({
        ...dto, reconciliationDate: new Date(dto.reconciliationDate),
      })).toState();
    } catch (e) { handleError(e); }
  }

  @Get("reconciliations")
  @ApiOperation({ summary: "List reconciliations" })
  async listReconciliations(@Query("bankAccountId") bankAccountId?: string) {
    return (await this.txService.listReconciliations(bankAccountId)).map(r => r.toState());
  }

  @Get("reconciliations/:id")
  @ApiOperation({ summary: "Get reconciliation by ID" })
  async getReconciliation(@Param("id") id: string) {
    const r = await this.txService.getReconciliation(id);
    if (!r) throw new NotFoundException("Reconciliation not found");
    return r.toState();
  }

  @Post("reconciliations/:id/match")
  @ApiOperation({ summary: "Add matched item to reconciliation" })
  async matchReconciliationItem(@Param("id") id: string, @Body() dto: MatchReconciliationItemDto) {
    try { return (await this.txService.matchReconciliationItem(id, dto)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("reconciliations/:id/resolve")
  @ApiOperation({ summary: "Resolve reconciliation" })
  async resolveReconciliation(@Param("id") id: string, @Body() dto: UserActionDto) {
    try { return (await this.txService.resolveReconciliation(id, dto.userId)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("reconciliations/:id/approve")
  @ApiOperation({ summary: "Approve and close reconciliation" })
  async approveReconciliation(@Param("id") id: string, @Body() dto: UserActionDto) {
    try { return (await this.txService.approveReconciliation(id, dto.userId)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Payment Requests ────────────────────────────────────────────────────────

  @Post("payment-requests")
  @ApiOperation({ summary: "Create payment request" })
  async createPaymentRequest(@Body() dto: CreatePaymentRequestDto) {
    try {
      return (await this.txService.createPaymentRequest({
        ...dto, paymentDate: new Date(dto.paymentDate),
      })).toState();
    } catch (e) { handleError(e); }
  }

  @Get("payment-requests")
  @ApiOperation({ summary: "List payment requests" })
  async listPaymentRequests() {
    return (await this.txService.listTransactions()).map(t => t.toState()); // simplified
  }

  @Put("payment-requests/:id/approve")
  @ApiOperation({ summary: "Approve payment request" })
  async approvePaymentRequest(@Param("id") id: string, @Body() dto: UserActionDto) {
    try { return (await this.txService.approvePaymentRequest(id, dto.userId)).toState(); }
    catch (e) { handleError(e); }
  }

  @Put("payment-requests/:id/reject")
  @ApiOperation({ summary: "Reject payment request" })
  async rejectPaymentRequest(@Param("id") id: string, @Body() dto: RejectPaymentRequestDto) {
    try { return (await this.txService.rejectPaymentRequest(id, dto.userId, dto.reason)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Payment Batches ──────────────────────────────────────────────────────────

  @Post("payment-batches")
  @ApiOperation({ summary: "Create payment batch" })
  async createPaymentBatch(@Body() dto: CreatePaymentBatchDto) {
    try {
      return (await this.txService.createPaymentBatch({
        ...dto, paymentDate: new Date(dto.paymentDate),
      })).toState();
    } catch (e) { handleError(e); }
  }

  @Put("payment-batches/:id/release")
  @ApiOperation({ summary: "Validate, approve, and release payment batch" })
  async releasePaymentBatch(@Param("id") id: string, @Body() dto: UserActionDto) {
    try { return (await this.txService.releasePaymentBatch(id, dto.userId)).toState(); }
    catch (e) { handleError(e); }
  }

  // ─── Recurring Payments ───────────────────────────────────────────────────────

  @Post("recurring-payments")
  @ApiOperation({ summary: "Create recurring payment" })
  async createRecurringPayment(@Body() dto: CreateRecurringPaymentDto) {
    try {
      return (await this.txService.createRecurringPayment({
        ...dto, startDate: new Date(dto.startDate),
      })).toState();
    } catch (e) { handleError(e); }
  }

  @Post("recurring-payments/process-due")
  @ApiOperation({ summary: "Process due recurring payments" })
  async processDueRecurringPayments() {
    return this.txService.processDueRecurringPayments();
  }

  // ─── Cash Positions ─────────────────────────────────────────────────────────

  @Post("cash-positions")
  @ApiOperation({ summary: "Create cash position" })
  async createCashPosition(@Body() dto: CreateCashPositionDto) {
    try {
      return (await this.txService.createCashPosition({
        ...dto, positionDate: new Date(dto.positionDate),
      })).toState();
    } catch (e) { handleError(e); }
  }

  // ─── FX Revaluation ─────────────────────────────────────────────────────────

  @Post("fx-revaluations")
  @ApiOperation({ summary: "Create FX revaluation" })
  async createFXRevaluation(@Body() dto: CreateFXRevaluationDto) {
    try {
      return (await this.txService.createFXRevaluation({
        ...dto, revaluationDate: new Date(dto.revaluationDate),
      })).toState();
    } catch (e) { handleError(e); }
  }

  @Put("fx-revaluations/:id/post-gl")
  @ApiOperation({ summary: "Post FX revaluation to GL" })
  async postFXRevaluationToGL(@Param("id") id: string, @Body() body: { glBatchId: string }) {
    try { return (await this.txService.postFXRevaluationToGL(id, body.glBatchId)).toState(); }
    catch (e) { handleError(e); }
  }
}
