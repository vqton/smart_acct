import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { PayrollRunId, PayrollLineId, PayrollElementId, EmployeePayrollId } from "./prl-ids.js";
import { PayrollRunStatus, ElementCategory } from "./prl-enums.js";
import {
  PayrollRunCreated, PayrollRunCalculated, PayrollRunApproved,
  PayrollRunPosted, PayrollRunPaid, PayrollRunReversed,
  PayrollLineCalculated,
} from "./prl-events.js";
import { SalaryComponent } from "./salary-component.js";
import { InsuranceRate } from "./insurance-rate.js";
import { TaxBracket } from "./tax-bracket.js";

export interface PayrollElementState {
  id: string;
  lineId: string;
  componentId: string;
  elementName: string;
  elementType: string;
  category: string;
  amount: bigint;
  baseAmount: bigint;
  quantity: number | null;
  rate: number | null;
  isTaxable: boolean;
  isInsurable: boolean;
  isPITable: boolean;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export class PayrollElement {
  private _id: PayrollElementId;
  private _lineId: string;
  private _componentId: string;
  private _elementName: string;
  private _elementType: string;
  private _category: string;
  private _amount: bigint;
  private _baseAmount: bigint;
  private _quantity: number | null;
  private _rate: number | null;
  private _isTaxable: boolean;
  private _isInsurable: boolean;
  private _isPITable: boolean;
  private _notes: string | null;

  constructor(params: {
    id?: PayrollElementId; lineId: string; componentId: string;
    elementName: string; elementType: string; category: string;
    amount?: bigint; baseAmount?: bigint; quantity?: number; rate?: number;
    isTaxable?: boolean; isInsurable?: boolean; isPITable?: boolean; notes?: string;
  }) {
    this._id = params.id ?? PayrollElementId.new();
    this._lineId = params.lineId;
    this._componentId = params.componentId;
    this._elementName = params.elementName;
    this._elementType = params.elementType;
    this._category = params.category;
    this._amount = params.amount ?? 0n;
    this._baseAmount = params.baseAmount ?? 0n;
    this._quantity = params.quantity ?? null;
    this._rate = params.rate ?? null;
    this._isTaxable = params.isTaxable ?? true;
    this._isInsurable = params.isInsurable ?? false;
    this._isPITable = params.isPITable ?? true;
    this._notes = params.notes ?? null;
  }

  static load(state: PayrollElementState): PayrollElement {
    return new PayrollElement({
      id: new PayrollElementId(state.id),
      lineId: state.lineId,
      componentId: state.componentId,
      elementName: state.elementName,
      elementType: state.elementType,
      category: state.category,
      amount: state.amount,
      baseAmount: state.baseAmount,
      quantity: state.quantity ?? undefined,
      rate: state.rate ?? undefined,
      isTaxable: state.isTaxable,
      isInsurable: state.isInsurable,
      isPITable: state.isPITable,
      notes: state.notes ?? undefined,
    });
  }

  toState(): PayrollElementState {
    return {
      id: this._id.value, lineId: this._lineId, componentId: this._componentId,
      elementName: this._elementName, elementType: this._elementType, category: this._category,
      amount: this._amount, baseAmount: this._baseAmount,
      quantity: this._quantity, rate: this._rate,
      isTaxable: this._isTaxable, isInsurable: this._isInsurable, isPITable: this._isPITable,
      notes: this._notes, version: 1, createdAt: new Date(), updatedAt: new Date(), deletedAt: null,
    };
  }

  get id(): PayrollElementId { return this._id; }
  get componentId(): string { return this._componentId; }
  get elementName(): string { return this._elementName; }
  get elementType(): string { return this._elementType; }
  get category(): string { return this._category; }
  get amount(): bigint { return this._amount; }
  get isTaxable(): boolean { return this._isTaxable; }
  get isInsurable(): boolean { return this._isInsurable; }
  get isPITable(): boolean { return this._isPITable; }
}

export interface PayrollLineState {
  id: string;
  runId: string;
  employeeId: string;
  lineNumber: number;
  employeeCode: string;
  employeeName: string;
  departmentId: string | null;
  costCenterId: string | null;
  branchId: string | null;
  taxCode: string | null;
  socialInsuranceNo: string | null;
  bankAccountId: string | null;
  totalEarnings: bigint;
  totalDeductions: bigint;
  grossPay: bigint;
  totalInsurance: bigint;
  totalPIT: bigint;
  netPay: bigint;
  employerCost: bigint;
  workingDays: number;
  overtimeHours: number;
  leaveDays: number;
  absenceDays: number;
  isCalculated: boolean;
  isExcluded: boolean;
  excludeReason: string | null;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
  elements: PayrollElementState[];
}

export class PayrollLine {
  private _id: PayrollLineId;
  private _runId: string;
  private _employeeId: string;
  private _lineNumber: number;
  private _employeeCode: string;
  private _employeeName: string;
  private _departmentId: string | null;
  private _costCenterId: string | null;
  private _branchId: string | null;
  private _taxCode: string | null;
  private _socialInsuranceNo: string | null;
  private _bankAccountId: string | null;
  private _totalEarnings: bigint;
  private _totalDeductions: bigint;
  private _grossPay: bigint;
  private _totalInsurance: bigint;
  private _totalPIT: bigint;
  private _netPay: bigint;
  private _employerCost: bigint;
  private _workingDays: number;
  private _overtimeHours: number;
  private _leaveDays: number;
  private _absenceDays: number;
  private _isCalculated: boolean;
  private _isExcluded: boolean;
  private _excludeReason: string | null = null;
  private _elements: PayrollElement[];

