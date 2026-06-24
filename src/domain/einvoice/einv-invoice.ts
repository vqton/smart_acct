import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { EinvInvoiceId, EinvInvoiceLineId } from "./einv-ids.js";
import { EinvInvoiceStatus, EinvInvoiceCategory } from "./einv-enums.js";
import {
  EinvInvoiceCreated, EinvInvoiceSubmitted, EinvInvoiceApproved,
  EinvInvoiceSigned, EinvInvoiceIssued, EinvInvoiceSubmittedToTaxAuthority,
  EinvInvoiceAccepted, EinvInvoiceRejected, EinvInvoiceReplaced,
  EinvInvoiceAdjusted, EinvInvoiceCancelled, EinvInvoiceArchived,
  EinvInvoiceRestored, EinvInvoiceExpired,
} from "./einv-events.js";

// ─── Invoice Line ──────────────────────────────────────────────────────────────

export interface EinvInvoiceLineState {
  id: string; invoiceId: string; lineNumber: number;
  itemCode: string; itemName: string; unit: string;
  quantity: number; unitPrice: bigint; totalPrice: bigint;
  discountPercent: number; discountAmount: bigint;
  taxCode: string | null; taxRate: number; taxAmount: bigint; netAmount: bigint;
  salesLineId: string | null; itemId: string | null; description: string | null;
}

export class EinvInvoiceLine extends AggregateRoot<EinvInvoiceLineId> {
  private _id: EinvInvoiceLineId;
  private _invoiceId: string;
  private _lineNumber: number;
  private _itemCode: string;
  private _itemName: string;
  private _unit: string;
  private _quantity: number;
  private _unitPrice: bigint;
  private _totalPrice: bigint;
  private _discountPercent: number;
  private _discountAmount: bigint;
  private _taxCode: string | null;
  private _taxRate: number;
  private _taxAmount: bigint;
  private _netAmount: bigint;
  private _salesLineId: string | null;
  private _itemId: string | null;
  private _description: string | null;

  private constructor(id: EinvInvoiceLineId, invoiceId: string, lineNumber: number, itemCode: string, itemName: string, unit: string, quantity: number, unitPrice: bigint) {
    super();
    this._id = id; this._invoiceId = invoiceId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._unit = unit;
    this._quantity = quantity; this._unitPrice = unitPrice;
    this._totalPrice = BigInt(Math.round(Number(quantity) * Number(unitPrice)));
    this._discountPercent = 0; this._discountAmount = 0n;
    this._taxCode = null; this._taxRate = 0; this._taxAmount = 0n;
    this._netAmount = this._totalPrice;
    this._salesLineId = null; this._itemId = null; this._description = null;
  }

  static create(p: {
    invoiceId: string; lineNumber: number; itemCode: string; itemName: string;
    unit: string; quantity: number; unitPrice: bigint;
    discountPercent?: number; discountAmount?: bigint;
    taxCode?: string; taxRate?: number;
    salesLineId?: string; itemId?: string; description?: string;
  }): EinvInvoiceLine {
    const l = new EinvInvoiceLine(EinvInvoiceLineId.new(), p.invoiceId, p.lineNumber, p.itemCode, p.itemName, p.unit, p.quantity, p.unitPrice);
    if (p.discountPercent) { l._discountPercent = p.discountPercent; l._discountAmount = BigInt(Math.round(Number(l._totalPrice) * p.discountPercent / 100)); }
    if (p.discountAmount) l._discountAmount = p.discountAmount;
    l._taxCode = p.taxCode ?? null; l._taxRate = p.taxRate ?? 0;
    l._taxAmount = BigInt(Math.round(Number(l._totalPrice - l._discountAmount) * l._taxRate / 100));
    l._netAmount = l._totalPrice - l._discountAmount + l._taxAmount;
    l._salesLineId = p.salesLineId ?? null; l._itemId = p.itemId ?? null;
    l._description = p.description ?? null;
    return l;
  }

