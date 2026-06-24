import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PurchaseRequisitionId, RequisitionItemId } from "./purchasing-ids.js";
import { RequisitionStatus, RequisitionPriority, BudgetCheckStatus } from "./purchasing-enums.js";
import {
  RequisitionCreated, RequisitionSubmitted, RequisitionApproved,
  RequisitionRejected, RequisitionCancelled,
} from "./purchasing-events.js";

// ─── Requisition Item ────────────────────────────────────────────────────────────

export interface RequisitionItemState {
  id: string; requisitionId: string; lineNumber: number;
  itemId: string | null; itemCode: string; itemName: string;
  description: string | null; quantity: number; uom: string;
  estimatedUnitPrice: number; estimatedTotal: number;
  currencyCode: string; requestedDate: Date | null;
  projectId: string | null; costCenterId: string | null; departmentId: string | null;
  branchId: string | null; warehouseId: string | null;
  budgetCheckStatus: string | null; notes: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class RequisitionItem extends AggregateRoot<RequisitionItemId> {
  private _id: RequisitionItemId; private _requisitionId: string; private _lineNumber: number;
  private _itemId: string | null; private _itemCode: string; private _itemName: string;
  private _description: string | null; private _quantity: number; private _uom: string;
  private _estimatedUnitPrice: number; private _estimatedTotal: number;
  private _currencyCode: string; private _requestedDate: Date | null;
  private _projectId: string | null; private _costCenterId: string | null;
  private _departmentId: string | null; private _branchId: string | null;
  private _warehouseId: string | null; private _budgetCheckStatus: string | null;
  private _notes: string | null; private _version: number; private _createdAt: Date;
  private _updatedAt: Date; private _deletedAt: Date | null;

  private constructor(id: RequisitionItemId, requisitionId: string, lineNumber: number, itemCode: string, itemName: string, quantity: number, uom: string, estimatedUnitPrice: number) {
    super(); this._id = id; this._requisitionId = requisitionId; this._lineNumber = lineNumber;
    this._itemCode = itemCode; this._itemName = itemName; this._quantity = quantity;
    this._uom = uom; this._estimatedUnitPrice = estimatedUnitPrice;
    this._estimatedTotal = quantity * estimatedUnitPrice;
    this._currencyCode = "VND"; this._itemId = null; this._description = null;
    this._requestedDate = null; this._projectId = null; this._costCenterId = null;
    this._departmentId = null; this._branchId = null; this._warehouseId = null;
    this._budgetCheckStatus = null; this._notes = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    requisitionId: string; lineNumber: number; itemCode: string; itemName: string;
    quantity: number; uom: string; estimatedUnitPrice: number; itemId?: string;
    description?: string; requestedDate?: Date; projectId?: string;
    costCenterId?: string; departmentId?: string; branchId?: string;
    warehouseId?: string; notes?: string;
  }): RequisitionItem {
    const ri = new RequisitionItem(RequisitionItemId.new(), p.requisitionId, p.lineNumber, p.itemCode, p.itemName, p.quantity, p.uom, p.estimatedUnitPrice);
    ri._itemId = p.itemId ?? null; ri._description = p.description ?? null;
    ri._requestedDate = p.requestedDate ?? null; ri._projectId = p.projectId ?? null;
    ri._costCenterId = p.costCenterId ?? null; ri._departmentId = p.departmentId ?? null;
    ri._branchId = p.branchId ?? null; ri._warehouseId = p.warehouseId ?? null;
    ri._notes = p.notes ?? null;
    return ri;
  }

  static load(s: RequisitionItemState): RequisitionItem {
    const ri = new RequisitionItem(new RequisitionItemId(s.id), s.requisitionId, s.lineNumber, s.itemCode, s.itemName, s.quantity, s.uom, s.estimatedUnitPrice);
    ri._itemId = s.itemId; ri._description = s.description; ri._requestedDate = s.requestedDate;
    ri._projectId = s.projectId; ri._costCenterId = s.costCenterId; ri._departmentId = s.departmentId;
    ri._branchId = s.branchId; ri._warehouseId = s.warehouseId; ri._budgetCheckStatus = s.budgetCheckStatus;
    ri._currencyCode = s.currencyCode; ri._estimatedTotal = s.estimatedTotal; ri._notes = s.notes;
    ri._version = s.version; ri._createdAt = s.createdAt; ri._updatedAt = s.updatedAt; ri._deletedAt = s.deletedAt;
    return ri;
  }