  constructor(params: {
    id?: PayrollLineId; runId: string; employeeId: string; lineNumber: number;
    employeeCode: string; employeeName: string;
    departmentId?: string; costCenterId?: string; branchId?: string;
    taxCode?: string; socialInsuranceNo?: string; bankAccountId?: string;
  }) {
    this._id = params.id ?? PayrollLineId.new();
    this._runId = params.runId;
    this._employeeId = params.employeeId;
    this._lineNumber = params.lineNumber;
    this._employeeCode = params.employeeCode;
    this._employeeName = params.employeeName;
    this._departmentId = params.departmentId ?? null;
    this._costCenterId = params.costCenterId ?? null;
    this._branchId = params.branchId ?? null;
    this._taxCode = params.taxCode ?? null;
    this._socialInsuranceNo = params.socialInsuranceNo ?? null;
    this._bankAccountId = params.bankAccountId ?? null;
    this._totalEarnings = 0n;
    this._totalDeductions = 0n;
    this._grossPay = 0n;
    this._totalInsurance = 0n;
    this._totalPIT = 0n;
    this._netPay = 0n;
    this._employerCost = 0n;
    this._workingDays = 0;
    this._overtimeHours = 0;
    this._leaveDays = 0;
    this._absenceDays = 0;
    this._isCalculated = false;
    this._isExcluded = false;
    this._elements = [];
  }

  addElement(element: PayrollElement): void {
    this._elements.push(element);
  }