  static load(s: EinvInvoiceLineState): EinvInvoiceLine {
    const l = new EinvInvoiceLine(new EinvInvoiceLineId(s.id), s.invoiceId, s.lineNumber, s.itemCode, s.itemName, s.unit, s.quantity, s.unitPrice);
    l._totalPrice = s.totalPrice; l._discountPercent = s.discountPercent;
    l._discountAmount = s.discountAmount; l._taxCode = s.taxCode;
    l._taxRate = s.taxRate; l._taxAmount = s.taxAmount; l._netAmount = s.netAmount;
    l._salesLineId = s.salesLineId; l._itemId = s.itemId; l._description = s.description;
    return l;
  }

  get id() { return this._id; }
  get lineNumber() { return this._lineNumber; }
  get itemCode() { return this._itemCode; }
  get itemName() { return this._itemName; }
  get quantity() { return this._quantity; }
  get unitPrice() { return this._unitPrice; }
  get totalPrice() { return this._totalPrice; }
  get discountAmount() { return this._discountAmount; }
  get taxCode() { return this._taxCode; }
  get taxRate() { return this._taxRate; }
  get taxAmount() { return this._taxAmount; }
  get netAmount() { return this._netAmount; }

  toState(): EinvInvoiceLineState {
    return { id: this._id.value, invoiceId: this._invoiceId, lineNumber: this._lineNumber,
      itemCode: this._itemCode, itemName: this._itemName, unit: this._unit,
      quantity: this._quantity, unitPrice: this._unitPrice, totalPrice: this._totalPrice,
      discountPercent: this._discountPercent, discountAmount: this._discountAmount,
      taxCode: this._taxCode, taxRate: this._taxRate, taxAmount: this._taxAmount,
      netAmount: this._netAmount, salesLineId: this._salesLineId, itemId: this._itemId,
      description: this._description };
  }
}

// ─── Invoice Aggregate ─────────────────────────────────────────────────────────

