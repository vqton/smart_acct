export enum VendorStatus { active = "active", inactive = "inactive", blocked = "blocked", suspended = "suspended", pending = "pending" }
export enum VendorType { individual = "individual", company = "company", government = "government", nonProfit = "non_profit", foreign = "foreign" }
export enum VendorCategory { rawMaterial = "raw_material", packaging = "packaging", spareParts = "spare_parts", services = "services", equipment = "equipment", it = "it", logistics = "logistics", consulting = "consulting", utilities = "utilities", other = "other" }
export enum VendorClassification { local = "local", foreign = "foreign", preferred = "preferred", strategic = "strategic", critical = "critical", approved = "approved", certified = "certified" }
export enum VendorQualificationStatus { unqualified = "unqualified", qualified = "qualified", underReview = "under_review", certified = "certified", suspended = "suspended", revoked = "revoked" }
export enum EvaluationScore { a = "A", b = "B", c = "C", d = "D", f = "F" }
export enum RequisitionStatus { draft = "draft", submitted = "submitted", approved = "approved", rejected = "rejected", partiallyOrdered = "partially_ordered", fullyOrdered = "fully_ordered", cancelled = "cancelled" }
export enum RequisitionPriority { low = "low", medium = "medium", high = "high", urgent = "urgent" }
export enum RFQStatus { draft = "draft", sent = "sent", responsesReceived = "responses_received", evaluated = "evaluated", awarded = "awarded", cancelled = "cancelled" }
export enum QuotationStatus { draft = "draft", submitted = "submitted", withdrawn = "withdrawn", accepted = "accepted", rejected = "rejected" }
export enum POStatus { draft = "draft", pendingApproval = "pending_approval", approved = "approved", sent = "sent", confirmed = "confirmed", partlyReceived = "partly_received", fullyReceived = "fully_received", partlyInvoiced = "partly_invoiced", fullyInvoiced = "fully_invoiced", closed = "closed", cancelled = "cancelled", onHold = "on_hold" }
export enum POType { standard = "standard", blanket = "blanket", framework = "framework", contract = "contract", service = "service", consignment = "consignment", dropShipment = "drop_shipment", emergency = "emergency", recurring = "recurring" }
export enum PORevisionStatus { draft = "draft", approved = "approved", cancelled = "cancelled" }
export enum ContractStatus { draft = "draft", active = "active", expired = "expired", terminated = "terminated", amended = "amended" }
export enum ContractType { framework = "framework", blanket = "blanket", fixedPrice = "fixed_price", unitPrice = "unit_price", costPlus = "cost_plus", service = "service" }
export enum ReceiptStatus { expected = "expected", partlyReceived = "partly_received", fullyReceived = "fully_received", reversed = "reversed", cancelled = "cancelled" }
export enum InspectionStatus { pending = "pending", passed = "passed", failed = "failed", quarantined = "quarantined", partialPass = "partial_pass" }
export enum InvoiceStatus { draft = "draft", registered = "registered", verified = "verified", approved = "approved", paid = "paid", partiallyPaid = "partially_paid", cancelled = "cancelled", onHold = "on_hold" }
export enum InvoiceMatchStatus { unmatched = "unmatched", partiallyMatched = "partially_matched", fullyMatched = "fully_matched", exception = "exception" }
export enum PaymentStatus { pending = "pending", scheduled = "scheduled", paid = "paid", partial = "partial", overdue = "overdue", cancelled = "cancelled", onHold = "on_hold" }
export enum ImportStatus { declared = "declared", customsCleared = "customs_cleared", goodsReleased = "goods_released", dutyPaid = "duty_paid", completed = "completed" }
export enum Incoterm { exw = "EXW", fca = "FCA", fas = "FAS", fob = "FOB", cfr = "CFR", cif = "CIF", cpt = "CPT", cip = "CIP", dpu = "DPU", dap = "DAP", ddp = "DDP" }
export enum FreightTerm { prepaid = "prepaid", collect = "collect", prepaidAndCharge = "prepaid_and_charge" }
export enum ApprovalStatus { pending = "pending", approved = "approved", rejected = "rejected", returned = "returned", delegated = "delegated", escalated = "escalated" }
export enum ApprovalType { sequential = "sequential", parallel = "parallel", any = "any" }
export enum WorkflowEntityType { requisition = "requisition", rfq = "rfq", po = "po", contract = "contract", invoice = "invoice", payment = "payment" }
export enum DocumentType { requisition = "requisition", rfq = "rfq", quotation = "quotation", po = "po", contract = "contract", receipt = "receipt", invoice = "invoice", creditNote = "credit_note", debitNote = "debit_note" }
export enum ToleranceType { percentage = "percentage", amount = "amount", both = "both" }
export enum MatchingRule { twoWay = "two_way", threeWay = "three_way", fourWay = "four_way" }
export enum LandedCostType { freight = "freight", insurance = "insurance", duty = "duty", handling = "handling", inspection = "inspection", storage = "storage", brokerage = "brokerage", other = "other" }
export enum ShipmentStatus { booked = "booked", inTransit = "in_transit", arrived = "arrived", cleared = "cleared", delivered = "delivered" }
export enum PriceUnit { perUnit = "per_unit", perKg = "per_kg", perTon = "per_ton", perMeter = "per_meter", perSquareMeter = "per_sqm", perLiter = "per_liter", perHour = "per_hour", perDay = "per_day", perMonth = "per_month", lumpSum = "lump_sum" }
export enum BudgetCheckStatus { withinBudget = "within_budget", nearLimit = "near_limit", exceeded = "exceeded", notFound = "not_found" }