  get id(): RequisitionItemId { return this._id; }
  get quantity(): number { return this._quantity; }
  get estimatedTotal(): number { return this._estimatedTotal; }
  get version(): number { return this._version; }

  toState(): RequisitionItemState {
    return { id: this._id.value, requisitionId: this._requisitionId, lineNumber: this._lineNumber,
      itemId: this._itemId, itemCode: this._itemCode, itemName: this._itemName,
      description: this._description, quantity: this._quantity, uom: this._uom,
      estimatedUnitPrice: this._estimatedUnitPrice, estimatedTotal: this._estimatedTotal,
      currencyCode: this._currencyCode, requestedDate: this._requestedDate,
      projectId: this._projectId, costCenterId: this._costCenterId, departmentId: this._departmentId,
      branchId: this._branchId, warehouseId: this._warehouseId, budgetCheckStatus: this._budgetCheckStatus,
      notes: this._notes, version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}

// ─── Purchase Requisition ────────────────────────────────────────────────────────

export interface PurchaseRequisitionState {
  id: string; prNumber: string; companyId: string; branchId: string | null;
  departmentId: string | null; requesterId: string; description: string | null;
  status: string; priority: string; currencyCode: string;
  totalEstimated: number; notes: string | null;
  submittedAt: Date | null; approvedAt: Date | null; approvedBy: string | null;
  cancelledAt: Date | null; cancelReason: string | null;
  version: number; createdAt: Date; updatedAt: Date; deletedAt: Date | null;
}

export class PurchaseRequisition extends AggregateRoot<PurchaseRequisitionId> {
  private _id: PurchaseRequisitionId; private _prNumber: string; private _companyId: string;
  private _branchId: string | null; private _departmentId: string | null;
  private _requesterId: string; private _description: string | null;
  private _status: RequisitionStatus; private _priority: RequisitionPriority;
  private _currencyCode: string; private _totalEstimated: number;
  private _notes: string | null; private _items: RequisitionItem[] = [];
  private _submittedAt: Date | null; private _approvedAt: Date | null;
  private _approvedBy: string | null; private _cancelledAt: Date | null;
  private _cancelReason: string | null;
  private _version: number; private _createdAt: Date; private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: PurchaseRequisitionId, prNumber: string, companyId: string, requesterId: string) {
    super(); this._id = id; this._prNumber = prNumber; this._companyId = companyId;
    this._requesterId = requesterId; this._status = RequisitionStatus.draft;
    this._priority = RequisitionPriority.medium; this._currencyCode = "VND";
    this._totalEstimated = 0; this._branchId = null; this._departmentId = null;
    this._description = null; this._notes = null; this._submittedAt = null;
    this._approvedAt = null; this._approvedBy = null; this._cancelledAt = null;
    this._cancelReason = null;
    this._version = 1; this._createdAt = new Date(); this._updatedAt = new Date(); this._deletedAt = null;
  }

  static create(p: {
    prNumber: string; companyId: string; requesterId: string; branchId?: string;
    departmentId?: string; description?: string; priority?: RequisitionPriority;
    currencyCode?: string; notes?: string;
  }): PurchaseRequisition {
    const pr = new PurchaseRequisition(PurchaseRequisitionId.new(), p.prNumber, p.companyId, p.requesterId);
    pr._branchId = p.branchId ?? null; pr._departmentId = p.departmentId ?? null;
    pr._description = p.description ?? null; pr._priority = p.priority ?? RequisitionPriority.medium;
    pr._currencyCode = p.currencyCode ?? "VND"; pr._notes = p.notes ?? null;
    pr.addEvent(new RequisitionCreated(pr._id.value, new Date(), { prNumber: pr._prNumber }));
    return pr;
  }

  static load(s: PurchaseRequisitionState): PurchaseRequisition {
    const pr = new PurchaseRequisition(new PurchaseRequisitionId(s.id), s.prNumber, s.companyId, s.requesterId);
    pr._branchId = s.branchId; pr._departmentId = s.departmentId; pr._description = s.description;
    pr._status = s.status as RequisitionStatus; pr._priority = s.priority as RequisitionPriority;
    pr._currencyCode = s.currencyCode; pr._totalEstimated = s.totalEstimated; pr._notes = s.notes;
    pr._submittedAt = s.submittedAt; pr._approvedAt = s.approvedAt; pr._approvedBy = s.approvedBy;
    pr._cancelledAt = s.cancelledAt; pr._cancelReason = s.cancelReason;
    pr._version = s.version; pr._createdAt = s.createdAt; pr._updatedAt = s.updatedAt; pr._deletedAt = s.deletedAt;
    return pr;
  }

  get id(): PurchaseRequisitionId { return this._id; }
  get prNumber(): string { return this._prNumber; }
  get status(): RequisitionStatus { return this._status; }
  get items(): RequisitionItem[] { return this._items; }
  get totalEstimated(): number { return this._totalEstimated; }
  get version(): number { return this._version; }

  addItem(item: RequisitionItem): void {
    if (this._status !== RequisitionStatus.draft) throw new DomainError("BusinessRule", "Cannot add items to non-draft requisition");
    this._items.push(item);
    this._totalEstimated = this._items.reduce((sum, i) => sum + i.estimatedTotal, 0);
    this._updatedAt = new Date(); this._version++;
  }

  submit(): void {
    if (this._items.length === 0) throw new DomainError("Validation", "Cannot submit empty requisition");
    if (this._status !== RequisitionStatus.draft) throw new DomainError("BusinessRule", "Only draft requisitions can be submitted");
    this._status = RequisitionStatus.submitted;
    this._submittedAt = new Date(); this._updatedAt = new Date(); this._version++;
    this.addEvent(new RequisitionSubmitted(this._id.value, new Date(), { prNumber: this._prNumber }));
  }

  approve(approvedBy: string): void {
    if (this._status !== RequisitionStatus.submitted) throw new DomainError("BusinessRule", "Only submitted requisitions can be approved");
    this._status = RequisitionStatus.approved;
    this._approvedBy = approvedBy; this._approvedAt = new Date();
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new RequisitionApproved(this._id.value, new Date(), { prNumber: this._prNumber, approvedBy }));
  }

