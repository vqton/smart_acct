import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { FaCipProjectId, FaCipCostId, FaCipMilestoneId, FaCipSettlementId } from "./fa-ids.js";
import { FaCipProjectCreated, FaCipCapitalized } from "./fa-events.js";

export interface FaCipProjectState {
  id: string; projectCode: string; projectName: string; companyId: string;
  startDate: Date; totalBudget: number; totalCost: number;
  capitalizedAmount: number; remainingBudget: number;
  projectType: string | null; status: string | null;
  branchId: string | null; departmentId: string | null;
  projectManagerId: string | null; expectedEndDate: Date | null;
  actualEndDate: Date | null; currencyCode: string;
  description: string | null; contractNumber: string | null;
  contractorId: string | null; contractorName: string | null;
  isExternal: boolean; approvalStatus: string | null;
  approvedById: string | null; approvedAt: Date | null;
  version: number; createdAt: Date; updatedAt: Date;
}

export class FaCipProject extends AggregateRoot<FaCipProjectId> {
  private _id: FaCipProjectId;
  private _projectCode: string;
  private _projectName: string;
  private _companyId: string;
  private _startDate: Date;
  private _totalBudget: number;
  private _totalCost: number;
  private _capitalizedAmount: number;
  private _remainingBudget: number;
  private _projectType: string | null;
  private _status: string | null;
  private _branchId: string | null;
  private _departmentId: string | null;
  private _projectManagerId: string | null;
  private _expectedEndDate: Date | null;
  private _actualEndDate: Date | null;
  private _currencyCode: string;
  private _description: string | null;
  private _contractNumber: string | null;
  private _contractorId: string | null;
  private _contractorName: string | null;
  private _isExternal: boolean;
  private _approvalStatus: string | null;
  private _approvedById: string | null;
  private _approvedAt: Date | null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(projectCode: string, projectName: string, companyId: string, startDate: Date) {
    super();
    this._id = FaCipProjectId.new();
    this._projectCode = projectCode;
    this._projectName = projectName;
    this._companyId = companyId;
    this._startDate = startDate;
    this._totalBudget = 0;
    this._totalCost = 0;
    this._capitalizedAmount = 0;
    this._remainingBudget = 0;
    this._currencyCode = "VND";
    this._isExternal = true;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._projectType = null;
    this._status = "active";
    this._branchId = null;
    this._departmentId = null;
    this._projectManagerId = null;
    this._expectedEndDate = null;
    this._actualEndDate = null;
    this._description = null;
    this._contractNumber = null;
    this._contractorId = null;
    this._contractorName = null;
    this._approvalStatus = null;
    this._approvedById = null;
    this._approvedAt = null;
  }

  static create(p: {
    projectCode: string; projectName: string; companyId: string; startDate: Date;
    totalBudget?: number; description?: string; projectType?: string;
    branchId?: string; departmentId?: string; projectManagerId?: string;
    expectedEndDate?: Date; contractNumber?: string; contractorId?: string;
    contractorName?: string; isExternal?: boolean;
  }): FaCipProject {
    const proj = new FaCipProject(p.projectCode, p.projectName, p.companyId, p.startDate);
    proj._totalBudget = p.totalBudget ?? 0;
    proj._remainingBudget = p.totalBudget ?? 0;
    if (p.description) proj._description = p.description;
    if (p.projectType) proj._projectType = p.projectType;
    if (p.branchId) proj._branchId = p.branchId;
    if (p.departmentId) proj._departmentId = p.departmentId;
    if (p.projectManagerId) proj._projectManagerId = p.projectManagerId;
    if (p.expectedEndDate) proj._expectedEndDate = p.expectedEndDate;
    if (p.contractNumber) proj._contractNumber = p.contractNumber;
    if (p.contractorId) proj._contractorId = p.contractorId;
    if (p.contractorName) proj._contractorName = p.contractorName;
    if (p.isExternal !== undefined) proj._isExternal = p.isExternal;
    proj.addEvent(FaCipProjectCreated.create(proj._id.value, { projectCode: p.projectCode }));
    return proj;
  }

  static load(state: FaCipProjectState): FaCipProject {
    const p = new FaCipProject(state.projectCode, state.projectName, state.companyId, state.startDate);
    p._id = FaCipProjectId.from(state.id);
    p._totalBudget = state.totalBudget;
    p._totalCost = state.totalCost;
    p._capitalizedAmount = state.capitalizedAmount;
    p._remainingBudget = state.remainingBudget;
    p._projectType = state.projectType;
    p._status = state.status;
    p._branchId = state.branchId;
    p._departmentId = state.departmentId;
    p._projectManagerId = state.projectManagerId;
    p._expectedEndDate = state.expectedEndDate;
    p._actualEndDate = state.actualEndDate;
    p._currencyCode = state.currencyCode;
    p._description = state.description;
    p._contractNumber = state.contractNumber;
    p._contractorId = state.contractorId;
    p._contractorName = state.contractorName;
    p._isExternal = state.isExternal;
    p._approvalStatus = state.approvalStatus;
    p._approvedById = state.approvedById;
    p._approvedAt = state.approvedAt;
    p._version = state.version;
    p._createdAt = state.createdAt;
    p._updatedAt = state.updatedAt;
    return p;
  }

  get id() { return this._id; }
  get projectCode() { return this._projectCode; }
  get projectName() { return this._projectName; }
  get totalBudget() { return this._totalBudget; }
  get totalCost() { return this._totalCost; }
  get capitalizedAmount() { return this._capitalizedAmount; }
  get remainingBudget() { return this._remainingBudget; }
  get status() { return this._status; }
  get version() { return this._version; }

  addCost(amount: number): void {
    this._totalCost += amount;
    this._remainingBudget = this._totalBudget - this._totalCost;
    this._updatedAt = new Date();
  }

  capitalize(amount: number, assetId: string): void {
    if (amount > this._totalCost - this._capitalizedAmount) {
      throw new DomainError("BusinessRule", "Capitalization amount exceeds remaining un-capitalized cost");
    }
    this._capitalizedAmount += amount;
    this._updatedAt = new Date();
    this.addEvent(FaCipCapitalized.create(this._id.value, { amount, assetId }));
  }

  complete(endDate: Date): void {
    this._actualEndDate = endDate;
    this._status = "completed";
    this._updatedAt = new Date();
  }

  close(): void {
    if (this._capitalizedAmount < this._totalCost) {
      throw new DomainError("BusinessRule", "Cannot close project with uncapitalized costs");
    }
    this._status = "closed";
    this._updatedAt = new Date();
  }

  toState(): FaCipProjectState {
    return {
      id: this._id.value, projectCode: this._projectCode,
      projectName: this._projectName, companyId: this._companyId,
      startDate: this._startDate, totalBudget: this._totalBudget,
      totalCost: this._totalCost, capitalizedAmount: this._capitalizedAmount,
      remainingBudget: this._remainingBudget, projectType: this._projectType,
      status: this._status, branchId: this._branchId,
      departmentId: this._departmentId, projectManagerId: this._projectManagerId,
      expectedEndDate: this._expectedEndDate, actualEndDate: this._actualEndDate,
      currencyCode: this._currencyCode, description: this._description,
      contractNumber: this._contractNumber, contractorId: this._contractorId,
      contractorName: this._contractorName, isExternal: this._isExternal,
      approvalStatus: this._approvalStatus, approvedById: this._approvedById,
      approvedAt: this._approvedAt, version: this._version,
      createdAt: this._createdAt, updatedAt: this._updatedAt,
    };
  }
}
