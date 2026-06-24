import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { ProductionOrderId, ProductionOrderComponentId, ProductionOrderOperationId } from "./cst-ids.js";
import { CstProductionOrderStatus, CstCostElementType } from "./cst-enums.js";
import { CostingEvents } from "./cst-events.js";

export interface ProductionOrderComponentState {
  id: string;
  orderId: string;
  lineNumber: number;
  componentItemId: string;
  componentCode: string;
  componentName: string;
  requiredQty: number;
  issuedQty: number;
  scrappedQty: number;
  returnedQty: number;
  uom: string;
  unitCost: number;
  totalCost: number;
  standardCost: number;
  costVariance: number;
  costElement: string;
  bomLineId: string | null;
  warehouseId: string | null;
  inventoryTxId: string | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class ProductionOrderComponent {
  constructor(
    private _id: ProductionOrderComponentId,
    private _orderId: string,
    private _lineNumber: number,
    private _componentItemId: string,
    private _componentCode: string,
    private _componentName: string,
    private _requiredQty: number,
    private _issuedQty: number,
    private _scrappedQty: number,
    private _returnedQty: number,
    private _uom: string,
    private _unitCost: number,
    private _totalCost: number,
    private _standardCost: number,
    private _costVariance: number,
    private _costElement: CstCostElementType,
    private _bomLineId: string | null,
    private _warehouseId: string | null,
    private _inventoryTxId: string | null,
    private _notes: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
  ) {}

  static create(p: {
    orderId: string; lineNumber: number; componentItemId: string;
    componentCode: string; componentName: string; requiredQty: number;
    uom?: string; unitCost?: number; standardCost?: number;
    costElement?: CstCostElementType; bomLineId?: string | null;
    warehouseId?: string | null; notes?: string | null;
  }): ProductionOrderComponent {
    return new ProductionOrderComponent(
      ProductionOrderComponentId.new(), p.orderId, p.lineNumber,
      p.componentItemId, p.componentCode, p.componentName, p.requiredQty,
      0, 0, 0, p.uom ?? "pc", p.unitCost ?? 0,
      (p.unitCost ?? 0) * p.requiredQty,
      p.standardCost ?? 0, 0,
      p.costElement ?? CstCostElementType.Material,
      p.bomLineId ?? null, p.warehouseId ?? null, null,
      p.notes ?? null, 1, new Date(), new Date(),
    );
  }

  static load(s: ProductionOrderComponentState): ProductionOrderComponent {
    return new ProductionOrderComponent(
      new ProductionOrderComponentId(s.id), s.orderId, s.lineNumber,
      s.componentItemId, s.componentCode, s.componentName,
      s.requiredQty, s.issuedQty, s.scrappedQty, s.returnedQty,
      s.uom, s.unitCost, s.totalCost, s.standardCost, s.costVariance,
      s.costElement as CstCostElementType, s.bomLineId, s.warehouseId,
      s.inventoryTxId, s.notes, s.version, s.createdAt, s.updatedAt,
    );
  }

  get id() { return this._id; }
  get componentItemId() { return this._componentItemId; }
  get requiredQty() { return this._requiredQty; }
  get issuedQty() { return this._issuedQty; }
  get unitCost() { return this._unitCost; }
  get totalCost() { return this._totalCost; }
  get standardCost() { return this._standardCost; }
  get costVariance() { return this._costVariance; }

  issue(quantity: number, unitCost: number): void {
    if (quantity <= 0) throw new DomainError("BusinessRule", "Issue quantity must be positive");
    this._issuedQty += quantity;
    this._unitCost = unitCost;
    this._totalCost = this._issuedQty * unitCost;
    this._costVariance = this._totalCost - (this._issuedQty * this._standardCost);
    this._version++;
    this._updatedAt = new Date();
  }

  returnMaterial(quantity: number): void {
    if (quantity <= 0 || quantity > this._issuedQty - this._returnedQty) {
      throw new DomainError("BusinessRule", "Invalid return quantity");
    }
    this._returnedQty += quantity;
    this._totalCost = (this._issuedQty - this._returnedQty) * this._unitCost;
    this._costVariance = this._totalCost - ((this._issuedQty - this._returnedQty) * this._standardCost);
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): ProductionOrderComponentState {
    return {
      id: this._id.value, orderId: this._orderId, lineNumber: this._lineNumber,
      componentItemId: this._componentItemId, componentCode: this._componentCode,
      componentName: this._componentName, requiredQty: this._requiredQty,
      issuedQty: this._issuedQty, scrappedQty: this._scrappedQty,
      returnedQty: this._returnedQty, uom: this._uom, unitCost: this._unitCost,
      totalCost: this._totalCost, standardCost: this._standardCost,
      costVariance: this._costVariance, costElement: this._costElement,
      bomLineId: this._bomLineId, warehouseId: this._warehouseId,
      inventoryTxId: this._inventoryTxId, notes: this._notes,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}

export interface ProductionOrderOperationState {
  id: string;
  orderId: string;
  operationSeq: number;
  workCenterId: string | null;
  operationName: string;
  setupTime: number;
  runTime: number;
  actualSetupTime: number;
  actualRunTime: number;
  laborCount: number;
  machineCount: number;
  laborRate: number;
  machineRate: number;
  overheadRate: number;
  estimatedLaborCost: number;
  estimatedMachineCost: number;
  estimatedOverheadCost: number;
  estimatedTotalCost: number;
  actualLaborCost: number;
  actualMachineCost: number;
  actualOverheadCost: number;
  actualTotalCost: number;
  completedQty: number;
  isCompleted: boolean;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
}

export class ProductionOrderOperation {
  constructor(
    private _id: ProductionOrderOperationId,
    private _orderId: string,
    private _operationSeq: number,
    private _workCenterId: string | null,
    private _operationName: string,
    private _setupTime: number,
    private _runTime: number,
    private _actualSetupTime: number,
    private _actualRunTime: number,
    private _laborCount: number,
    private _machineCount: number,
    private _laborRate: number,
    private _machineRate: number,
    private _overheadRate: number,
    private _estimatedLaborCost: number,
    private _estimatedMachineCost: number,
    private _estimatedOverheadCost: number,
    private _estimatedTotalCost: number,
    private _actualLaborCost: number,
    private _actualMachineCost: number,
    private _actualOverheadCost: number,
    private _actualTotalCost: number,
    private _completedQty: number,
    private _isCompleted: boolean,
    private _notes: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
  ) {}

  static create(p: {
    orderId: string; operationSeq: number; operationName: string;
    workCenterId?: string | null; setupTime?: number; runTime?: number;
    laborCount?: number; machineCount?: number;
    laborRate?: number; machineRate?: number; overheadRate?: number;
    notes?: string | null;
  }): ProductionOrderOperation {
    const setup = p.setupTime ?? 0;
    const run = p.runTime ?? 0;
    const lr = p.laborRate ?? 0;
    const mr = p.machineRate ?? 0;
    const or = p.overheadRate ?? 0;
    const lc = p.laborCount ?? 1;
    const mc = p.machineCount ?? 1;
    const eLabor = run * lr * lc;
    const eMachine = run * mr * mc;
    const eOverhead = run * or;
    return new ProductionOrderOperation(
      ProductionOrderOperationId.new(), p.orderId, p.operationSeq,
      p.workCenterId ?? null, p.operationName, setup, run,
      0, 0, lc, mc, lr, mr, or,
      eLabor, eMachine, eOverhead, eLabor + eMachine + eOverhead,
      0, 0, 0, 0, 0, false,
      p.notes ?? null, 1, new Date(), new Date(),
    );
  }

  static load(s: ProductionOrderOperationState): ProductionOrderOperation {
    return new ProductionOrderOperation(
      new ProductionOrderOperationId(s.id), s.orderId, s.operationSeq,
      s.workCenterId, s.operationName, s.setupTime, s.runTime,
      s.actualSetupTime, s.actualRunTime, s.laborCount, s.machineCount,
      s.laborRate, s.machineRate, s.overheadRate,
      s.estimatedLaborCost, s.estimatedMachineCost, s.estimatedOverheadCost,
      s.estimatedTotalCost, s.actualLaborCost, s.actualMachineCost,
      s.actualOverheadCost, s.actualTotalCost, s.completedQty,
      s.isCompleted, s.notes, s.version, s.createdAt, s.updatedAt,
    );
  }

  get id() { return this._id; }
  get operationSeq() { return this._operationSeq; }
  get isCompleted() { return this._isCompleted; }
  get estimatedTotalCost() { return this._estimatedTotalCost; }
  get estimatedLaborCost() { return this._estimatedLaborCost; }
  get estimatedMachineCost() { return this._estimatedMachineCost; }
  get estimatedOverheadCost() { return this._estimatedOverheadCost; }
  get actualLaborCost() { return this._actualLaborCost; }
  get actualMachineCost() { return this._actualMachineCost; }
  get actualOverheadCost() { return this._actualOverheadCost; }
  get actualTotalCost() { return this._actualTotalCost; }

  complete(actualSetupTime: number, actualRunTime: number): void {
    this._actualSetupTime = actualSetupTime;
    this._actualRunTime = actualRunTime;
    this._actualLaborCost = actualRunTime * this._laborRate * this._laborCount;
    this._actualMachineCost = actualRunTime * this._machineRate * this._machineCount;
    this._actualOverheadCost = actualRunTime * this._overheadRate;
    this._actualTotalCost = this._actualLaborCost + this._actualMachineCost + this._actualOverheadCost;
    this._isCompleted = true;
    this._version++;
    this._updatedAt = new Date();
  }

  toState(): ProductionOrderOperationState {
    return {
      id: this._id.value, orderId: this._orderId, operationSeq: this._operationSeq,
      workCenterId: this._workCenterId, operationName: this._operationName,
      setupTime: this._setupTime, runTime: this._runTime,
      actualSetupTime: this._actualSetupTime, actualRunTime: this._actualRunTime,
      laborCount: this._laborCount, machineCount: this._machineCount,
      laborRate: this._laborRate, machineRate: this._machineRate,
      overheadRate: this._overheadRate,
      estimatedLaborCost: this._estimatedLaborCost,
      estimatedMachineCost: this._estimatedMachineCost,
      estimatedOverheadCost: this._estimatedOverheadCost,
      estimatedTotalCost: this._estimatedTotalCost,
      actualLaborCost: this._actualLaborCost,
      actualMachineCost: this._actualMachineCost,
      actualOverheadCost: this._actualOverheadCost,
      actualTotalCost: this._actualTotalCost,
      completedQty: this._completedQty, isCompleted: this._isCompleted,
      notes: this._notes, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}

export interface ProductionOrderState {
  id: string;
  orderNumber: string;
  itemId: string;
  itemCode: string;
  itemName: string;
  bomId: string | null;
  routingId: string | null;
  workCenterId: string | null;
  status: string;
  quantity: number;
  completedQty: number;
  scrappedQty: number;
  uom: string;
  plannedStartDate: Date;
  plannedEndDate: Date | null;
  actualStartDate: Date | null;
  actualEndDate: Date | null;
  companyId: string;
  branchId: string | null;
  warehouseId: string | null;
  currencyCode: string;
  exchangeRate: number;
  estimatedMaterialCost: number;
  estimatedLaborCost: number;
  estimatedMachineCost: number;
  estimatedOverheadCost: number;
  estimatedTotalCost: number;
  actualMaterialCost: number;
  actualLaborCost: number;
  actualMachineCost: number;
  actualOverheadCost: number;
  actualTotalCost: number;
  materialVariance: number;
  laborVariance: number;
  machineVariance: number;
  overheadVariance: number;
  totalVariance: number;
  glBatchId: string | null;
  postedToGL: boolean;
  createdById: string | null;
  approvedById: string | null;
  approvedAt: Date | null;
  closedById: string | null;
  closedAt: Date | null;
  notes: string | null;
  components: ProductionOrderComponentState[];
  operations: ProductionOrderOperationState[];
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class ProductionOrder extends AggregateRoot<ProductionOrderId> {
  private _components: ProductionOrderComponent[] = [];
  private _operations: ProductionOrderOperation[] = [];

  private constructor(
    private _id: ProductionOrderId,
    private _orderNumber: string,
    private _itemId: string,
    private _itemCode: string,
    private _itemName: string,
    private _bomId: string | null,
    private _routingId: string | null,
    private _workCenterId: string | null,
    private _status: CstProductionOrderStatus,
    private _quantity: number,
    private _completedQty: number,
    private _scrappedQty: number,
    private _uom: string,
    private _plannedStartDate: Date,
    private _plannedEndDate: Date | null,
    private _actualStartDate: Date | null,
    private _actualEndDate: Date | null,
    private _companyId: string,
    private _branchId: string | null,
    private _warehouseId: string | null,
    private _currencyCode: string,
    private _exchangeRate: number,
    private _estimatedMaterialCost: number,
    private _estimatedLaborCost: number,
    private _estimatedMachineCost: number,
    private _estimatedOverheadCost: number,
    private _estimatedTotalCost: number,
    private _actualMaterialCost: number,
    private _actualLaborCost: number,
    private _actualMachineCost: number,
    private _actualOverheadCost: number,
    private _actualTotalCost: number,
    private _materialVariance: number,
    private _laborVariance: number,
    private _machineVariance: number,
    private _overheadVariance: number,
    private _totalVariance: number,
    private _glBatchId: string | null,
    private _postedToGL: boolean,
    private _createdById: string | null,
    private _approvedById: string | null,
    private _approvedAt: Date | null,
    private _closedById: string | null,
    private _closedAt: Date | null,
    private _notes: string | null,
    private _version: number,
    private _createdAt: Date,
    private _updatedAt: Date,
    private _deletedAt: Date | null,
  ) { super(); }

  static create(p: {
    orderNumber: string; itemId: string; itemCode: string; itemName: string;
    bomId?: string | null; workCenterId?: string | null;
    quantity: number; uom?: string;
    plannedStartDate: Date; plannedEndDate?: Date | null;
    companyId: string; branchId?: string | null; warehouseId?: string | null;
    currencyCode?: string; exchangeRate?: number;
    estimatedMaterialCost?: number; estimatedLaborCost?: number;
    estimatedMachineCost?: number; estimatedOverheadCost?: number;
    createdById?: string | null; notes?: string | null;
  }): ProductionOrder {
    const eMat = p.estimatedMaterialCost ?? 0;
    const eLab = p.estimatedLaborCost ?? 0;
    const eMac = p.estimatedMachineCost ?? 0;
    const eOh = p.estimatedOverheadCost ?? 0;
    const po = new ProductionOrder(
      ProductionOrderId.new(), p.orderNumber, p.itemId, p.itemCode, p.itemName,
      p.bomId ?? null, null, p.workCenterId ?? null,
      CstProductionOrderStatus.Planned, p.quantity, 0, 0,
      p.uom ?? "pc", p.plannedStartDate, p.plannedEndDate ?? null,
      null, null, p.companyId, p.branchId ?? null, p.warehouseId ?? null,
      p.currencyCode ?? "VND", p.exchangeRate ?? 1,
      eMat, eLab, eMac, eOh, eMat + eLab + eMac + eOh,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, null, false,
      p.createdById ?? null, null, null, null, null,
      p.notes ?? null, 1, new Date(), new Date(), null,
    );
    po.addEvent(CostingEvents.ProductionOrderCreated(po._id.value, { orderNumber: p.orderNumber, itemId: p.itemId }));
    return po;
  }

  static load(s: ProductionOrderState): ProductionOrder {
    const po = new ProductionOrder(
      new ProductionOrderId(s.id), s.orderNumber, s.itemId, s.itemCode, s.itemName,
      s.bomId, s.routingId, s.workCenterId, s.status as CstProductionOrderStatus,
      s.quantity, s.completedQty, s.scrappedQty, s.uom,
      s.plannedStartDate, s.plannedEndDate, s.actualStartDate, s.actualEndDate,
      s.companyId, s.branchId, s.warehouseId, s.currencyCode, s.exchangeRate,
      s.estimatedMaterialCost, s.estimatedLaborCost, s.estimatedMachineCost,
      s.estimatedOverheadCost, s.estimatedTotalCost,
      s.actualMaterialCost, s.actualLaborCost, s.actualMachineCost,
      s.actualOverheadCost, s.actualTotalCost,
      s.materialVariance, s.laborVariance, s.machineVariance,
      s.overheadVariance, s.totalVariance,
      s.glBatchId, s.postedToGL, s.createdById, s.approvedById,
      s.approvedAt, s.closedById, s.closedAt, s.notes,
      s.version, s.createdAt, s.updatedAt, s.deletedAt,
    );
    po._components = s.components.map(c => ProductionOrderComponent.load(c));
    po._operations = s.operations.map(o => ProductionOrderOperation.load(o));
    return po;
  }

  get id() { return this._id; }
  get orderNumber() { return this._orderNumber; }
  get status() { return this._status; }
  get itemId() { return this._itemId; }
  get quantity() { return this._quantity; }
  get completedQty() { return this._completedQty; }
  get components() { return [...this._components]; }
  get operations() { return [...this._operations]; }
  get version() { return this._version; }

  // Computed
  get actualMaterialCost() { return this._actualMaterialCost; }
  get actualLaborCost() { return this._actualLaborCost; }
  get actualTotalCost() { return this._actualTotalCost; }
  get totalVariance() { return this._totalVariance; }
  get estimatedTotalCost() { return this._estimatedTotalCost; }

  addComponent(component: ProductionOrderComponent): void {
    if (this._status !== CstProductionOrderStatus.Planned) {
      throw new DomainError("BusinessRule", "Can only add components to planned orders");
    }
    this._components.push(component);
    this._version++;
    this._updatedAt = new Date();
  }

  addOperation(operation: ProductionOrderOperation): void {
    if (this._status !== CstProductionOrderStatus.Planned) {
      throw new DomainError("BusinessRule", "Can only add operations to planned orders");
    }
    this._operations.push(operation);
    this._version++;
    this._updatedAt = new Date();
  }

  release(userId: string): void {
    if (this._status !== CstProductionOrderStatus.Planned) {
      throw new DomainError("BusinessRule", "Only planned orders can be released");
    }
    this._status = CstProductionOrderStatus.Released;
    this._actualStartDate = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.ProductionOrderReleased(this._id.value, { orderNumber: this._orderNumber }));
  }

  complete(userId: string): void {
    if (this._status !== CstProductionOrderStatus.InProgress) {
      throw new DomainError("BusinessRule", "Only in-progress orders can be completed");
    }
    if (this._components.some(c => c.issuedQty < c.requiredQty)) {
      throw new DomainError("BusinessRule", "All components must be issued before completion");
    }
    this._status = CstProductionOrderStatus.Completed;
    this._completedQty = this._quantity;
    this._actualEndDate = new Date();
    this.recalculateCosts();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.ProductionOrderCompleted(this._id.value, {
      orderNumber: this._orderNumber,
      actualTotalCost: this._actualTotalCost,
      totalVariance: this._totalVariance,
    }));
  }

  close(userId: string): void {
    if (this._status !== CstProductionOrderStatus.Completed) {
      throw new DomainError("BusinessRule", "Only completed orders can be closed");
    }
    this._status = CstProductionOrderStatus.Closed;
    this._closedById = userId;
    this._closedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.ProductionOrderClosed(this._id.value, { orderNumber: this._orderNumber }));
  }

  cancel(reason: string): void {
    if (this._status === CstProductionOrderStatus.Completed || this._status === CstProductionOrderStatus.Closed) {
      throw new DomainError("BusinessRule", "Cannot cancel completed or closed orders");
    }
    this._status = CstProductionOrderStatus.Cancelled;
    this._notes = reason;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.ProductionOrderCancelled(this._id.value, { orderNumber: this._orderNumber, reason }));
  }

  issueComponent(componentId: string, quantity: number, unitCost: number): void {
    const comp = this._components.find(c => c.id.value === componentId);
    if (!comp) throw new DomainError("NotFound", "Component not found");
    comp.issue(quantity, unitCost);
    this.recalculateCosts();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.ComponentIssued(componentId, {
      orderNumber: this._orderNumber, componentItemId: comp.componentItemId, quantity, unitCost,
    }));
  }

  returnComponent(componentId: string, quantity: number): void {
    const comp = this._components.find(c => c.id.value === componentId);
    if (!comp) throw new DomainError("NotFound", "Component not found");
    comp.returnMaterial(quantity);
    this.recalculateCosts();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.ComponentReturned(componentId, {
      orderNumber: this._orderNumber, componentItemId: comp.componentItemId, quantity,
    }));
  }

