import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import {
  PayrollGroup, PayrollGroupId, PayrollGroupState,
  SalaryComponent, SalaryComponentId, SalaryComponentState,
  EmployeePayroll, EmployeePayrollId, EmployeePayrollState,
  PayrollRun, PayrollRunId, PayrollRunState, PayrollLine, PayrollElement,
  PayrollPeriod, PayrollPeriodId, PayrollPeriodState,
  InsuranceRate, InsuranceRateId, InsuranceRateState,
  TaxBracket, TaxBracketId, TaxBracketState,
} from "../../domain/prl/index.js";
import {
  PrismaPayrollGroupRepository, PrismaSalaryComponentRepository,
  PrismaEmployeePayrollRepository, PrismaPayrollRunRepository,
  PrismaInsuranceRateRepository, PrismaTaxBracketRepository,
  PrismaPayrollPeriodRepository,
} from "../../infrastructure/prl/index.js";

@Injectable()
export class PayrollService {
  constructor(
    private readonly groupRepo: PrismaPayrollGroupRepository,
    private readonly componentRepo: PrismaSalaryComponentRepository,
    private readonly employeeRepo: PrismaEmployeePayrollRepository,
    private readonly runRepo: PrismaPayrollRunRepository,
    private readonly insuranceRepo: PrismaInsuranceRateRepository,
    private readonly taxRepo: PrismaTaxBracketRepository,
    private readonly periodRepo: PrismaPayrollPeriodRepository,
  ) {}

  // ─── Payroll Group ───────────────────────────────────────────────────────

  async createGroup(params: {
    code: string; name: string; description?: string;
    companyId: string; branchId?: string; payFrequency?: string; currencyCode?: string;
  }): Promise<PayrollGroupState> {
    const existing = await this.groupRepo.findByCode(params.code);
    if (existing) throw new DomainError("Conflict", `Payroll group code ${params.code} already exists`);
    const group = PayrollGroup.create(params);
    await this.groupRepo.save(group);
    return group.toState();
  }

  async getGroup(id: string): Promise<PayrollGroupState> {
    const group = await this.groupRepo.findById(new PayrollGroupId(id));
    if (!group) throw new DomainError("NotFound", "Payroll group not found");
    return group.toState();
  }

  async listGroups(companyId?: string): Promise<PayrollGroupState[]> {
    const groups = await this.groupRepo.findAll(companyId);
    return groups.map(g => g.toState());
  }

  async updateGroup(id: string, params: { name?: string; description?: string; payFrequency?: string; currencyCode?: string }): Promise<PayrollGroupState> {
    const group = await this.groupRepo.findById(new PayrollGroupId(id));
    if (!group) throw new DomainError("NotFound", "Payroll group not found");
    group.update(params);
    await this.groupRepo.save(group);
    return group.toState();
  }

  async deactivateGroup(id: string): Promise<PayrollGroupState> {
    const group = await this.groupRepo.findById(new PayrollGroupId(id));
    if (!group) throw new DomainError("NotFound", "Payroll group not found");
    group.deactivate();
    await this.groupRepo.save(group);
    return group.toState();
  }

  async deleteGroup(id: string): Promise<void> {
    await this.groupRepo.delete(new PayrollGroupId(id));
  }

  // ─── Salary Component ────────────────────────────────────────────────────

  async createComponent(params: {
    code: string; name: string; nameEn?: string;
    elementType: string; category: string;
    isTaxable?: boolean; isInsurable?: boolean; isPITable?: boolean;
    priority?: number; formula?: string; defaultValue?: bigint;
    currencyCode?: string; description?: string;
  }): Promise<SalaryComponentState> {
    const existing = await this.componentRepo.findByCode(params.code);
    if (existing) throw new DomainError("Conflict", `Salary component code ${params.code} already exists`);
    const component = SalaryComponent.create(params);
    await this.componentRepo.save(component);
    return component.toState();
  }

  async getComponent(id: string): Promise<SalaryComponentState> {
    const c = await this.componentRepo.findById(new SalaryComponentId(id));
    if (!c) throw new DomainError("NotFound", "Salary component not found");
    return c.toState();
  }

  async listComponents(): Promise<SalaryComponentState[]> {
    const list = await this.componentRepo.findAll();
    return list.map(c => c.toState());
  }

  async deleteComponent(id: string): Promise<void> {
    await this.componentRepo.delete(new SalaryComponentId(id));
  }

  // ─── Employee Payroll ────────────────────────────────────────────────────

