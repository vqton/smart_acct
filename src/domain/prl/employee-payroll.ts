import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { EmployeePayrollId } from "./prl-ids.js";
import { EmployeePayrollCreated, EmployeePayrollUpdated, EmployeePayrollTerminated } from "./prl-events.js";

export interface EmployeePayrollState {
  id: string;
  employeeCode: string;
  employeeName: string;
  fullName: string | null;
  gender: string | null;
  dateOfBirth: Date | null;
  identityNumber: string | null;
  taxCode: string | null;
  socialInsuranceNo: string | null;
  healthInsuranceNo: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  companyId: string;
  branchId: string | null;
  departmentId: string | null;
  divisionId: string | null;
  sectionId: string | null;
  positionId: string | null;
  jobGradeId: string | null;
  costCenterId: string | null;
  groupId: string;
  payFrequency: string | null;
  currencyCode: string;
  paymentMethod: string;
  employmentType: string;
  hireDate: Date;
  contractEndDate: Date | null;
  terminationDate: Date | null;
  isActive: boolean;
  isPITRegistered: boolean;
  isSIEnrolled: boolean;
  isHIEnrolled: boolean;
  isUIEnrolled: boolean;
  dependentCount: number;
  approvedById: string | null;
  approvedAt: Date | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class EmployeePayroll extends AggregateRoot<EmployeePayrollId> {
  private _id: EmployeePayrollId;
  private _employeeCode: string;
  private _employeeName: string;
  private _fullName: string | null = null;
  private _gender: string | null = null;
  private _dateOfBirth: Date | null = null;
  private _identityNumber: string | null = null;
  private _taxCode: string | null = null;
  private _socialInsuranceNo: string | null = null;
  private _healthInsuranceNo: string | null = null;
  private _phone: string | null = null;
  private _email: string | null = null;
  private _address: string | null = null;
  private _companyId: string;
  private _branchId: string | null = null;
  private _departmentId: string | null = null;
  private _divisionId: string | null = null;
  private _sectionId: string | null = null;
  private _positionId: string | null = null;
  private _jobGradeId: string | null = null;
  private _costCenterId: string | null = null;
  private _groupId: string;
  private _payFrequency: string | null = null;
  private _currencyCode: string;
  private _paymentMethod: string;
  private _employmentType: string;
  private _hireDate: Date;
  private _contractEndDate: Date | null = null;
  private _terminationDate: Date | null = null;
  private _isActive: boolean;
  private _isPITRegistered: boolean;
  private _isSIEnrolled: boolean;
  private _isHIEnrolled: boolean;
  private _isUIEnrolled: boolean;
  private _dependentCount: number;
  private _approvedById: string | null = null;
  private _approvedAt: Date | null = null;
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(id: EmployeePayrollId, employeeCode: string, employeeName: string, companyId: string, groupId: string, hireDate: Date) {
    super();
    this._id = id;
    this._employeeCode = employeeCode;
    this._employeeName = employeeName;
    this._companyId = companyId;
    this._groupId = groupId;
    this._hireDate = hireDate;
    this._paymentMethod = "bank_transfer";
    this._employmentType = "indefinite";
    this._currencyCode = "VND";
    this._isActive = true;
    this._isPITRegistered = false;
    this._isSIEnrolled = true;
    this._isHIEnrolled = true;
    this._isUIEnrolled = true;
    this._dependentCount = 0;
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    employeeCode: string; employeeName: string; fullName?: string;
    gender?: string; dateOfBirth?: Date; identityNumber?: string;
    taxCode?: string; socialInsuranceNo?: string; healthInsuranceNo?: string;
    phone?: string; email?: string; address?: string;
    companyId: string; branchId?: string;
    departmentId?: string; divisionId?: string; sectionId?: string;
    positionId?: string; jobGradeId?: string; costCenterId?: string;
    groupId: string; payFrequency?: string; currencyCode?: string;
    paymentMethod?: string; employmentType?: string; hireDate: Date;
    contractEndDate?: Date;
    isPITRegistered?: boolean; isSIEnrolled?: boolean; isHIEnrolled?: boolean; isUIEnrolled?: boolean;
    dependentCount?: number;
  }): EmployeePayroll {
    if (!params.employeeCode) throw new DomainError("Validation", "Employee code is required");
    if (!params.employeeName) throw new DomainError("Validation", "Employee name is required");
    if (!params.companyId) throw new DomainError("Validation", "Company is required");
    if (!params.groupId) throw new DomainError("Validation", "Payroll group is required");
    if (!params.hireDate) throw new DomainError("Validation", "Hire date is required");

    const emp = new EmployeePayroll(EmployeePayrollId.new(), params.employeeCode, params.employeeName, params.companyId, params.groupId, params.hireDate);
    emp._fullName = params.fullName ?? null;
    emp._gender = params.gender ?? null;
    emp._dateOfBirth = params.dateOfBirth ?? null;
    emp._identityNumber = params.identityNumber ?? null;
    emp._taxCode = params.taxCode ?? null;
    emp._socialInsuranceNo = params.socialInsuranceNo ?? null;
    emp._healthInsuranceNo = params.healthInsuranceNo ?? null;
    emp._phone = params.phone ?? null;
    emp._email = params.email ?? null;
    emp._address = params.address ?? null;
    emp._branchId = params.branchId ?? null;
    emp._departmentId = params.departmentId ?? null;
    emp._divisionId = params.divisionId ?? null;
    emp._sectionId = params.sectionId ?? null;
    emp._positionId = params.positionId ?? null;
    emp._jobGradeId = params.jobGradeId ?? null;
    emp._costCenterId = params.costCenterId ?? null;
    emp._payFrequency = params.payFrequency ?? null;
    emp._currencyCode = params.currencyCode ?? "VND";
    emp._paymentMethod = params.paymentMethod ?? "bank_transfer";
    emp._employmentType = params.employmentType ?? "indefinite";
    emp._contractEndDate = params.contractEndDate ?? null;
    emp._isPITRegistered = params.isPITRegistered ?? false;
    emp._isSIEnrolled = params.isSIEnrolled ?? true;
    emp._isHIEnrolled = params.isHIEnrolled ?? true;
    emp._isUIEnrolled = params.isUIEnrolled ?? true;
    emp._dependentCount = params.dependentCount ?? 0;

    emp.addEvent(new EmployeePayrollCreated(emp._id.value, new Date(), {
      employeeCode: emp._employeeCode, employeeName: emp._employeeName, companyId: emp._companyId,
    }));
    return emp;
  }

