import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import {
  PayrollGroup, PayrollGroupState, PayrollGroupId,
  SalaryComponent, SalaryComponentState, SalaryComponentId,
  EmployeePayroll, EmployeePayrollState, EmployeePayrollId,
  PayrollRun, PayrollRunState, PayrollRunId,
  PayrollPayment, PayrollPaymentState, PayrollPaymentId,
  PayrollPeriod, PayrollPeriodState, PayrollPeriodId,
  InsuranceRate, InsuranceRateState, InsuranceRateId,
  TaxBracket, TaxBracketState, TaxBracketId,
} from "../../domain/prl/index.js";
import {
  PayrollGroupRepository, SalaryComponentRepository,
  EmployeePayrollRepository, PayrollRunRepository,
  InsuranceRateRepository, TaxBracketRepository,
} from "../../domain/prl/prl-repositories.js";

function toBigInt(v: bigint | number | null | undefined): bigint {
  if (v === null || v === undefined) return 0n;
  if (typeof v === "bigint") return v;
  return BigInt(Math.round(v));
}

// ─── PayrollGroup ───────────────────────────────────────────────────────────

function fromPrismaPayrollGroup(row: Record<string, unknown>): PayrollGroup {
  return PayrollGroup.load({
    id: row.id as string,
    code: row.code as string,
    name: row.name as string,
    description: (row.description as string) ?? null,
    companyId: row.companyId as string,
    branchId: (row.branchId as string) ?? null,
    payFrequency: row.payFrequency as string,
    currencyCode: row.currencyCode as string,
    isActive: row.isActive as boolean,
    version: row.version as number,
    createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date,
    deletedAt: (row.deletedAt as Date) ?? null,
  });
}

function toPrismaPayrollGroup(group: PayrollGroup): Record<string, unknown> {
  const s = group.toState();
  return {
    id: s.id, code: s.code, name: s.name, description: s.description,
    companyId: s.companyId, branchId: s.branchId, payFrequency: s.payFrequency,
    currencyCode: s.currencyCode, isActive: s.isActive, version: s.version,
    createdAt: s.createdAt, updatedAt: s.updatedAt, deletedAt: s.deletedAt,
  };
}

@Injectable()
export class PrismaPayrollGroupRepository implements PayrollGroupRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(group: PayrollGroup): Promise<void> {
    const data = toPrismaPayrollGroup(group);
    await (this.prisma as any).prlPayrollGroup.upsert({
      where: { id: data.id as string },
      create: data,
      update: data,
    });
  }

  async findById(id: PayrollGroupId): Promise<PayrollGroup | null> {
    const row = await (this.prisma as any).prlPayrollGroup.findUnique({ where: { id: id.value } });
    return row ? fromPrismaPayrollGroup(row) : null;
  }

  async findByCode(code: string): Promise<PayrollGroup | null> {
    const row = await (this.prisma as any).prlPayrollGroup.findUnique({ where: { code } });
    return row ? fromPrismaPayrollGroup(row) : null;
  }

  async findAll(companyId?: string): Promise<PayrollGroup[]> {
    const where: Record<string, unknown> = { deletedAt: null };
    if (companyId) where.companyId = companyId;
    const rows = await (this.prisma as any).prlPayrollGroup.findMany({ where, orderBy: { code: "asc" } });
    return rows.map(fromPrismaPayrollGroup);
  }

  async findActive(): Promise<PayrollGroup[]> {
    const rows = await (this.prisma as any).prlPayrollGroup.findMany({ where: { isActive: true, deletedAt: null } });
    return rows.map(fromPrismaPayrollGroup);
  }

  async delete(id: PayrollGroupId): Promise<void> {
    await (this.prisma as any).prlPayrollGroup.update({ where: { id: id.value }, data: { deletedAt: new Date() } });
  }
}

// ─── SalaryComponent ────────────────────────────────────────────────────────

function fromPrismaSalaryComponent(row: Record<string, unknown>): SalaryComponent {
  return SalaryComponent.load({
    id: row.id as string, code: row.code as string, name: row.name as string,
    nameEn: (row.nameEn as string) ?? null, elementType: row.elementType as string,
    category: row.category as string, isActive: row.isActive as boolean,
    isTaxable: row.isTaxable as boolean, isInsurable: row.isInsurable as boolean,
    isPITable: row.isPITable as boolean, priority: row.priority as number,
    formula: (row.formula as string) ?? null, defaultValue: toBigInt(row.defaultValue as bigint | null),
    currencyCode: row.currencyCode as string, description: (row.description as string) ?? null,
    version: row.version as number, createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date, deletedAt: (row.deletedAt as Date) ?? null,
  });
}