export interface EinvInvoiceState {
  id: string; salesInvoiceId: string | null;
  invoiceNumber: string; invoiceCode: string | null; invoiceSymbol: string | null;
  invoiceName: string | null;
  invoiceTypeId: string; templateId: string; seriesId: string | null;
  providerId: string | null;
  sellerName: string; sellerTaxCode: string; sellerAddress: string | null;
  sellerPhone: string | null; sellerEmail: string | null;
  sellerBankName: string | null; sellerBankAccount: string | null;
  buyerName: string; buyerTaxCode: string | null; buyerAddress: string | null;
  buyerPhone: string | null; buyerEmail: string | null;
  buyerBankName: string | null; buyerBankAccount: string | null;
  currencyCode: string; exchangeRate: number;
  subtotal: bigint; discountAmount: bigint; taxAmount: bigint; grandTotal: bigint;
  amountInWords: string | null;
  status: string; category: string;
  invoiceDate: Date; issueDate: Date | null; signingDate: Date | null;
  taxAuthorityCode: string | null;
  taxAuthorityResponse: Record<string, unknown> | null;
  verifyCode: string | null;
  glBatchId: string | null; postedToGL: boolean;
  xmlData: string | null; pdfData: string | null;
  version: number; createdBy: string | null;
  createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class EinvInvoice extends AggregateRoot<EinvInvoiceId> {
  private _id: EinvInvoiceId;
  private _salesInvoiceId: string | null;
  private _invoiceNumber: string;
  private _invoiceCode: string | null;
  private _invoiceSymbol: string | null;
  private _invoiceName: string | null;
  private _invoiceTypeId: string;
  private _templateId: string;
  private _seriesId: string | null;
  private _providerId: string | null;
  private _sellerName: string;
  private _sellerTaxCode: string;
  private _sellerAddress: string | null;
  private _sellerPhone: string | null;
  private _sellerEmail: string | null;
  private _sellerBankName: string | null;
  private _sellerBankAccount: string | null;
  private _buyerName: string;
  private _buyerTaxCode: string | null;
  private _buyerAddress: string | null;
  private _buyerPhone: string | null;
  private _buyerEmail: string | null;
  private _buyerBankName: string | null;
  private _buyerBankAccount: string | null;
  private _currencyCode: string;
  private _exchangeRate: number;
  private _subtotal: bigint;
  private _discountAmount: bigint;
  private _taxAmount: bigint;
  private _grandTotal: bigint;
  private _amountInWords: string | null;
  private _status: EinvInvoiceStatus;
  private _category: EinvInvoiceCategory;
  private _invoiceDate: Date;
  private _issueDate: Date | null;
  private _signingDate: Date | null;
  private _taxAuthorityCode: string | null;
  private _taxAuthorityResponse: Record<string, unknown> | null;
  private _verifyCode: string | null;
  private _glBatchId: string | null;
  private _postedToGL: boolean;
  private _xmlData: string | null;
  private _pdfData: string | null;
  private _lines: EinvInvoiceLine[] = [];
  private _version: number;
  private _createdBy: string | null;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(
    id: EinvInvoiceId, invoiceNumber: string, invoiceTypeId: string, templateId: string,
    sellerName: string, sellerTaxCode: string, buyerName: string, invoiceDate: Date, category: EinvInvoiceCategory,
  ) {
    super();
    this._id = id; this._invoiceNumber = invoiceNumber;
    this._invoiceTypeId = invoiceTypeId; this._templateId = templateId;
    this._sellerName = sellerName; this._sellerTaxCode = sellerTaxCode;
    this._buyerName = buyerName; this._invoiceDate = invoiceDate;
    this._category = category;
    this._status = EinvInvoiceStatus.draft;
    this._currencyCode = "VND"; this._exchangeRate = 1;
    this._subtotal = 0n; this._discountAmount = 0n; this._taxAmount = 0n; this._grandTotal = 0n;
    this._salesInvoiceId = null; this._invoiceCode = null; this._invoiceSymbol = null;
    this._invoiceName = null; this._seriesId = null; this._providerId = null;
    this._sellerAddress = null; this._sellerPhone = null; this._sellerEmail = null;
    this._sellerBankName = null; this._sellerBankAccount = null;
    this._buyerTaxCode = null; this._buyerAddress = null; this._buyerPhone = null;
    this._buyerEmail = null; this._buyerBankName = null; this._buyerBankAccount = null;
    this._amountInWords = null;
    this._issueDate = null; this._signingDate = null;
    this._taxAuthorityCode = null; this._taxAuthorityResponse = null; this._verifyCode = null;
    this._glBatchId = null; this._postedToGL = false;
    this._xmlData = null; this._pdfData = null;
    this._version = 1; this._createdBy = null;
    this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    invoiceNumber: string; invoiceTypeId: string; templateId: string;
    sellerName: string; sellerTaxCode: string; buyerName: string;
    invoiceDate: Date; category?: EinvInvoiceCategory;
    salesInvoiceId?: string; invoiceCode?: string; invoiceSymbol?: string;
    seriesId?: string; providerId?: string;
    sellerAddress?: string; sellerPhone?: string; sellerEmail?: string;
    sellerBankName?: string; sellerBankAccount?: string;
    buyerTaxCode?: string; buyerAddress?: string; buyerPhone?: string; buyerEmail?: string;
    buyerBankName?: string; buyerBankAccount?: string;
    currencyCode?: string; exchangeRate?: number;
    createdBy?: string;
  }): EinvInvoice {
    const i = new EinvInvoice(
      EinvInvoiceId.new(), p.invoiceNumber, p.invoiceTypeId, p.templateId,
      p.sellerName, p.sellerTaxCode, p.buyerName, p.invoiceDate,
      p.category ?? EinvInvoiceCategory.sales,
    );
    i._salesInvoiceId = p.salesInvoiceId ?? null;
    i._invoiceCode = p.invoiceCode ?? null; i._invoiceSymbol = p.invoiceSymbol ?? null;
    i._seriesId = p.seriesId ?? null; i._providerId = p.providerId ?? null;
    i._sellerAddress = p.sellerAddress ?? null; i._sellerPhone = p.sellerPhone ?? null;
    i._sellerEmail = p.sellerEmail ?? null;
    i._sellerBankName = p.sellerBankName ?? null; i._sellerBankAccount = p.sellerBankAccount ?? null;
    i._buyerTaxCode = p.buyerTaxCode ?? null; i._buyerAddress = p.buyerAddress ?? null;
    i._buyerPhone = p.buyerPhone ?? null; i._buyerEmail = p.buyerEmail ?? null;
    i._buyerBankName = p.buyerBankName ?? null; i._buyerBankAccount = p.buyerBankAccount ?? null;
    if (p.currencyCode) i._currencyCode = p.currencyCode;
    if (p.exchangeRate) i._exchangeRate = p.exchangeRate;
    i._createdBy = p.createdBy ?? null;
    i.addEvent(new EinvInvoiceCreated(i._id.value, new Date(), {
      invoiceNumber: p.invoiceNumber, buyerName: p.buyerName,
    }));
    return i;
  }

