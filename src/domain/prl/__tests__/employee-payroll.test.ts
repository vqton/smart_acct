import { describe, it, expect } from "vitest";
import { EmployeePayroll } from "../employee-payroll.js";
import { DomainError } from "../../../shared/domain-error.js";

describe("EmployeePayroll", () => {
  const baseParams = {
    employeeCode: "EMP001",
    employeeName: "Nguyen Van A",
    companyId: "c1",
    groupId: "g1",
    hireDate: new Date("2024-01-01"),
  };

  it("creates with valid params", () => {
    const emp = EmployeePayroll.create(baseParams);
    expect(emp.employeeCode).toBe("EMP001");
    expect(emp.employeeName).toBe("Nguyen Van A");
    expect(emp.isActive).toBe(true);
    expect(emp.isSIEnrolled).toBe(true);
  });

  it("rejects missing required fields", () => {
    expect(() => EmployeePayroll.create({ ...baseParams, employeeCode: "" })).toThrow(DomainError);
    expect(() => EmployeePayroll.create({ ...baseParams, companyId: "" })).toThrow(DomainError);
  });

  it("creates with optional fields", () => {
    const emp = EmployeePayroll.create({
      ...baseParams,
      taxCode: "123456789",
      socialInsuranceNo: "SI123",
      departmentId: "dept1",
      costCenterId: "cc1",
      dependentCount: 2,
      isPITRegistered: true,
    });
    expect(emp.taxCode).toBe("123456789");
    expect(emp.dependentCount).toBe(2);
    expect(emp.isPITRegistered).toBe(true);
  });

  it("terminates employee", () => {
    const emp = EmployeePayroll.create(baseParams);
    emp.terminate(new Date("2024-12-31"));
    expect(emp.isActive).toBe(false);
    expect(() => emp.terminate(new Date("2025-01-01"))).toThrow(DomainError);
  });

  it("updates fields", () => {
    const emp = EmployeePayroll.create(baseParams);
    emp.update({ employeeName: "Nguyen Van B", taxCode: "987654321" });
    expect(emp.employeeName).toBe("Nguyen Van B");
    expect(emp.taxCode).toBe("987654321");
  });

  it("serializes to/from state", () => {
    const emp = EmployeePayroll.create(baseParams);
    const state = emp.toState();
    const restored = EmployeePayroll.load(state);
    expect(restored.employeeCode).toBe("EMP001");
    expect(restored.companyId).toBe("c1");
  });
});