  calculate(
    employeeSalary: Map<string, bigint>,
    insuranceRates: InsuranceRate[],
    taxBrackets: TaxBracket[],
    familyDeduction: bigint,
    dependentCount: number,
  ): void {
    let totalEarnings = 0n;
    let totalDeductions = 0n;
    let totalInsurableEE = 0n;
    let totalInsurableER = 0n;

    for (const el of this._elements) {
      if (el.category === ElementCategory.EARNING || el.category === ElementCategory.EMPLOYER_CONTRIBUTION) {
        totalEarnings += el.amount;
      } else {
        totalDeductions += el.amount;
      }
    }

    const grossPay = totalEarnings;
    let insuranceEE = 0n;
    let insuranceER = 0n;

    for (const ir of insuranceRates) {
      if (!ir.isActive) continue;
      insuranceEE += ir.calculateEmployeeContribution(grossPay);
      insuranceER += ir.calculateEmployerContribution(grossPay);
    }

    let taxableIncome = grossPay - insuranceEE;
    const familyDeductionTotal = familyDeduction * BigInt(dependentCount > 0 ? dependentCount : 1);
    taxableIncome = taxableIncome > familyDeductionTotal ? taxableIncome - familyDeductionTotal : 0n;

    let pitAmount = 0n;
    if (taxableIncome > 0n) {
      const sorted = [...taxBrackets].sort((a, b) => a.bracketOrder - b.bracketOrder);
      for (const bracket of sorted) {
        pitAmount += bracket.calculateTax(taxableIncome);
      }
    }

    const netPay = grossPay - insuranceEE - pitAmount - totalDeductions;

    this._totalEarnings = totalEarnings;
    this._totalDeductions = totalDeductions;
    this._grossPay = grossPay;
    this._totalInsurance = insuranceEE;
    this._totalPIT = pitAmount;
    this._netPay = netPay < 0n ? 0n : netPay;
    this._employerCost = insuranceER;
    this._isCalculated = true;
  }

  static load(state: PayrollLineState): PayrollLine {
    const line = new PayrollLine({
      id: new PayrollLineId(state.id), runId: state.runId, employeeId: state.employeeId,
      lineNumber: state.lineNumber, employeeCode: state.employeeCode, employeeName: state.employeeName,
      departmentId: state.departmentId ?? undefined, costCenterId: state.costCenterId ?? undefined,
      branchId: state.branchId ?? undefined, taxCode: state.taxCode ?? undefined,
      socialInsuranceNo: state.socialInsuranceNo ?? undefined, bankAccountId: state.bankAccountId ?? undefined,
    });
    line._totalEarnings = state.totalEarnings;
    line._totalDeductions = state.totalDeductions;
    line._grossPay = state.grossPay;
    line._totalInsurance = state.totalInsurance;
    line._totalPIT = state.totalPIT;
    line._netPay = state.netPay;
    line._employerCost = state.employerCost;
    line._workingDays = state.workingDays;
    line._overtimeHours = state.overtimeHours;
    line._leaveDays = state.leaveDays;
    line._absenceDays = state.absenceDays;
    line._isCalculated = state.isCalculated;
    line._isExcluded = state.isExcluded;
    line._excludeReason = state.excludeReason;
    line._elements = (state.elements ?? []).map(PayrollElement.load);
    return line;
  }

  toState(): PayrollLineState {
    return {
      id: this._id.value, runId: this._runId, employeeId: this._employeeId,
      lineNumber: this._lineNumber, employeeCode: this._employeeCode, employeeName: this._employeeName,
      departmentId: this._departmentId, costCenterId: this._costCenterId, branchId: this._branchId,
      taxCode: this._taxCode, socialInsuranceNo: this._socialInsuranceNo, bankAccountId: this._bankAccountId,
      totalEarnings: this._totalEarnings, totalDeductions: this._totalDeductions, grossPay: this._grossPay,
      totalInsurance: this._totalInsurance, totalPIT: this._totalPIT, netPay: this._netPay,
      employerCost: this._employerCost,
      workingDays: this._workingDays, overtimeHours: this._overtimeHours,
      leaveDays: this._leaveDays, absenceDays: this._absenceDays,
      isCalculated: this._isCalculated, isExcluded: this._isExcluded,
      excludeReason: this._excludeReason, notes: null,
      version: 1, createdAt: new Date(), updatedAt: new Date(), deletedAt: null,
      elements: this._elements.map(e => e.toState()),
    };
  }

