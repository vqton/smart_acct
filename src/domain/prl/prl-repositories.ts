import { PayrollGroup } from "./payroll-group.js";
import { PayrollGroupId } from "./prl-ids.js";
import { SalaryComponent } from "./salary-component.js";
import { SalaryComponentId } from "./prl-ids.js";
import { EmployeePayroll } from "./employee-payroll.js";
import { EmployeePayrollId } from "./prl-ids.js";
import { PayrollRun } from "./payroll-run.js";
import { PayrollRunId } from "./prl-ids.js";
import { InsuranceRate } from "./insurance-rate.js";
import { InsuranceRateId } from "./prl-ids.js";
import { TaxBracket } from "./tax-bracket.js";
import { TaxBracketId } from "./prl-ids.js";

export interface PayrollGroupRepository {
  save(group: PayrollGroup): Promise<void>;
  findById(id: PayrollGroupId): Promise<PayrollGroup | null>;
  findByCode(code: string): Promise<PayrollGroup | null>;
  findAll(companyId?: string): Promise<PayrollGroup[]>;
  findActive(): Promise<PayrollGroup[]>;
  delete(id: PayrollGroupId): Promise<void>;
}

export interface SalaryComponentRepository {
  save(component: SalaryComponent): Promise<void>;
  findById(id: SalaryComponentId): Promise<SalaryComponent | null>;
  findByCode(code: string): Promise<SalaryComponent | null>;
  findAll(): Promise<SalaryComponent[]>;
  findByCategory(category: string): Promise<SalaryComponent[]>;
  findActive(): Promise<SalaryComponent[]>;
  delete(id: SalaryComponentId): Promise<void>;
}

export interface EmployeePayrollRepository {
  save(employee: EmployeePayroll): Promise<void>;
  findById(id: EmployeePayrollId): Promise<EmployeePayroll | null>;
  findByCode(code: string): Promise<EmployeePayroll | null>;
  findAll(companyId?: string): Promise<EmployeePayroll[]>;
  findByGroup(groupId: string): Promise<EmployeePayroll[]>;
  findActiveByGroup(groupId: string): Promise<EmployeePayroll[]>;
  findByDepartment(departmentId: string): Promise<EmployeePayroll[]>;
  findActive(): Promise<EmployeePayroll[]>;
  delete(id: EmployeePayrollId): Promise<void>;
}

export interface PayrollRunRepository {
  save(run: PayrollRun): Promise<void>;
  findById(id: PayrollRunId): Promise<PayrollRun | null>;
  findByRunNumber(runNumber: string): Promise<PayrollRun | null>;
  findByGroup(groupId: string): Promise<PayrollRun[]>;
  findByPeriod(periodId: string): Promise<PayrollRun[]>;
  findByStatus(status: string): Promise<PayrollRun[]>;
  findLatestByGroup(groupId: string): Promise<PayrollRun | null>;
  delete(id: PayrollRunId): Promise<void>;
}

export interface InsuranceRateRepository {
  save(rate: InsuranceRate): Promise<void>;
  findById(id: InsuranceRateId): Promise<InsuranceRate | null>;
  findByType(insuranceType: string): Promise<InsuranceRate[]>;
  findActive(): Promise<InsuranceRate[]>;
  findEffective(date: Date): Promise<InsuranceRate[]>;
  delete(id: InsuranceRateId): Promise<void>;
}

export interface TaxBracketRepository {
  save(bracket: TaxBracket): Promise<void>;
  findById(id: TaxBracketId): Promise<TaxBracket | null>;
  findActive(): Promise<TaxBracket[]>;
  findEffective(date: Date): Promise<TaxBracket[]>;
  delete(id: TaxBracketId): Promise<void>;
}