  async createEmployee(params: {
    employeeCode: string; employeeName: string; companyId: string;
    groupId: string; hireDate: Date;
    fullName?: string; gender?: string; taxCode?: string;
    socialInsuranceNo?: string; healthInsuranceNo?: string;
    phone?: string; email?: string; departmentId?: string;
    costCenterId?: string; branchId?: string; positionId?: string;
    paymentMethod?: string; employmentType?: string;
    isPITRegistered?: boolean; dependentCount?: number;
  }): Promise<EmployeePayrollState> {
    const existing = await this.employeeRepo.findByCode(params.employeeCode);
    if (existing) throw new DomainError("Conflict", `Employee code ${params.employeeCode} already exists`);
    const emp = EmployeePayroll.create(params);
    await this.employeeRepo.save(emp);
    return emp.toState();
  }

  async getEmployee(id: string): Promise<EmployeePayrollState> {
    const emp = await this.employeeRepo.findById(new EmployeePayrollId(id));
    if (!emp) throw new DomainError("NotFound", "Employee not found");
    return emp.toState();
  }

  async listEmployees(companyId?: string): Promise<EmployeePayrollState[]> {
    const list = await this.employeeRepo.findAll(companyId);
    return list.map(e => e.toState());
  }

  async listEmployeesByGroup(groupId: string): Promise<EmployeePayrollState[]> {
    const list = await this.employeeRepo.findActiveByGroup(groupId);
    return list.map(e => e.toState());
  }

  async updateEmployee(id: string, params: Record<string, unknown>): Promise<EmployeePayrollState> {
    const emp = await this.employeeRepo.findById(new EmployeePayrollId(id));
    if (!emp) throw new DomainError("NotFound", "Employee not found");
    emp.update(params as any);
    await this.employeeRepo.save(emp);
    return emp.toState();
  }

  async terminateEmployee(id: string, terminationDate: Date): Promise<EmployeePayrollState> {
    const emp = await this.employeeRepo.findById(new EmployeePayrollId(id));
    if (!emp) throw new DomainError("NotFound", "Employee not found");
    emp.terminate(terminationDate);
    await this.employeeRepo.save(emp);
    return emp.toState();
  }

  async deleteEmployee(id: string): Promise<void> {
    await this.employeeRepo.delete(new EmployeePayrollId(id));
  }

  // ─── Payroll Period ──────────────────────────────────────────────────────

  async createPeriod(params: {
    calendarId: string; periodNumber: number; name: string;
    startDate: Date; endDate: Date; year: number; month: number;
    paymentDate?: Date;
  }): Promise<PayrollPeriodState> {
    const period = PayrollPeriod.create(params);
    await this.periodRepo.save(period);
    return period.toState();
  }

  async getPeriod(id: string): Promise<PayrollPeriodState> {
    const period = await this.periodRepo.findById(new PayrollPeriodId(id));
    if (!period) throw new DomainError("NotFound", "Payroll period not found");
    return period.toState();
  }

  async listPeriods(calendarId: string): Promise<PayrollPeriodState[]> {
    const list = await this.periodRepo.findByCalendar(calendarId);
    return list.map(p => p.toState());
  }

  async closePeriod(id: string, closedById: string): Promise<PayrollPeriodState> {
    const period = await this.periodRepo.findById(new PayrollPeriodId(id));
    if (!period) throw new DomainError("NotFound", "Payroll period not found");
    period.close(closedById);
    await this.periodRepo.save(period);
    return period.toState();
  }

  // ─── Payroll Run ─────────────────────────────────────────────────────────

  async createRun(params: {
    runNumber: string; groupId: string; periodId: string;
    calendarId: string; name: string; companyId: string;
    branchId?: string; currencyCode?: string;
  }): Promise<PayrollRunState> {
    const existing = await this.runRepo.findByRunNumber(params.runNumber);
    if (existing) throw new DomainError("Conflict", `Payroll run ${params.runNumber} already exists`);
    const run = PayrollRun.create(params);
    await this.runRepo.save(run);
    return run.toState();
  }

  async getRun(id: string): Promise<PayrollRunState> {
    const run = await this.runRepo.findById(new PayrollRunId(id));
    if (!run) throw new DomainError("NotFound", "Payroll run not found");
    return run.toState();
  }

  async listRuns(groupId: string): Promise<PayrollRunState[]> {
    const list = await this.runRepo.findByGroup(groupId);
    return list.map(r => r.toState());
  }