  static load(state: EmployeePayrollState): EmployeePayroll {
    const emp = new EmployeePayroll(new EmployeePayrollId(state.id), state.employeeCode, state.employeeName, state.companyId, state.groupId, state.hireDate);
    emp._fullName = state.fullName;
    emp._gender = state.gender;
    emp._dateOfBirth = state.dateOfBirth;
    emp._identityNumber = state.identityNumber;
    emp._taxCode = state.taxCode;
    emp._socialInsuranceNo = state.socialInsuranceNo;
    emp._healthInsuranceNo = state.healthInsuranceNo;
    emp._phone = state.phone;
    emp._email = state.email;
    emp._address = state.address;
    emp._branchId = state.branchId;
    emp._departmentId = state.departmentId;
    emp._divisionId = state.divisionId;
    emp._sectionId = state.sectionId;
    emp._positionId = state.positionId;
    emp._jobGradeId = state.jobGradeId;
    emp._costCenterId = state.costCenterId;
    emp._payFrequency = state.payFrequency;
    emp._currencyCode = state.currencyCode;
    emp._paymentMethod = state.paymentMethod;
    emp._employmentType = state.employmentType;
    emp._contractEndDate = state.contractEndDate;
    emp._terminationDate = state.terminationDate;
    emp._isActive = state.isActive;
    emp._isPITRegistered = state.isPITRegistered;
    emp._isSIEnrolled = state.isSIEnrolled;
    emp._isHIEnrolled = state.isHIEnrolled;
    emp._isUIEnrolled = state.isUIEnrolled;
    emp._dependentCount = state.dependentCount;
    emp._approvedById = state.approvedById;
    emp._approvedAt = state.approvedAt;
    emp._version = state.version;
    emp._createdAt = state.createdAt;
    emp._updatedAt = state.updatedAt;
    emp._deletedAt = state.deletedAt;
    return emp;
  }

  toState(): EmployeePayrollState {
    return {
      id: this._id.value, employeeCode: this._employeeCode, employeeName: this._employeeName,
      fullName: this._fullName, gender: this._gender, dateOfBirth: this._dateOfBirth,
      identityNumber: this._identityNumber, taxCode: this._taxCode,
      socialInsuranceNo: this._socialInsuranceNo, healthInsuranceNo: this._healthInsuranceNo,
      phone: this._phone, email: this._email, address: this._address,
      companyId: this._companyId, branchId: this._branchId,
      departmentId: this._departmentId, divisionId: this._divisionId, sectionId: this._sectionId,
      positionId: this._positionId, jobGradeId: this._jobGradeId, costCenterId: this._costCenterId,
      groupId: this._groupId, payFrequency: this._payFrequency, currencyCode: this._currencyCode,
      paymentMethod: this._paymentMethod, employmentType: this._employmentType,
      hireDate: this._hireDate, contractEndDate: this._contractEndDate, terminationDate: this._terminationDate,
      isActive: this._isActive, isPITRegistered: this._isPITRegistered,
      isSIEnrolled: this._isSIEnrolled, isHIEnrolled: this._isHIEnrolled, isUIEnrolled: this._isUIEnrolled,
      dependentCount: this._dependentCount, approvedById: this._approvedById, approvedAt: this._approvedAt,
      version: this._version, createdAt: this._createdAt, updatedAt: this._updatedAt, deletedAt: this._deletedAt,
    };
  }