  setReversalValues(source: PayrollLineState): void {
    this._isCalculated = true;
    this._totalEarnings = -source.totalEarnings;
    this._totalDeductions = -source.totalDeductions;
    this._grossPay = -source.grossPay;
    this._totalInsurance = -source.totalInsurance;
    this._totalPIT = -source.totalPIT;
    this._netPay = -source.netPay;
    this._employerCost = -source.employerCost;
  }

  get id(): PayrollLineId { return this._id; }
  get employeeId(): string { return this._employeeId; }
  get lineNumber(): number { return this._lineNumber; }
  get totalEarnings(): bigint { return this._totalEarnings; }
  get totalDeductions(): bigint { return this._totalDeductions; }
  get grossPay(): bigint { return this._grossPay; }
  get totalInsurance(): bigint { return this._totalInsurance; }
  get totalPIT(): bigint { return this._totalPIT; }
  get netPay(): bigint { return this._netPay; }
  get employerCost(): bigint { return this._employerCost; }
  get isCalculated(): boolean { return this._isCalculated; }
  get isExcluded(): boolean { return this._isExcluded; }
  get elements(): PayrollElement[] { return this._elements; }
  get departmentId(): string | null { return this._departmentId; }
  get costCenterId(): string | null { return this._costCenterId; }
  get branchId(): string | null { return this._branchId; }
  get employeeCode(): string { return this._employeeCode; }
  get employeeName(): string { return this._employeeName; }
  get taxCode(): string | null { return this._taxCode; }
}

export interface PayrollRunState {
  id: string;
  runNumber: string;
  groupId: string;
  periodId: string;
  calendarId: string;
  name: string;
  status: string;
  companyId: string;
  branchId: string | null;
  currencyCode: string;
  exchangeRate: number;
  totalEarnings: bigint;
  totalDeductions: bigint;
  totalEmployerCost: bigint;
  totalNetPay: bigint;
  totalPIT: bigint;
  totalInsurance: bigint;
  employeeCount: number;
  calculationDate: Date | null;
  approvedDate: Date | null;
  approvedById: string | null;
  postedDate: Date | null;
  postedById: string | null;
  paidDate: Date | null;
  paidById: string | null;
  reversedDate: Date | null;
  reversedById: string | null;
  reverseOfId: string | null;
  glBatchId: string | null;
  postedToGL: boolean;
  notes: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
  lines: PayrollLineState[];
}

export class PayrollRun extends AggregateRoot<PayrollRunId> {
  private _id: PayrollRunId;
  private _runNumber: string;
  private _groupId: string;
  private _periodId: string;
  private _calendarId: string;
  private _name: string;
  private _status: string;
  private _companyId: string;
  private _branchId: string | null;
  private _currencyCode: string;
  private _exchangeRate: number;
  private _totalEarnings: bigint;
  private _totalDeductions: bigint;
  private _totalEmployerCost: bigint;
  private _totalNetPay: bigint;
  private _totalPIT: bigint;
  private _totalInsurance: bigint;
  private _employeeCount: number;
  private _calculationDate: Date | null;
  private _approvedDate: Date | null;
  private _approvedById: string | null;
  private _postedDate: Date | null;
  private _postedById: string | null;
  private _paidDate: Date | null;
  private _paidById: string | null;
  private _reversedDate: Date | null;
  private _reversedById: string | null;
  private _reverseOfId: string | null;
  private _glBatchId: string | null;
  private _postedToGL: boolean;
  private _notes: string | null;
  private _lines: PayrollLine[];
  private _version: number;
  private _createdAt: Date;
  private _updatedAt: Date;
  private _deletedAt: Date | null;