function toPrismaSalaryComponent(sc: SalaryComponent): Record<string, unknown> {
  const s = sc.toState();
  return { ...s, defaultValue: s.defaultValue ?? undefined };
}

@Injectable()
export class PrismaSalaryComponentRepository implements SalaryComponentRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(component: SalaryComponent): Promise<void> {
    const data = toPrismaSalaryComponent(component);
    await (this.prisma as any).prlSalaryComponent.upsert({
      where: { id: data.id as string }, create: data, update: data,
    });
  }

  async findById(id: SalaryComponentId): Promise<SalaryComponent | null> {
    const row = await (this.prisma as any).prlSalaryComponent.findUnique({ where: { id: id.value } });
    return row ? fromPrismaSalaryComponent(row) : null;
  }

  async findByCode(code: string): Promise<SalaryComponent | null> {
    const row = await (this.prisma as any).prlSalaryComponent.findUnique({ where: { code } });
    return row ? fromPrismaSalaryComponent(row) : null;
  }

  async findAll(): Promise<SalaryComponent[]> {
    const rows = await (this.prisma as any).prlSalaryComponent.findMany({ where: { deletedAt: null }, orderBy: { priority: "asc" } });
    return rows.map(fromPrismaSalaryComponent);
  }

  async findByCategory(category: string): Promise<SalaryComponent[]> {
    const rows = await (this.prisma as any).prlSalaryComponent.findMany({ where: { category, deletedAt: null }, orderBy: { priority: "asc" } });
    return rows.map(fromPrismaSalaryComponent);
  }

  async findActive(): Promise<SalaryComponent[]> {
    const rows = await (this.prisma as any).prlSalaryComponent.findMany({ where: { isActive: true, deletedAt: null }, orderBy: { priority: "asc" } });
    return rows.map(fromPrismaSalaryComponent);
  }

  async delete(id: SalaryComponentId): Promise<void> {
    await (this.prisma as any).prlSalaryComponent.update({ where: { id: id.value }, data: { deletedAt: new Date() } });
  }
}

// ─── EmployeePayroll ────────────────────────────────────────────────────────

function fromPrismaEmployeePayroll(row: Record<string, unknown>): EmployeePayroll {
  return EmployeePayroll.load({
    id: row.id as string, employeeCode: row.employeeCode as string,
    employeeName: row.employeeName as string, fullName: (row.fullName as string) ?? null,
    gender: (row.gender as string) ?? null, dateOfBirth: (row.dateOfBirth as Date) ?? null,
    identityNumber: (row.identityNumber as string) ?? null, taxCode: (row.taxCode as string) ?? null,
    socialInsuranceNo: (row.socialInsuranceNo as string) ?? null,
    healthInsuranceNo: (row.healthInsuranceNo as string) ?? null,
    phone: (row.phone as string) ?? null, email: (row.email as string) ?? null,
    address: (row.address as string) ?? null, companyId: row.companyId as string,
    branchId: (row.branchId as string) ?? null, departmentId: (row.departmentId as string) ?? null,
    divisionId: (row.divisionId as string) ?? null, sectionId: (row.sectionId as string) ?? null,
    positionId: (row.positionId as string) ?? null, jobGradeId: (row.jobGradeId as string) ?? null,
    costCenterId: (row.costCenterId as string) ?? null, groupId: row.groupId as string,
    payFrequency: (row.payFrequency as string) ?? null, currencyCode: row.currencyCode as string,
    paymentMethod: row.paymentMethod as string, employmentType: row.employmentType as string,
    hireDate: row.hireDate as Date, contractEndDate: (row.contractEndDate as Date) ?? null,
    terminationDate: (row.terminationDate as Date) ?? null,
    isActive: row.isActive as boolean, isPITRegistered: row.isPITRegistered as boolean,
    isSIEnrolled: row.isSIEnrolled as boolean, isHIEnrolled: row.isHIEnrolled as boolean,
    isUIEnrolled: row.isUIEnrolled as boolean, dependentCount: row.dependentCount as number,
    approvedById: (row.approvedById as string) ?? null, approvedAt: (row.approvedAt as Date) ?? null,
    version: row.version as number, createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date, deletedAt: (row.deletedAt as Date) ?? null,
  });
}