  async addEmployeesToRun(runId: string, employeeIds: string[]): Promise<PayrollRunState> {
    const run = await this.runRepo.findById(new PayrollRunId(runId));
    if (!run) throw new DomainError("NotFound", "Payroll run not found");

    for (const empId of employeeIds) {
      const emp = await this.employeeRepo.findById(new EmployeePayrollId(empId));
      if (!emp) throw new DomainError("NotFound", `Employee ${empId} not found`);
      const line = new PayrollLine({
        runId: run.id.value, employeeId: emp.id.value, lineNumber: run.lines.length + 1,
        employeeCode: emp.employeeCode, employeeName: emp.employeeName,
        departmentId: emp.departmentId ?? undefined, costCenterId: emp.costCenterId ?? undefined,
        branchId: emp.branchId ?? undefined, taxCode: emp.taxCode ?? undefined,
        socialInsuranceNo: emp.socialInsuranceNo ?? undefined,
      });
      run.addLine(line);
    }
    await this.runRepo.save(run);
    return run.toState();
  }

  async calculateRun(runId: string): Promise<PayrollRunState> {
    const run = await this.runRepo.findById(new PayrollRunId(runId));
    if (!run) throw new DomainError("NotFound", "Payroll run not found");

    const insuranceRates = await this.insuranceRepo.findEffective(new Date());
    const taxBrackets = await this.taxRepo.findEffective(new Date());

    const employeeDeps = new Map<string, number>();
    for (const line of run.lines) {
      const emp = await this.employeeRepo.findById(new EmployeePayrollId(line.employeeId));
      if (emp) employeeDeps.set(line.employeeId, emp.dependentCount);
    }

    run.calculate(new Map(), insuranceRates, taxBrackets, 11000000n, employeeDeps);
    await this.runRepo.save(run);
    return run.toState();
  }

  async approveRun(runId: string, approvedById: string): Promise<PayrollRunState> {
    const run = await this.runRepo.findById(new PayrollRunId(runId));
    if (!run) throw new DomainError("NotFound", "Payroll run not found");
    run.approve(approvedById);
    await this.runRepo.save(run);
    return run.toState();
  }

  async postRun(runId: string, postedById: string): Promise<PayrollRunState> {
    const run = await this.runRepo.findById(new PayrollRunId(runId));
    if (!run) throw new DomainError("NotFound", "Payroll run not found");
    run.post(postedById);
    await this.runRepo.save(run);
    return run.toState();
  }

  async reverseRun(runId: string, reversedById: string): Promise<{ reversedRun: PayrollRunState; newRun: PayrollRunState }> {
    const run = await this.runRepo.findById(new PayrollRunId(runId));
    if (!run) throw new DomainError("NotFound", "Payroll run not found");
    const reversalRun = run.reverse(reversedById);
    await this.runRepo.save(run);
    await this.runRepo.save(reversalRun);
    return { reversedRun: run.toState(), newRun: reversalRun.toState() };
  }

  async cancelRun(runId: string): Promise<PayrollRunState> {
    const run = await this.runRepo.findById(new PayrollRunId(runId));
    if (!run) throw new DomainError("NotFound", "Payroll run not found");
    run.cancel();
    await this.runRepo.save(run);
    return run.toState();
  }

  // ─── Insurance Rate ──────────────────────────────────────────────────────

  async createInsuranceRate(params: {
    insuranceType: string; name: string; effectiveFrom: Date;
    eeRate: number; erRate: number; ceilingAmount?: bigint;
    regulationRef?: string;
  }): Promise<InsuranceRateState> {
    const ir = InsuranceRate.create(params);
    await this.insuranceRepo.save(ir);
    return ir.toState();
  }

  async listInsuranceRates(): Promise<InsuranceRateState[]> {
    const list = await this.insuranceRepo.findActive();
    return list.map(r => r.toState());
  }

  // ─── Tax Bracket ─────────────────────────────────────────────────────────

  async createTaxBracket(params: {
    name: string; effectiveFrom: Date; bracketOrder: number;
    fromAmount: bigint; toAmount?: bigint; rate: number;
    deductAmount: bigint; regulationRef?: string;
  }): Promise<TaxBracketState> {
    const tb = TaxBracket.create(params);
    await this.taxRepo.save(tb);
    return tb.toState();
  }

  async listTaxBrackets(): Promise<TaxBracketState[]> {
    const list = await this.taxRepo.findActive();
    return list.map(t => t.toState());
  }
}