  private constructor(
    id: PayrollRunId, runNumber: string, groupId: string,
    periodId: string, calendarId: string, name: string, companyId: string,
  ) {
    super();
    this._id = id;
    this._runNumber = runNumber;
    this._groupId = groupId;
    this._periodId = periodId;
    this._calendarId = calendarId;
    this._name = name;
    this._companyId = companyId;
    this._status = PayrollRunStatus.DRAFT;
    this._branchId = null;
    this._currencyCode = "VND";
    this._exchangeRate = 1;
    this._totalEarnings = 0n;
    this._totalDeductions = 0n;
    this._totalEmployerCost = 0n;
    this._totalNetPay = 0n;
    this._totalPIT = 0n;
    this._totalInsurance = 0n;
    this._employeeCount = 0;
    this._calculationDate = null;
    this._approvedDate = null;
    this._approvedById = null;
    this._postedDate = null;
    this._postedById = null;
    this._paidDate = null;
    this._paidById = null;
    this._reversedDate = null;
    this._reversedById = null;
    this._reverseOfId = null;
    this._glBatchId = null;
    this._postedToGL = false;
    this._notes = null;
    this._lines = [];
    this._version = 1;
    this._createdAt = new Date();
    this._updatedAt = new Date();
    this._deletedAt = null;
  }

  static create(params: {
    runNumber: string; groupId: string; periodId: string;
    calendarId: string; name: string; companyId: string;
    branchId?: string; currencyCode?: string;
  }): PayrollRun {
    if (!params.runNumber) throw new DomainError("Validation", "Run number is required");
    if (!params.groupId) throw new DomainError("Validation", "Payroll group is required");
    if (!params.periodId) throw new DomainError("Validation", "Period is required");
    if (!params.companyId) throw new DomainError("Validation", "Company is required");

    const run = new PayrollRun(
      PayrollRunId.new(), params.runNumber, params.groupId,
      params.periodId, params.calendarId, params.name, params.companyId,
    );
    run._branchId = params.branchId ?? null;
    run._currencyCode = params.currencyCode ?? "VND";
    run.addEvent(new PayrollRunCreated(run._id.value, new Date(), {
      runNumber: run._runNumber, groupId: run._groupId, periodId: run._periodId,
    }));
    return run;
  }

  addLine(line: PayrollLine): void {
    if (this._status !== PayrollRunStatus.DRAFT) {
      throw new DomainError("BusinessRule", "Can only add lines to draft payroll run");
    }
    if (this._lines.some(l => l.employeeId === line.employeeId)) {
      throw new DomainError("BusinessRule", "Employee already in payroll run");
    }
    this._lines.push(line);
  }

  calculate(
    employeeSalaries: Map<string, Map<string, bigint>>,
    insuranceRates: InsuranceRate[],
    taxBrackets: TaxBracket[],
    familyDeduction: bigint,
    dependentCounts: Map<string, number>,
  ): void {
    if (this._status !== PayrollRunStatus.DRAFT) {
      throw new DomainError("BusinessRule", "Can only calculate draft payroll run");
    }
    if (this._lines.length === 0) {
      throw new DomainError("BusinessRule", "No employees in payroll run");
    }

    for (const line of this._lines) {
      const salaries = employeeSalaries.get(line.employeeId) ?? new Map();
      const deps = dependentCounts.get(line.employeeId) ?? 0;
      line.calculate(salaries, insuranceRates, taxBrackets, familyDeduction, deps);
    }

    this._recalculateTotals();
    this._status = PayrollRunStatus.CALCULATED;
    this._calculationDate = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new PayrollRunCalculated(this._id.value, new Date(), {
      runNumber: this._runNumber, totalNetPay: this._totalNetPay.toString(),
    }));
  }