  static load(s: EinvInvoiceState): EinvInvoice {
    const i = new EinvInvoice(
      new EinvInvoiceId(s.id), s.invoiceNumber, s.invoiceTypeId, s.templateId,
      s.sellerName, s.sellerTaxCode, s.buyerName, s.invoiceDate,
      s.category as EinvInvoiceCategory,
    );
    i._salesInvoiceId = s.salesInvoiceId; i._invoiceCode = s.invoiceCode;
    i._invoiceSymbol = s.invoiceSymbol; i._invoiceName = s.invoiceName;
    i._seriesId = s.seriesId; i._providerId = s.providerId;
    i._sellerAddress = s.sellerAddress; i._sellerPhone = s.sellerPhone;
    i._sellerEmail = s.sellerEmail; i._sellerBankName = s.sellerBankName;
    i._sellerBankAccount = s.sellerBankAccount;
    i._buyerTaxCode = s.buyerTaxCode; i._buyerAddress = s.buyerAddress;
    i._buyerPhone = s.buyerPhone; i._buyerEmail = s.buyerEmail;
    i._buyerBankName = s.buyerBankName; i._buyerBankAccount = s.buyerBankAccount;
    i._currencyCode = s.currencyCode; i._exchangeRate = s.exchangeRate;
    i._subtotal = s.subtotal; i._discountAmount = s.discountAmount;
    i._taxAmount = s.taxAmount; i._grandTotal = s.grandTotal;
    i._amountInWords = s.amountInWords;
    i._status = s.status as EinvInvoiceStatus;
    i._issueDate = s.issueDate; i._signingDate = s.signingDate;
    i._taxAuthorityCode = s.taxAuthorityCode;
    i._taxAuthorityResponse = s.taxAuthorityResponse; i._verifyCode = s.verifyCode;
    i._glBatchId = s.glBatchId; i._postedToGL = s.postedToGL;
    i._xmlData = s.xmlData; i._pdfData = s.pdfData;
    i._version = s.version; i._createdBy = s.createdBy;
    i._createdAt = s.createdAt; i._updatedAt = s.updatedAt; i._deletedAt = s.deletedAt;
    return i;
  }

  get id() { return this._id; }
  get invoiceNumber() { return this._invoiceNumber; }
  get invoiceCode() { return this._invoiceCode; }
  get invoiceSymbol() { return this._invoiceSymbol; }
  get status() { return this._status; }
  get category() { return this._category; }
  get sellerName() { return this._sellerName; }
  get sellerTaxCode() { return this._sellerTaxCode; }
  get buyerName() { return this._buyerName; }
  get buyerTaxCode() { return this._buyerTaxCode; }
  get subtotal() { return this._subtotal; }
  get taxAmount() { return this._taxAmount; }
  get grandTotal() { return this._grandTotal; }
  get amountInWords() { return this._amountInWords; }
  get lines() { return [...this._lines]; }
  get invoiceTypeId() { return this._invoiceTypeId; }
  get templateId() { return this._templateId; }
  get seriesId() { return this._seriesId; }
  get providerId() { return this._providerId; }
  get currencyCode() { return this._currencyCode; }
  get exchangeRate() { return this._exchangeRate; }
  get salesInvoiceId() { return this._salesInvoiceId; }
  get version() { return this._version; }
  get glBatchId() { return this._glBatchId; }
  get postedToGL() { return this._postedToGL; }
  get issueDate() { return this._issueDate; }
  get signingDate() { return this._signingDate; }
  get verifyCode() { return this._verifyCode; }
  get taxAuthorityCode() { return this._taxAuthorityCode; }
  get xmlData() { return this._xmlData; }
  get pdfData() { return this._pdfData; }
  get invoiceDate() { return this._invoiceDate; }

