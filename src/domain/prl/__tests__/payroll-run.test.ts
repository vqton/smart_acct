import { describe, it, expect } from "vitest";
import { PayrollRun, PayrollLine, PayrollElement } from "../payroll-run.js";
import { InsuranceRate } from "../insurance-rate.js";
import { TaxBracket } from "../tax-bracket.js";
import { DomainError } from "../../../shared/domain-error.js";
import { ElementType, ElementCategory } from "../prl-enums.js";

describe("PayrollRun", () => {
  const createRun = () =>
    PayrollRun.create({
      runNumber: "PR-2026-06",
      groupId: "g1",
      periodId: "p1",
      calendarId: "cal1",
      name: "Payroll June 2026",
      companyId: "c1",
    });

  const createLine = (runId: string, empId: string, lineNo: number) => {
    const line = new PayrollLine({
      runId, employeeId: empId, lineNumber: lineNo,
      employeeCode: `EMP${lineNo}`, employeeName: `Employee ${lineNo}`,
    });
    line.addElement(new PayrollElement({
      lineId: line.id.value, componentId: "BASIC",
      elementName: "Lương cơ bản", elementType: ElementType.BASE_SALARY, category: ElementCategory.EARNING,
      amount: 20000000n, isTaxable: true, isInsurable: true, isPITable: true,
    }));
    line.addElement(new PayrollElement({
      lineId: line.id.value, componentId: "MEAL",
      elementName: "Phụ cấp ăn trưa", elementType: ElementType.MEAL_ALLOWANCE, category: ElementCategory.EARNING,
      amount: 730000n, isTaxable: false, isInsurable: false, isPITable: false,
    }));
    line.addElement(new PayrollElement({
      lineId: line.id.value, componentId: "ADVANCE",
      elementName: "Tạm ứng", elementType: ElementType.SALARY_ADVANCE, category: ElementCategory.DEDUCTION,
      amount: 5000000n, isTaxable: false, isInsurable: false, isPITable: false,
    }));
    return line;
  };

  const createInsuranceRates = (): InsuranceRate[] => [
    InsuranceRate.create({
      insuranceType: "social_insurance", name: "BHXH", effectiveFrom: new Date("2024-01-01"),
      eeRate: 0.08, erRate: 0.175, ceilingAmount: 46800000n,
    }),
    InsuranceRate.create({
      insuranceType: "health_insurance", name: "BHYT", effectiveFrom: new Date("2024-01-01"),
      eeRate: 0.015, erRate: 0.03, ceilingAmount: 46800000n,
    }),
    InsuranceRate.create({
      insuranceType: "unemployment_insurance", name: "BHTN", effectiveFrom: new Date("2024-01-01"),
      eeRate: 0.01, erRate: 0.01, ceilingAmount: 46800000n,
    }),
  ];

  const createTaxBrackets = (): TaxBracket[] => [
    TaxBracket.create({ name: "Bậc 1", effectiveFrom: new Date("2024-01-01"), bracketOrder: 1, fromAmount: 0n, toAmount: 5000000n, rate: 0.05, deductAmount: 0n }),
    TaxBracket.create({ name: "Bậc 2", effectiveFrom: new Date("2024-01-01"), bracketOrder: 2, fromAmount: 5000000n, toAmount: 10000000n, rate: 0.1, deductAmount: 250000n }),
    TaxBracket.create({ name: "Bậc 3", effectiveFrom: new Date("2024-01-01"), bracketOrder: 3, fromAmount: 10000000n, toAmount: 18000000n, rate: 0.15, deductAmount: 750000n }),
    TaxBracket.create({ name: "Bậc 4", effectiveFrom: new Date("2024-01-01"), bracketOrder: 4, fromAmount: 18000000n, toAmount: 32000000n, rate: 0.2, deductAmount: 1650000n }),
    TaxBracket.create({ name: "Bậc 5", effectiveFrom: new Date("2024-01-01"), bracketOrder: 5, fromAmount: 32000000n, toAmount: 52000000n, rate: 0.25, deductAmount: 3250000n }),
    TaxBracket.create({ name: "Bậc 6", effectiveFrom: new Date("2024-01-01"), bracketOrder: 6, fromAmount: 52000000n, toAmount: 80000000n, rate: 0.3, deductAmount: 5850000n }),
    TaxBracket.create({ name: "Bậc 7", effectiveFrom: new Date("2024-01-01"), bracketOrder: 7, fromAmount: 80000000n, toAmount: undefined, rate: 0.35, deductAmount: 9850000n }),
  ];

  it("creates with draft status", () => {
    const run = createRun();
    expect(run.status).toBe("draft");
    expect(run.runNumber).toBe("PR-2026-06");
  });

  it("rejects duplicate run number", () => {
    const run = createRun();
    expect(run.runNumber).toBe("PR-2026-06");
  });

  it("adds employees", () => {
    const run = createRun();
    run.addLine(createLine(run.id.value, "emp1", 1));
    run.addLine(createLine(run.id.value, "emp2", 2));
    expect(run.lines.length).toBe(2);
    expect(run.employeeCount).toBe(0);
  });

  it("prevents duplicate employee in same run", () => {
    const run = createRun();
    run.addLine(createLine(run.id.value, "emp1", 1));
    expect(() => run.addLine(createLine(run.id.value, "emp1", 2))).toThrow(DomainError);
  });

  it("requires draft status for adding lines", () => {
    const run = createRun();
    run.addLine(createLine(run.id.value, "emp1", 1));
    run.cancel();
    expect(() => run.addLine(createLine(run.id.value, "emp2", 2))).toThrow(DomainError);
  });

  it("calculates payroll correctly", () => {
    const run = createRun();
    run.addLine(createLine(run.id.value, "emp1", 1));
    const employeeSalaries = new Map<string, Map<string, bigint>>();
    employeeSalaries.set("emp1", new Map([["BASIC", 20000000n], ["MEAL", 730000n]]));
    const insurances = createInsuranceRates();
    const brackets = createTaxBrackets();
    const deps = new Map<string, number>([["emp1", 1]]);

    run.calculate(employeeSalaries, insurances, brackets, 11000000n, deps);
    expect(run.status).toBe("calculated");
    expect(run.lines[0].isCalculated).toBe(true);

    const line = run.lines[0];
    expect(line.totalEarnings).toBeGreaterThan(0n);
    expect(line.netPay).toBeGreaterThan(0n);
    expect(line.grossPay).toBe(line.totalEarnings);
  });

  it("requires calculated status for approval", () => {
    const run = createRun();
    expect(() => run.approve("approver1")).toThrow(DomainError);
  });

  it("approves calculated payroll", () => {
    const run = createRun();
    run.addLine(createLine(run.id.value, "emp1", 1));
    run.calculate(new Map(), createInsuranceRates(), createTaxBrackets(), 11000000n, new Map());
    run.approve("approver1");
    expect(run.status).toBe("approved");
  });

  it("posts approved payroll", () => {
    const run = createRun();
    run.addLine(createLine(run.id.value, "emp1", 1));
    run.calculate(new Map(), createInsuranceRates(), createTaxBrackets(), 11000000n, new Map());
    run.approve("approver1");
    run.post("poster1");
    expect(run.status).toBe("posted");
  });

  it("requires approved status for posting", () => {
    const run = createRun();
    expect(() => run.post("poster1")).toThrow(DomainError);
  });

  it("creates reversal run", () => {
    const run = createRun();
    run.addLine(createLine(run.id.value, "emp1", 1));
    run.calculate(new Map(), createInsuranceRates(), createTaxBrackets(), 11000000n, new Map());
    run.approve("approver1");
    run.post("poster1");

    const reversal = run.reverse("reverser1");
    expect(run.status).toBe("reversed");
    expect(reversal.status).toBe("calculated");
    expect(reversal.lines.length).toBe(1);
    expect(reversal.lines[0].netPay).toBe(-run.lines[0].netPay);
  });

  it("cancels draft only", () => {
    const run = createRun();
    run.cancel();
    expect(run.status).toBe("cancelled");
  });

  it("prevents cancel of non-draft", () => {
    const run = createRun();
    run.addLine(createLine(run.id.value, "emp1", 1));
    run.calculate(new Map(), createInsuranceRates(), createTaxBrackets(), 11000000n, new Map());
    expect(() => run.cancel()).toThrow(DomainError);
  });

  it("serializes and deserializes with lines", () => {
    const run = createRun();
    run.addLine(createLine(run.id.value, "emp1", 1));
    run.addLine(createLine(run.id.value, "emp2", 2));

    const state = run.toState();
    expect(state.lines.length).toBe(2);
    expect(state.lines[0].elements.length).toBe(3);

    const restored = PayrollRun.load(state);
    expect(restored.lines.length).toBe(2);
    expect(restored.lines[0].elements.length).toBe(3);
    expect(restored.lines[0].employeeCode).toBe("EMP1");
  });
});