function toPrismaEmployeePayroll(emp: EmployeePayroll): Record<string, unknown> {
  return { ...emp.toState() };
}

@Injectable()
export class PrismaEmployeePayrollRepository implements EmployeePayrollRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(employee: EmployeePayroll): Promise<void> {
    const data = toPrismaEmployeePayroll(employee);
    await (this.prisma as any).prlEmployeePayroll.upsert({
      where: { id: data.id as string }, create: data, update: data,
    });
  }

  async findById(id: EmployeePayrollId): Promise<EmployeePayroll | null> {
    const row = await (this.prisma as any).prlEmployeePayroll.findUnique({ where: { id: id.value } });
    return row ? fromPrismaEmployeePayroll(row) : null;
  }

  async findByCode(code: string): Promise<EmployeePayroll | null> {
    const row = await (this.prisma as any).prlEmployeePayroll.findUnique({ where: { employeeCode: code } });
    return row ? fromPrismaEmployeePayroll(row) : null;
  }

  async findAll(companyId?: string): Promise<EmployeePayroll[]> {
    const where: Record<string, unknown> = { deletedAt: null };
    if (companyId) where.companyId = companyId;
    const rows = await (this.prisma as any).prlEmployeePayroll.findMany({ where, orderBy: { employeeCode: "asc" } });
    return rows.map(fromPrismaEmployeePayroll);
  }

  async findByGroup(groupId: string): Promise<EmployeePayroll[]> {
    const rows = await (this.prisma as any).prlEmployeePayroll.findMany({
      where: { groupId, deletedAt: null }, orderBy: { employeeCode: "asc" },
    });
    return rows.map(fromPrismaEmployeePayroll);
  }

  async findActiveByGroup(groupId: string): Promise<EmployeePayroll[]> {
    const rows = await (this.prisma as any).prlEmployeePayroll.findMany({
      where: { groupId, isActive: true, deletedAt: null }, orderBy: { employeeCode: "asc" },
    });
    return rows.map(fromPrismaEmployeePayroll);
  }

  async findByDepartment(departmentId: string): Promise<EmployeePayroll[]> {
    const rows = await (this.prisma as any).prlEmployeePayroll.findMany({
      where: { departmentId, deletedAt: null }, orderBy: { employeeCode: "asc" },
    });
    return rows.map(fromPrismaEmployeePayroll);
  }

  async findActive(): Promise<EmployeePayroll[]> {
    const rows = await (this.prisma as any).prlEmployeePayroll.findMany({
      where: { isActive: true, deletedAt: null }, orderBy: { employeeCode: "asc" },
    });
    return rows.map(fromPrismaEmployeePayroll);
  }

  async delete(id: EmployeePayrollId): Promise<void> {
    await (this.prisma as any).prlEmployeePayroll.update({ where: { id: id.value }, data: { deletedAt: new Date() } });
  }
}

// ─── PayrollRun ─────────────────────────────────────────────────────────────