  // ─── Line Management ────────────────────────────────────────────────────────

  addLine(line: EinvInvoiceLine): void {
    if (this._status !== EinvInvoiceStatus.draft) {
      throw new DomainError("BusinessRule", "Cannot add lines to non-draft invoice");
    }
    this._lines.push(line);
    this._recalculate();
  }

  private _recalculate(): void {
    this._subtotal = this._lines.reduce((s, l) => s + l.totalPrice, 0n);
    this._discountAmount = this._lines.reduce((s, l) => s + l.discountAmount, 0n);
    this._taxAmount = this._lines.reduce((s, l) => s + l.taxAmount, 0n);
    this._grandTotal = this._subtotal - this._discountAmount + this._taxAmount;
  }

  setAmountInWords(words: string): void {
    this._amountInWords = words;
  }

  // ─── Lifecycle Transitions ──────────────────────────────────────────────────

  submit(): void {
    if (this._lines.length === 0) throw new DomainError("Validation", "Cannot submit invoice with no lines");
    if (this._status !== EinvInvoiceStatus.draft) throw new DomainError("BusinessRule", "Only draft invoice can be submitted");
    this._status = EinvInvoiceStatus.pendingApproval;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceSubmitted(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  approve(): void {
    if (this._status !== EinvInvoiceStatus.pendingApproval) throw new DomainError("BusinessRule", "Invoice not pending approval");
    this._status = EinvInvoiceStatus.approved;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceApproved(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  reject(reason: string): void {
    if (this._status !== EinvInvoiceStatus.pendingApproval) throw new DomainError("BusinessRule", "Invoice not pending approval");
    this._status = EinvInvoiceStatus.rejected;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceRejected(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber, reason }));
  }

  sign(): void {
    if (this._status !== EinvInvoiceStatus.approved) throw new DomainError("BusinessRule", "Only approved invoice can be signed");
    this._status = EinvInvoiceStatus.signed;
    this._signingDate = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceSigned(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  issue(): void {
    if (this._status !== EinvInvoiceStatus.signed && this._status !== EinvInvoiceStatus.approved) {
      throw new DomainError("BusinessRule", "Invoice must be signed or approved before issuance");
    }
    this._status = EinvInvoiceStatus.issued;
    this._issueDate = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceIssued(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  submitToTaxAuthority(providerId: string): void {
    if (this._status !== EinvInvoiceStatus.issued) throw new DomainError("BusinessRule", "Only issued invoice can be submitted");
    this._providerId = providerId;
    this._status = EinvInvoiceStatus.submitted;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceSubmittedToTaxAuthority(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber, providerId }));
  }

  markAccepted(taxAuthorityCode: string, verifyCode: string): void {
    if (this._status !== EinvInvoiceStatus.submitted) throw new DomainError("BusinessRule", "Invoice not in submitted status");
    this._status = EinvInvoiceStatus.accepted;
    this._taxAuthorityCode = taxAuthorityCode;
    this._verifyCode = verifyCode;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceAccepted(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber, taxAuthorityCode, verifyCode }));
  }

  markRejectedByTaxAuthority(reason: string): void {
    if (this._status !== EinvInvoiceStatus.submitted) throw new DomainError("BusinessRule", "Invoice not in submitted status");
    this._status = EinvInvoiceStatus.rejected;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceRejected(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber, reason }));
  }

