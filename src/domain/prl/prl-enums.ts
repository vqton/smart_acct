export enum PayFrequency {
  MONTHLY = "monthly",
  WEEKLY = "weekly",
  BIWEEKLY = "biweekly",
  SEMIMONTHLY = "semimonthly",
  DAILY = "daily",
  HOURLY = "hourly",
}

export enum EmploymentType {
  INDEFINITE = "indefinite",
  FIXED_TERM = "fixed_term",
  SEASONAL = "seasonal",
  PROBATION = "probation",
  INTERNSHIP = "internship",
  PART_TIME = "part_time",
  OUTSOURCED = "outsourced",
}

export enum PaymentMethod {
  BANK_TRANSFER = "bank_transfer",
  CASH = "cash",
  CHEQUE = "cheque",
}

export enum PayrollRunStatus {
  DRAFT = "draft",
  CALCULATED = "calculated",
  APPROVED = "approved",
  POSTED = "posted",
  PAID = "paid",
  REVERSED = "reversed",
  CANCELLED = "cancelled",
}

export enum ElementCategory {
  EARNING = "earning",
  DEDUCTION = "deduction",
  EMPLOYER_CONTRIBUTION = "employer_contribution",
  EMPLOYEE_CONTRIBUTION = "employee_contribution",
  TAX = "tax",
  INSURANCE = "insurance",
  LOAN = "loan",
  ADJUSTMENT = "adjustment",
}

export enum ElementType {
  BASE_SALARY = "base_salary",
  HOURLY_WAGE = "hourly_wage",
  DAILY_WAGE = "daily_wage",
  COMMISSION = "commission",
  BONUS = "bonus",
  PERFORMANCE_BONUS = "performance_bonus",
  THIRTEENTH_MONTH = "thirteenth_month",
  ALLOWANCE_FIXED = "allowance_fixed",
  ALLOWANCE_VARIABLE = "allowance_variable",
  SHIFT_ALLOWANCE = "shift_allowance",
  MEAL_ALLOWANCE = "meal_allowance",
  TRANSPORTATION = "transportation",
  PHONE_ALLOWANCE = "phone_allowance",
  HOUSING_ALLOWANCE = "housing_allowance",
  RESPONSIBILITY_ALLOWANCE = "responsibility_allowance",
  POSITION_ALLOWANCE = "position_allowance",
  ATTENDANCE_ALLOWANCE = "attendance_allowance",
  KPI_BONUS = "kpi_bonus",
  OVERTIME = "overtime",
  NIGHT_SHIFT = "night_shift",
  WEEKEND_WORK = "weekend_work",
  HOLIDAY_WORK = "holiday_work",
  SOCIAL_INSURANCE_EE = "social_insurance_ee",
  HEALTH_INSURANCE_EE = "health_insurance_ee",
  UNEMPLOYMENT_INSURANCE_EE = "unemployment_insurance_ee",
  SOCIAL_INSURANCE_ER = "social_insurance_er",
  HEALTH_INSURANCE_ER = "health_insurance_er",
  UNEMPLOYMENT_INSURANCE_ER = "unemployment_insurance_er",
  TRADE_UNION_FEE = "trade_union_fee",
  PIT = "pit",
  SALARY_ADVANCE = "salary_advance",
  LOAN_REPAYMENT = "loan_repayment",
  GARNISHMENT = "garnishment",
  OTHER_EARNING = "other_earning",
  OTHER_DEDUCTION = "other_deduction",
}

export enum InsuranceType {
  SOCIAL_INSURANCE = "social_insurance",
  HEALTH_INSURANCE = "health_insurance",
  UNEMPLOYMENT_INSURANCE = "unemployment_insurance",
  OCCUPATIONAL_INSURANCE = "occupational_insurance",
  TRADE_UNION = "trade_union",
}

export enum LeaveType {
  ANNUAL = "annual",
  SICK = "sick",
  MATERNITY = "maternity",
  PATERNITY = "paternity",
  UNPAID = "unpaid",
  MARRIAGE = "marriage",
  FUNERAL = "funeral",
  STUDY = "study",
  COMPASSIONATE = "compassionate",
  OTHER = "other",
}

export enum OvertimeType {
  WEEKDAY = "weekday",
  WEEKDAY_NIGHT = "weekday_night",
  WEEKEND = "weekend",
  WEEKEND_NIGHT = "weekend_night",
  HOLIDAY = "holiday",
  HOLIDAY_NIGHT = "holiday_night",
}

export enum ApprovalStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected",
  RETURNED = "returned",
}

export enum Gender {
  MALE = "male",
  FEMALE = "female",
  OTHER = "other",
}