function fromPrismaPayrollRun(row: Record<string, unknown> & { payrollLines?: Record<string, unknown>[] }): PayrollRun {
  const lines = (row.payrollLines as Record<string, unknown>[] | undefined) ?? [];
  return PayrollRun.load({
    id: row.id as string, runNumber: row.runNumber as string, groupId: row.groupId as string,
    periodId: row.periodId as string, calendarId: row.calendarId as string,
    name: row.name as string, status: row.status as string, companyId: row.companyId as string,
    branchId: (row.branchId as string) ?? null, currencyCode: row.currencyCode as string,
    exchangeRate: (row.exchangeRate as number) ?? 1,
    totalEarnings: toBigInt(row.totalEarnings as bigint), totalDeductions: toBigInt(row.totalDeductions as bigint),
    totalEmployerCost: toBigInt(row.totalEmployerCost as bigint), totalNetPay: toBigInt(row.totalNetPay as bigint),
    totalPIT: toBigInt(row.totalPIT as bigint), totalInsurance: toBigInt(row.totalInsurance as bigint),
    employeeCount: row.employeeCount as number, calculationDate: (row.calculationDate as Date) ?? null,
    approvedDate: (row.approvedDate as Date) ?? null, approvedById: (row.approvedById as string) ?? null,
    postedDate: (row.postedDate as Date) ?? null, postedById: (row.postedById as string) ?? null,
    paidDate: (row.paidDate as Date) ?? null, paidById: (row.paidById as string) ?? null,
    reversedDate: (row.reversedDate as Date) ?? null, reversedById: (row.reversedById as string) ?? null,
    reverseOfId: (row.reverseOfId as string) ?? null, glBatchId: (row.glBatchId as string) ?? null,
    postedToGL: row.postedToGL as boolean, notes: (row.notes as string) ?? null,
    version: row.version as number, createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date, deletedAt: (row.deletedAt as Date) ?? null,
    lines: lines.map(l => ({
      id: l.id as string, runId: l.runId as string, employeeId: l.employeeId as string,
      lineNumber: l.lineNumber as number, employeeCode: l.employeeCode as string,
      employeeName: l.employeeName as string, departmentId: (l.departmentId as string) ?? null,
      costCenterId: (l.costCenterId as string) ?? null, branchId: (l.branchId as string) ?? null,
      taxCode: (l.taxCode as string) ?? null, socialInsuranceNo: (l.socialInsuranceNo as string) ?? null,
      bankAccountId: (l.bankAccountId as string) ?? null,
      totalEarnings: toBigInt(l.totalEarnings as bigint), totalDeductions: toBigInt(l.totalDeductions as bigint),
      grossPay: toBigInt(l.grossPay as bigint), totalInsurance: toBigInt(l.totalInsurance as bigint),
      totalPIT: toBigInt(l.totalPIT as bigint), netPay: toBigInt(l.netPay as bigint),
      employerCost: toBigInt(l.employerCost as bigint), workingDays: (l.workingDays as number) ?? 0,
      overtimeHours: (l.overtimeHours as number) ?? 0, leaveDays: (l.leaveDays as number) ?? 0,
      absenceDays: (l.absenceDays as number) ?? 0, isCalculated: l.isCalculated as boolean,
      isExcluded: l.isExcluded as boolean, excludeReason: (l.excludeReason as string) ?? null,
      notes: (l.notes as string) ?? null, version: l.version as number,
      createdAt: l.createdAt as Date, updatedAt: l.updatedAt as Date, deletedAt: (l.deletedAt as Date) ?? null,
      elements: ((l.prlPayrollElements as Record<string, unknown>[]) ?? []).map((el: Record<string, unknown>) => ({
        id: el.id as string, lineId: el.lineId as string, componentId: el.componentId as string,
        elementName: el.elementName as string, elementType: el.elementType as string,
        category: el.category as string, amount: toBigInt(el.amount as bigint),
        baseAmount: toBigInt(el.baseAmount as bigint), quantity: (el.quantity as number) ?? null,
        rate: (el.rate as number) ?? null, isTaxable: el.isTaxable as boolean,
        isInsurable: el.isInsurable as boolean, isPITable: el.isPITable as boolean,
        notes: (el.notes as string) ?? null, version: el.version as number,
        createdAt: el.createdAt as Date, updatedAt: el.updatedAt as Date, deletedAt: (el.deletedAt as Date) ?? null,
      })),
    })),
  });
}

@Injectable()
export class PrismaPayrollRunRepository implements PayrollRunRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(run: PayrollRun): Promise<void> {
    const s = run.toState();
    const runData = {
      id: s.id, runNumber: s.runNumber, groupId: s.groupId, periodId: s.periodId,
      calendarId: s.calendarId, name: s.name, status: s.status, companyId: s.companyId,
      branchId: s.branchId, currencyCode: s.currencyCode, exchangeRate: s.exchangeRate,
      totalEarnings: s.totalEarnings, totalDeductions: s.totalDeductions,
      totalEmployerCost: s.totalEmployerCost, totalNetPay: s.totalNetPay,
      totalPIT: s.totalPIT, totalInsurance: s.totalInsurance,
      employeeCount: s.employeeCount, calculationDate: s.calculationDate,
      approvedDate: s.approvedDate, approvedById: s.approvedById,
      postedDate: s.postedDate, postedById: s.postedById,
      paidDate: s.paidDate, paidById: s.paidById,
      reversedDate: s.reversedDate, reversedById: s.reversedById,
      reverseOfId: s.reverseOfId, glBatchId: s.glBatchId, postedToGL: s.postedToGL,
      notes: s.notes, version: s.version, createdAt: s.createdAt, updatedAt: s.updatedAt, deletedAt: s.deletedAt,
    };
    await (this.prisma as any).prlPayrollRun.upsert({
      where: { id: runData.id }, create: runData, update: runData,
    });