  completeOperation(operationId: string, actualSetupTime: number, actualRunTime: number): void {
    const op = this._operations.find(o => o.id.value === operationId);
    if (!op) throw new DomainError("NotFound", "Operation not found");
    op.complete(actualSetupTime, actualRunTime);
    this.recalculateCosts();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(CostingEvents.OperationCompleted(operationId, {
      orderNumber: this._orderNumber, operationSeq: op.operationSeq,
    }));
    if (this._operations.every(o => o.isCompleted)) {
      this._status = CstProductionOrderStatus.InProgress;
    }
  }

  private recalculateCosts(): void {
    this._actualMaterialCost = this._components.reduce((s, c) => s + c.totalCost, 0);
    this._actualLaborCost = this._operations.reduce((s, o) => s + o.estimatedLaborCost, 0);
    this._actualMachineCost = this._operations.reduce((s, o) => s + o.estimatedMachineCost, 0);
    this._actualOverheadCost = this._operations.reduce((s, o) => s + o.estimatedOverheadCost, 0);
    this._actualTotalCost = this._actualMaterialCost + this._actualLaborCost + this._actualMachineCost + this._actualOverheadCost;
    this._materialVariance = this._actualMaterialCost - this._estimatedMaterialCost;
    this._laborVariance = this._actualLaborCost - this._estimatedLaborCost;
    this._machineVariance = this._actualMachineCost - this._estimatedMachineCost;
    this._overheadVariance = this._actualOverheadCost - this._estimatedOverheadCost;
    this._totalVariance = this._actualTotalCost - this._estimatedTotalCost;
  }