  update(params: {
    employeeName?: string; fullName?: string; gender?: string;
    dateOfBirth?: Date; identityNumber?: string; taxCode?: string;
    socialInsuranceNo?: string; healthInsuranceNo?: string;
    phone?: string; email?: string; address?: string;
    branchId?: string; departmentId?: string; positionId?: string;
    jobGradeId?: string; costCenterId?: string; groupId?: string;
    payFrequency?: string; currencyCode?: string; paymentMethod?: string;
    employmentType?: string; contractEndDate?: Date;
    isPITRegistered?: boolean; isSIEnrolled?: boolean; isHIEnrolled?: boolean; isUIEnrolled?: boolean;
    dependentCount?: number;
  }): void {
    if (params.employeeName !== undefined) this._employeeName = params.employeeName;
    if (params.fullName !== undefined) this._fullName = params.fullName;
    if (params.gender !== undefined) this._gender = params.gender;
    if (params.dateOfBirth !== undefined) this._dateOfBirth = params.dateOfBirth;
    if (params.identityNumber !== undefined) this._identityNumber = params.identityNumber;
    if (params.taxCode !== undefined) this._taxCode = params.taxCode;
    if (params.socialInsuranceNo !== undefined) this._socialInsuranceNo = params.socialInsuranceNo;
    if (params.healthInsuranceNo !== undefined) this._healthInsuranceNo = params.healthInsuranceNo;
    if (params.phone !== undefined) this._phone = params.phone;
    if (params.email !== undefined) this._email = params.email;
    if (params.address !== undefined) this._address = params.address;
    if (params.branchId !== undefined) this._branchId = params.branchId;
    if (params.departmentId !== undefined) this._departmentId = params.departmentId;
    if (params.positionId !== undefined) this._positionId = params.positionId;
    if (params.jobGradeId !== undefined) this._jobGradeId = params.jobGradeId;
    if (params.costCenterId !== undefined) this._costCenterId = params.costCenterId;
    if (params.groupId !== undefined) this._groupId = params.groupId;
    if (params.payFrequency !== undefined) this._payFrequency = params.payFrequency;
    if (params.currencyCode !== undefined) this._currencyCode = params.currencyCode;
    if (params.paymentMethod !== undefined) this._paymentMethod = params.paymentMethod;
    if (params.employmentType !== undefined) this._employmentType = params.employmentType;
    if (params.contractEndDate !== undefined) this._contractEndDate = params.contractEndDate;
    if (params.isPITRegistered !== undefined) this._isPITRegistered = params.isPITRegistered;
    if (params.isSIEnrolled !== undefined) this._isSIEnrolled = params.isSIEnrolled;
    if (params.isHIEnrolled !== undefined) this._isHIEnrolled = params.isHIEnrolled;
    if (params.isUIEnrolled !== undefined) this._isUIEnrolled = params.isUIEnrolled;
    if (params.dependentCount !== undefined) this._dependentCount = params.dependentCount;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new EmployeePayrollUpdated(this._id.value, new Date(), { id: this._id.value }));
  }

  terminate(terminationDate: Date): void {
    if (!this._isActive) throw new DomainError("BusinessRule", "Employee already terminated");
    if (this._terminationDate) throw new DomainError("BusinessRule", "Employee already has termination date");
    this._isActive = false;
    this._terminationDate = terminationDate;
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new EmployeePayrollTerminated(this._id.value, new Date(), { terminationDate: terminationDate.toISOString() }));
  }

  markDeleted(): void {
    this._deletedAt = new Date();
    this._version++;
    this._updatedAt = new Date();
  }

  get id(): EmployeePayrollId { return this._id; }
  get employeeCode(): string { return this._employeeCode; }
  get employeeName(): string { return this._employeeName; }
  get companyId(): string { return this._companyId; }
  get groupId(): string { return this._groupId; }
  get departmentId(): string | null { return this._departmentId; }
  get costCenterId(): string | null { return this._costCenterId; }
  get branchId(): string | null { return this._branchId; }
  get taxCode(): string | null { return this._taxCode; }
  get socialInsuranceNo(): string | null { return this._socialInsuranceNo; }
  get dependentCount(): number { return this._dependentCount; }
  get isActive(): boolean { return this._isActive; }
  get isSIEnrolled(): boolean { return this._isSIEnrolled; }
  get isHIEnrolled(): boolean { return this._isHIEnrolled; }
  get isUIEnrolled(): boolean { return this._isUIEnrolled; }
  get isPITRegistered(): boolean { return this._isPITRegistered; }
  get paymentMethod(): string { return this._paymentMethod; }
  get version(): number { return this._version; }
}