    if (s.lines.length > 0) {
      await (this.prisma as any).prlPayrollLine.deleteMany({ where: { runId: s.id } });
      for (const line of s.lines) {
        const lineData = {
          id: line.id, runId: line.runId, employeeId: line.employeeId,
          lineNumber: line.lineNumber, employeeCode: line.employeeCode,
          employeeName: line.employeeName, departmentId: line.departmentId,
          costCenterId: line.costCenterId, branchId: line.branchId,
          taxCode: line.taxCode, socialInsuranceNo: line.socialInsuranceNo,
          bankAccountId: line.bankAccountId, totalEarnings: line.totalEarnings,
          totalDeductions: line.totalDeductions, grossPay: line.grossPay,
          totalInsurance: line.totalInsurance, totalPIT: line.totalPIT,
          netPay: line.netPay, employerCost: line.employerCost,
          workingDays: line.workingDays, overtimeHours: line.overtimeHours,
          leaveDays: line.leaveDays, absenceDays: line.absenceDays,
          isCalculated: line.isCalculated, isExcluded: line.isExcluded,
          excludeReason: line.excludeReason, version: 1,
          createdAt: new Date(), updatedAt: new Date(), deletedAt: null,
        };
        await (this.prisma as any).prlPayrollLine.create({ data: lineData });

        if (line.elements.length > 0) {
          await (this.prisma as any).prlPayrollElement.deleteMany({ where: { lineId: line.id } });
          for (const el of line.elements) {
            await (this.prisma as any).prlPayrollElement.create({
              data: {
                id: el.id, lineId: line.id, componentId: el.componentId,
                elementName: el.elementName, elementType: el.elementType,
                category: el.category, amount: el.amount, baseAmount: 0n,
                isTaxable: el.isTaxable, isInsurable: el.isInsurable,
                isPITable: el.isPITable, version: 1, createdAt: new Date(), updatedAt: new Date(),
              },
            });
          }
        }
      }
    }
  }

  async findById(id: PayrollRunId): Promise<PayrollRun | null> {
    const row = await (this.prisma as any).prlPayrollRun.findUnique({
      where: { id: id.value },
      include: {
        payrollLines: {
          include: { prlPayrollElements: true },
          orderBy: { lineNumber: "asc" },
        },
      },
    });
    return row ? fromPrismaPayrollRun(row) : null;
  }

  async findByRunNumber(runNumber: string): Promise<PayrollRun | null> {
    const row = await (this.prisma as any).prlPayrollRun.findUnique({
      where: { runNumber },
      include: {
        payrollLines: {
          include: { prlPayrollElements: true },
          orderBy: { lineNumber: "asc" },
        },
      },
    });
    return row ? fromPrismaPayrollRun(row) : null;
  }

  async findByGroup(groupId: string): Promise<PayrollRun[]> {
    const rows = await (this.prisma as any).prlPayrollRun.findMany({
      where: { groupId, deletedAt: null },
      include: {
        payrollLines: {
          include: { prlPayrollElements: true },
          orderBy: { lineNumber: "asc" },
        },
      },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(fromPrismaPayrollRun);
  }

  async findByPeriod(periodId: string): Promise<PayrollRun[]> {
    const rows = await (this.prisma as any).prlPayrollRun.findMany({
      where: { periodId, deletedAt: null },
      include: {
        payrollLines: {
          include: { prlPayrollElements: true },
          orderBy: { lineNumber: "asc" },
        },
      },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(fromPrismaPayrollRun);
  }

  async findByStatus(status: string): Promise<PayrollRun[]> {
    const rows = await (this.prisma as any).prlPayrollRun.findMany({
      where: { status, deletedAt: null },
      include: {
        payrollLines: {
          include: { prlPayrollElements: true },
          orderBy: { lineNumber: "asc" },
        },
      },
      orderBy: { createdAt: "desc" },
    });
    return rows.map(fromPrismaPayrollRun);
  }

  async findLatestByGroup(groupId: string): Promise<PayrollRun | null> {
    const row = await (this.prisma as any).prlPayrollRun.findFirst({
      where: { groupId, deletedAt: null },
      orderBy: { createdAt: "desc" },
      include: {
        payrollLines: {
          include: { prlPayrollElements: true },
          orderBy: { lineNumber: "asc" },
        },
      },
    });
    return row ? fromPrismaPayrollRun(row) : null;
  }

  async delete(id: PayrollRunId): Promise<void> {
    await (this.prisma as any).prlPayrollRun.update({ where: { id: id.value }, data: { deletedAt: new Date() } });
  }
}

// ─── InsuranceRate ──────────────────────────────────────────────────────────

function fromPrismaInsuranceRate(row: Record<string, unknown>): InsuranceRate {
  return InsuranceRate.load({
    id: row.id as string, insuranceType: row.insuranceType as string, name: row.name as string,
    effectiveFrom: row.effectiveFrom as Date, effectiveTo: (row.effectiveTo as Date) ?? null,
    eeRate: Number(row.eeRate), erRate: Number(row.erRate),
    ceilingAmount: toBigInt(row.ceilingAmount as bigint | null),
    ceilingType: (row.ceilingType as string) ?? null, currencyCode: row.currencyCode as string,
    isActive: row.isActive as boolean, regulationRef: (row.regulationRef as string) ?? null,
    version: row.version as number, createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date, deletedAt: (row.deletedAt as Date) ?? null,
  });
}

function toPrismaInsuranceRate(ir: InsuranceRate): Record<string, unknown> {
  const s = ir.toState();
  return { ...s, eeRate: s.eeRate, erRate: s.erRate, ceilingAmount: s.ceilingAmount ?? undefined };
}

@Injectable()
export class PrismaInsuranceRateRepository implements InsuranceRateRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(rate: InsuranceRate): Promise<void> {
    const data = toPrismaInsuranceRate(rate);
    await (this.prisma as any).prlInsuranceRate.upsert({
      where: { id: data.id as string }, create: data, update: data,
    });
  }

  async findById(id: InsuranceRateId): Promise<InsuranceRate | null> {
    const row = await (this.prisma as any).prlInsuranceRate.findUnique({ where: { id: id.value } });
    return row ? fromPrismaInsuranceRate(row) : null;
  }

  async findByType(insuranceType: string): Promise<InsuranceRate[]> {
    const rows = await (this.prisma as any).prlInsuranceRate.findMany({
      where: { insuranceType, deletedAt: null }, orderBy: { effectiveFrom: "desc" },
    });
    return rows.map(fromPrismaInsuranceRate);
  }

  async findActive(): Promise<InsuranceRate[]> {
    const rows = await (this.prisma as any).prlInsuranceRate.findMany({
      where: { isActive: true, deletedAt: null }, orderBy: { effectiveFrom: "desc" },
    });
    return rows.map(fromPrismaInsuranceRate);
  }

  async findEffective(date: Date): Promise<InsuranceRate[]> {
    const rows = await (this.prisma as any).prlInsuranceRate.findMany({
      where: {
        isActive: true, deletedAt: null,
        effectiveFrom: { lte: date },
        OR: [{ effectiveTo: null }, { effectiveTo: { gte: date } }],
      },
    });
    return rows.map(fromPrismaInsuranceRate);
  }

  async delete(id: InsuranceRateId): Promise<void> {
    await (this.prisma as any).prlInsuranceRate.update({ where: { id: id.value }, data: { deletedAt: new Date() } });
  }
}

// ─── TaxBracket ─────────────────────────────────────────────────────────────

function fromPrismaTaxBracket(row: Record<string, unknown>): TaxBracket {
  return TaxBracket.load({
    id: row.id as string, name: row.name as string,
    effectiveFrom: row.effectiveFrom as Date, effectiveTo: (row.effectiveTo as Date) ?? null,
    bracketOrder: row.bracketOrder as number, fromAmount: toBigInt(row.fromAmount as bigint),
    toAmount: toBigInt(row.toAmount as bigint | null) !== 0n ? toBigInt(row.toAmount as bigint | null) : null,
    rate: Number(row.rate), deductAmount: toBigInt(row.deductAmount as bigint),
    currencyCode: row.currencyCode as string, isActive: row.isActive as boolean,
    regulationRef: (row.regulationRef as string) ?? null, version: row.version as number,
    createdAt: row.createdAt as Date, updatedAt: row.updatedAt as Date, deletedAt: (row.deletedAt as Date) ?? null,
  });
}

function toPrismaTaxBracket(tb: TaxBracket): Record<string, unknown> {
  const s = tb.toState();
  return { ...s, rate: s.rate, toAmount: s.toAmount ?? undefined, deductAmount: s.deductAmount };
}

@Injectable()
export class PrismaTaxBracketRepository implements TaxBracketRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(bracket: TaxBracket): Promise<void> {
    const data = toPrismaTaxBracket(bracket);
    await (this.prisma as any).prlTaxBracket.upsert({
      where: { id: data.id as string }, create: data, update: data,
    });
  }

  async findById(id: TaxBracketId): Promise<TaxBracket | null> {
    const row = await (this.prisma as any).prlTaxBracket.findUnique({ where: { id: id.value } });
    return row ? fromPrismaTaxBracket(row) : null;
  }

  async findActive(): Promise<TaxBracket[]> {
    const rows = await (this.prisma as any).prlTaxBracket.findMany({
      where: { isActive: true, deletedAt: null }, orderBy: { bracketOrder: "asc" },
    });
    return rows.map(fromPrismaTaxBracket);
  }

  async findEffective(date: Date): Promise<TaxBracket[]> {
    const rows = await (this.prisma as any).prlTaxBracket.findMany({
      where: {
        isActive: true, deletedAt: null,
        effectiveFrom: { lte: date },
        OR: [{ effectiveTo: null }, { effectiveTo: { gte: date } }],
      },
      orderBy: { bracketOrder: "asc" },
    });
    return rows.map(fromPrismaTaxBracket);
  }

  async delete(id: TaxBracketId): Promise<void> {
    await (this.prisma as any).prlTaxBracket.update({ where: { id: id.value }, data: { deletedAt: new Date() } });
  }
}

// ─── PayrollPeriod ─────────────────────────────────────────────────────────

function fromPrismaPayrollPeriod(row: Record<string, unknown>): PayrollPeriod {
  return PayrollPeriod.load({
    id: row.id as string, calendarId: row.calendarId as string,
    periodNumber: row.periodNumber as number, name: row.name as string,
    startDate: row.startDate as Date, endDate: row.endDate as Date,
    paymentDate: (row.paymentDate as Date) ?? null, year: row.year as number,
    month: row.month as number, isClosed: row.isClosed as boolean,
    closedAt: (row.closedAt as Date) ?? null, closedById: (row.closedById as string) ?? null,
    version: row.version as number, createdAt: row.createdAt as Date,
    updatedAt: row.updatedAt as Date, deletedAt: (row.deletedAt as Date) ?? null,
  });
}

@Injectable()
export class PrismaPayrollPeriodRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(period: PayrollPeriod): Promise<void> {
    const s = period.toState();
    await (this.prisma as any).prlPayrollPeriod.upsert({
      where: { id: s.id }, create: s, update: s,
    });
  }

  async findById(id: PayrollPeriodId): Promise<PayrollPeriod | null> {
    const row = await (this.prisma as any).prlPayrollPeriod.findUnique({ where: { id: id.value } });
    return row ? fromPrismaPayrollPeriod(row) : null;
  }

  async findByCalendar(calendarId: string): Promise<PayrollPeriod[]> {
    const rows = await (this.prisma as any).prlPayrollPeriod.findMany({
      where: { calendarId, deletedAt: null }, orderBy: { periodNumber: "asc" },
    });
    return rows.map(fromPrismaPayrollPeriod);
  }

  async findByYearMonth(calendarId: string, year: number, month: number): Promise<PayrollPeriod | null> {
    const row = await (this.prisma as any).prlPayrollPeriod.findFirst({
      where: { calendarId, year, month, deletedAt: null },
    });
    return row ? fromPrismaPayrollPeriod(row) : null;
  }

  async findOpenPeriod(calendarId: string, date: Date): Promise<PayrollPeriod | null> {
    const row = await (this.prisma as any).prlPayrollPeriod.findFirst({
      where: { calendarId, isClosed: false, startDate: { lte: date }, endDate: { gte: date }, deletedAt: null },
    });
    return row ? fromPrismaPayrollPeriod(row) : null;
  }
}