  toState(): ProductionOrderState {
    return {
      id: this._id.value, orderNumber: this._orderNumber,
      itemId: this._itemId, itemCode: this._itemCode, itemName: this._itemName,
      bomId: this._bomId, routingId: this._routingId,
      workCenterId: this._workCenterId, status: this._status,
      quantity: this._quantity, completedQty: this._completedQty,
      scrappedQty: this._scrappedQty, uom: this._uom,
      plannedStartDate: this._plannedStartDate,
      plannedEndDate: this._plannedEndDate,
      actualStartDate: this._actualStartDate, actualEndDate: this._actualEndDate,
      companyId: this._companyId, branchId: this._branchId,
      warehouseId: this._warehouseId, currencyCode: this._currencyCode,
      exchangeRate: this._exchangeRate,
      estimatedMaterialCost: this._estimatedMaterialCost,
      estimatedLaborCost: this._estimatedLaborCost,
      estimatedMachineCost: this._estimatedMachineCost,
      estimatedOverheadCost: this._estimatedOverheadCost,
      estimatedTotalCost: this._estimatedTotalCost,
      actualMaterialCost: this._actualMaterialCost,
      actualLaborCost: this._actualLaborCost,
      actualMachineCost: this._actualMachineCost,
      actualOverheadCost: this._actualOverheadCost,
      actualTotalCost: this._actualTotalCost,
      materialVariance: this._materialVariance,
      laborVariance: this._laborVariance,
      machineVariance: this._machineVariance,
      overheadVariance: this._overheadVariance,
      totalVariance: this._totalVariance,
      glBatchId: this._glBatchId, postedToGL: this._postedToGL,
      createdById: this._createdById, approvedById: this._approvedById,
      approvedAt: this._approvedAt, closedById: this._closedById,
      closedAt: this._closedAt, notes: this._notes,
      components: this._components.map(c => c.toState()),
      operations: this._operations.map(o => o.toState()),
      version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }
}
