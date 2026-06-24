import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class PayrollGroupId extends Identifier {
  static new(): PayrollGroupId { return new PayrollGroupId(IdGenerator.uuid()); }
}

export class SalaryComponentId extends Identifier {
  static new(): SalaryComponentId { return new SalaryComponentId(IdGenerator.uuid()); }
}

export class InsuranceRateId extends Identifier {
  static new(): InsuranceRateId { return new InsuranceRateId(IdGenerator.uuid()); }
}

export class TaxBracketId extends Identifier {
  static new(): TaxBracketId { return new TaxBracketId(IdGenerator.uuid()); }
}

export class PayrollCalendarId extends Identifier {
  static new(): PayrollCalendarId { return new PayrollCalendarId(IdGenerator.uuid()); }
}

export class PayrollPeriodId extends Identifier {
  static new(): PayrollPeriodId { return new PayrollPeriodId(IdGenerator.uuid()); }
}

export class EmployeePayrollId extends Identifier {
  static new(): EmployeePayrollId { return new EmployeePayrollId(IdGenerator.uuid()); }
}

export class EmployeeSalaryId extends Identifier {
  static new(): EmployeeSalaryId { return new EmployeeSalaryId(IdGenerator.uuid()); }
}

export class EmployeeDependentId extends Identifier {
  static new(): EmployeeDependentId { return new EmployeeDependentId(IdGenerator.uuid()); }
}

export class EmployeeBankAccountId extends Identifier {
  static new(): EmployeeBankAccountId { return new EmployeeBankAccountId(IdGenerator.uuid()); }
}

export class PayrollRunId extends Identifier {
  static new(): PayrollRunId { return new PayrollRunId(IdGenerator.uuid()); }
}

export class PayrollLineId extends Identifier {
  static new(): PayrollLineId { return new PayrollLineId(IdGenerator.uuid()); }
}

export class PayrollElementId extends Identifier {
  static new(): PayrollElementId { return new PayrollElementId(IdGenerator.uuid()); }
}

export class PayrollApprovalId extends Identifier {
  static new(): PayrollApprovalId { return new PayrollApprovalId(IdGenerator.uuid()); }
}

export class PayrollPaymentId extends Identifier {
  static new(): PayrollPaymentId { return new PayrollPaymentId(IdGenerator.uuid()); }
}

export class PayrollJournalId extends Identifier {
  static new(): PayrollJournalId { return new PayrollJournalId(IdGenerator.uuid()); }
}

export class AttendanceRecordId extends Identifier {
  static new(): AttendanceRecordId { return new AttendanceRecordId(IdGenerator.uuid()); }
}

export class OvertimeRecordId extends Identifier {
  static new(): OvertimeRecordId { return new OvertimeRecordId(IdGenerator.uuid()); }
}

export class LeaveRecordId extends Identifier {
  static new(): LeaveRecordId { return new LeaveRecordId(IdGenerator.uuid()); }
}