  cancel(reason: string): void {
    if (this._status === EinvInvoiceStatus.cancelled) throw new DomainError("BusinessRule", "Invoice already cancelled");
    if (this._status === EinvInvoiceStatus.accepted || this._status === EinvInvoiceStatus.issued) {
      this._status = EinvInvoiceStatus.cancelled;
      this._updatedAt = new Date(); this._version++;
      this.addEvent(new EinvInvoiceCancelled(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber, reason }));
    } else {
      throw new DomainError("BusinessRule", "Invoice cannot be cancelled in current status");
    }
  }

  replace(): void {
    if (this._status !== EinvInvoiceStatus.accepted && this._status !== EinvInvoiceStatus.issued) {
      throw new DomainError("BusinessRule", "Only accepted/issued invoice can be replaced");
    }
    this._status = EinvInvoiceStatus.replaced;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceReplaced(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  adjust(): void {
    if (this._status !== EinvInvoiceStatus.accepted) throw new DomainError("BusinessRule", "Only accepted invoice can be adjusted");
    this._status = EinvInvoiceStatus.adjusted;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceAdjusted(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  archive(): void {
    if (this._status === EinvInvoiceStatus.archived) throw new DomainError("BusinessRule", "Invoice already archived");
    this._status = EinvInvoiceStatus.archived;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceArchived(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  restore(): void {
    if (this._status !== EinvInvoiceStatus.archived) throw new DomainError("BusinessRule", "Only archived invoice can be restored");
    this._status = EinvInvoiceStatus.restored;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceRestored(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  markExpired(): void {
    if (this._status !== EinvInvoiceStatus.accepted && this._status !== EinvInvoiceStatus.issued) {
      throw new DomainError("BusinessRule", "Only accepted/issued invoice can expire");
    }
    this._status = EinvInvoiceStatus.expired;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new EinvInvoiceExpired(this._id.value, new Date(), { invoiceNumber: this._invoiceNumber }));
  }

  // ─── GL Integration ─────────────────────────────────────────────────────────

  markPostedToGL(glBatchId: string): void {
    if (this._postedToGL) throw new DomainError("BusinessRule", "Invoice already posted to GL");
    if (this._status !== EinvInvoiceStatus.accepted) throw new DomainError("BusinessRule", "Only accepted invoice can be posted to GL");
    this._glBatchId = glBatchId;
    this._postedToGL = true;
    this._updatedAt = new Date(); this._version++;
  }

  // ─── XML/PDF Data ────────────────────────────────────────────────────────────

  setXmlData(xml: string): void {
    this._xmlData = xml;
    this._updatedAt = new Date(); this._version++;
  }

  setPdfData(pdf: string): void {
    this._pdfData = pdf;
    this._updatedAt = new Date(); this._version++;
  }

  // ─── State ──────────────────────────────────────────────────────────────────

  toState(): EinvInvoiceState {
    return {
      id: this._id.value, salesInvoiceId: this._salesInvoiceId,
      invoiceNumber: this._invoiceNumber, invoiceCode: this._invoiceCode,
      invoiceSymbol: this._invoiceSymbol, invoiceName: this._invoiceName,
      invoiceTypeId: this._invoiceTypeId, templateId: this._templateId,
      seriesId: this._seriesId, providerId: this._providerId,
      sellerName: this._sellerName, sellerTaxCode: this._sellerTaxCode,
      sellerAddress: this._sellerAddress, sellerPhone: this._sellerPhone,
      sellerEmail: this._sellerEmail, sellerBankName: this._sellerBankName,
      sellerBankAccount: this._sellerBankAccount,
      buyerName: this._buyerName, buyerTaxCode: this._buyerTaxCode,
      buyerAddress: this._buyerAddress, buyerPhone: this._buyerPhone,
      buyerEmail: this._buyerEmail, buyerBankName: this._buyerBankName,
      buyerBankAccount: this._buyerBankAccount,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      subtotal: this._subtotal, discountAmount: this._discountAmount,
      taxAmount: this._taxAmount, grandTotal: this._grandTotal,
      amountInWords: this._amountInWords,
      status: this._status, category: this._category,
      invoiceDate: this._invoiceDate, issueDate: this._issueDate,
      signingDate: this._signingDate,
      taxAuthorityCode: this._taxAuthorityCode,
      taxAuthorityResponse: this._taxAuthorityResponse, verifyCode: this._verifyCode,
      glBatchId: this._glBatchId, postedToGL: this._postedToGL,
      xmlData: this._xmlData, pdfData: this._pdfData,
      version: this._version, createdBy: this._createdBy,
      createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