  reject(reason: string): void {
    if (this._status !== RequisitionStatus.submitted) throw new DomainError("BusinessRule", "Only submitted requisitions can be rejected");
    this._status = RequisitionStatus.rejected;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new RequisitionRejected(this._id.value, new Date(), { prNumber: this._prNumber, reason }));
  }

  cancel(reason: string): void {
    if (this._status === RequisitionStatus.cancelled) throw new DomainError("BusinessRule", "Requisition already cancelled");
    if (this._status === RequisitionStatus.approved || this._status === RequisitionStatus.fullyOrdered) {
      // Allow cancellation but track reason
    }
    this._status = RequisitionStatus.cancelled;
    this._cancelledAt = new Date(); this._cancelReason = reason;
    this._updatedAt = new Date(); this._version++;
    this.addEvent(new RequisitionCancelled(this._id.value, new Date(), { prNumber: this._prNumber, reason }));
  }

  markOrdered(): void {
    if (this._status === RequisitionStatus.approved) {
      this._status = RequisitionStatus.partiallyOrdered;
    } else if (this._status === RequisitionStatus.partiallyOrdered) {
      // keep as partial
    }
    this._updatedAt = new Date(); this._version++;
  }

  toState(): PurchaseRequisitionState {
    return { id: this._id.value, prNumber: this._prNumber, companyId: this._companyId,
      branchId: this._branchId, departmentId: this._departmentId, requesterId: this._requesterId,
      description: this._description, status: this._status, priority: this._priority,
      currencyCode: this._currencyCode, totalEstimated: this._totalEstimated, notes: this._notes,
      submittedAt: this._submittedAt, approvedAt: this._approvedAt, approvedBy: this._approvedBy,
      cancelledAt: this._cancelledAt, cancelReason: this._cancelReason,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt };
  }
}