  approve(approvedById: string): void {
    if (this._status !== PayrollRunStatus.CALCULATED) {
      throw new DomainError("BusinessRule", "Can only approve calculated payroll run");
    }
    this._status = PayrollRunStatus.APPROVED;
    this._approvedById = approvedById;
    this._approvedDate = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new PayrollRunApproved(this._id.value, new Date(), {
      approvedById, runNumber: this._runNumber,
    }));
  }

  post(postedById: string): void {
    if (this._status !== PayrollRunStatus.APPROVED) {
      throw new DomainError("BusinessRule", "Can only post approved payroll run");
    }
    this._status = PayrollRunStatus.POSTED;
    this._postedById = postedById;
    this._postedDate = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new PayrollRunPosted(this._id.value, new Date(), {
      postedById, runNumber: this._runNumber,
    }));
  }

  markPaid(paidById: string): void {
    if (this._status !== PayrollRunStatus.POSTED) {
      throw new DomainError("BusinessRule", "Can only mark posted payroll run as paid");
    }
    this._status = PayrollRunStatus.PAID;
    this._paidById = paidById;
    this._paidDate = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new PayrollRunPaid(this._id.value, new Date(), {
      paidById, runNumber: this._runNumber,
    }));
  }

  reverse(reversedById: string): PayrollRun {
    if (this._status !== PayrollRunStatus.PAID && this._status !== PayrollRunStatus.POSTED) {
      throw new DomainError("BusinessRule", "Can only reverse posted or paid payroll run");
    }
    const reversed = new PayrollRun(
      PayrollRunId.new(), `${this._runNumber}-REV`, this._groupId,
      this._periodId, this._calendarId, `REVERSAL: ${this._name}`, this._companyId,
    );
    reversed._reverseOfId = this._id.value;
    reversed._branchId = this._branchId;
    reversed._currencyCode = this._currencyCode;
    reversed._lines = this._lines.map(l => {
      const revLine = new PayrollLine({
        runId: reversed._id.value, employeeId: l.employeeId, lineNumber: l.lineNumber,
        employeeCode: l.employeeCode, employeeName: l.employeeName,
        departmentId: l.departmentId ?? undefined, costCenterId: l.costCenterId ?? undefined,
        branchId: l.branchId ?? undefined,
      });
      for (const el of l.elements) {
        revLine.addElement(new PayrollElement({
          lineId: revLine.id.value, componentId: el.componentId,
          elementName: el.elementName, elementType: el.elementType, category: el.category,
          amount: -el.amount, baseAmount: el.amount, isTaxable: el.isTaxable,
          isInsurable: el.isInsurable, isPITable: el.isPITable, notes: "Reversal",
        }));
      }
      revLine.setReversalValues(l.toState());
      return revLine;
    });
    reversed._recalculateTotals();
    reversed._status = PayrollRunStatus.CALCULATED;

    this._status = PayrollRunStatus.REVERSED;
    this._reversedById = reversedById;
    this._reversedDate = new Date();
    this._version++;
    this._updatedAt = new Date();
    this.addEvent(new PayrollRunReversed(this._id.value, new Date(), {
      reversedById, runNumber: this._runNumber, reversalRunId: reversed._id.value,
    }));
    return reversed;
  }

  cancel(): void {
    if (this._status !== PayrollRunStatus.DRAFT) {
      throw new DomainError("BusinessRule", "Can only cancel draft payroll run");
    }
    this._status = PayrollRunStatus.CANCELLED;
    this._version++;
    this._updatedAt = new Date();
  }

  markGLPosted(glBatchId: string): void {
    this._glBatchId = glBatchId;
    this._postedToGL = true;
    this._version++;
    this._updatedAt = new Date();
  }

  private _recalculateTotals(): void {
    this._totalEarnings = 0n;
    this._totalDeductions = 0n;
    this._totalEmployerCost = 0n;
    this._totalNetPay = 0n;
    this._totalPIT = 0n;
    this._totalInsurance = 0n;
    this._employeeCount = 0;

    for (const line of this._lines) {
      if (line.isExcluded) continue;
      this._totalEarnings += line.totalEarnings;
      this._totalDeductions += line.totalDeductions;
      this._totalEmployerCost += line.employerCost;
      this._totalNetPay += line.netPay;
      this._totalPIT += line.totalPIT;
      this._totalInsurance += line.totalInsurance;
      this._employeeCount++;
    }
  }

  static load(state: PayrollRunState): PayrollRun {
    const run = new PayrollRun(
      new PayrollRunId(state.id), state.runNumber, state.groupId,
      state.periodId, state.calendarId, state.name, state.companyId,
    );
    run._status = state.status;
    run._branchId = state.branchId;
    run._currencyCode = state.currencyCode;
    run._exchangeRate = state.exchangeRate;
    run._totalEarnings = state.totalEarnings;
    run._totalDeductions = state.totalDeductions;
    run._totalEmployerCost = state.totalEmployerCost;
    run._totalNetPay = state.totalNetPay;
    run._totalPIT = state.totalPIT;
    run._totalInsurance = state.totalInsurance;
    run._employeeCount = state.employeeCount;
    run._calculationDate = state.calculationDate;
    run._approvedDate = state.approvedDate;
    run._approvedById = state.approvedById;
    run._postedDate = state.postedDate;
    run._postedById = state.postedById;
    run._paidDate = state.paidDate;
    run._paidById = state.paidById;
    run._reversedDate = state.reversedDate;
    run._reversedById = state.reversedById;
    run._reverseOfId = state.reverseOfId;
    run._glBatchId = state.glBatchId;
    run._postedToGL = state.postedToGL;
    run._notes = state.notes;
    run._version = state.version;
    run._createdAt = state.createdAt;
    run._updatedAt = state.updatedAt;
    run._deletedAt = state.deletedAt;
    run._lines = (state.lines ?? []).map(PayrollLine.load);
    return run;
  }

  toState(): PayrollRunState {
    return {
      id: this._id.value, runNumber: this._runNumber, groupId: this._groupId,
      periodId: this._periodId, calendarId: this._calendarId, name: this._name,
      status: this._status, companyId: this._companyId, branchId: this._branchId,
      currencyCode: this._currencyCode, exchangeRate: this._exchangeRate,
      totalEarnings: this._totalEarnings, totalDeductions: this._totalDeductions,
      totalEmployerCost: this._totalEmployerCost, totalNetPay: this._totalNetPay,
      totalPIT: this._totalPIT, totalInsurance: this._totalInsurance,
      employeeCount: this._employeeCount, calculationDate: this._calculationDate,
      approvedDate: this._approvedDate, approvedById: this._approvedById,
      postedDate: this._postedDate, postedById: this._postedById,
      paidDate: this._paidDate, paidById: this._paidById,
      reversedDate: this._reversedDate, reversedById: this._reversedById,
      reverseOfId: this._reverseOfId, glBatchId: this._glBatchId,
      postedToGL: this._postedToGL, notes: this._notes,
      version: this._version, createdAt: this._createdAt,
      updatedAt: this._updatedAt, deletedAt: this._deletedAt,
      lines: this._lines.map(l => l.toState()),
    };
  }

  get id(): PayrollRunId { return this._id; }
  get runNumber(): string { return this._runNumber; }
  get groupId(): string { return this._groupId; }
  get periodId(): string { return this._periodId; }
  get status(): string { return this._status; }
  get lines(): PayrollLine[] { return this._lines; }
  get totalEarnings(): bigint { return this._totalEarnings; }
  get totalDeductions(): bigint { return this._totalDeductions; }
  get totalEmployerCost(): bigint { return this._totalEmployerCost; }
  get totalNetPay(): bigint { return this._totalNetPay; }
  get totalPIT(): bigint { return this._totalPIT; }
  get totalInsurance(): bigint { return this._totalInsurance; }
  get employeeCount(): number { return this._employeeCount; }
  get isPostedToGL(): boolean { return this._postedToGL; }
  get version(): number { return this._version; }
  get companyId(): string { return this._companyId; }
  get branchId(): string | null { return this._branchId; }
  get currencyCode(): string { return this._currencyCode; }
}
