import { Module } from "@nestjs/common";
import { PayrollController } from "./payroll.controller.js";
import { PayrollService } from "../../application/prl/payroll.service.js";
import {
  PrismaPayrollGroupRepository, PrismaSalaryComponentRepository,
  PrismaEmployeePayrollRepository, PrismaPayrollRunRepository,
  PrismaInsuranceRateRepository, PrismaTaxBracketRepository,
  PrismaPayrollPeriodRepository,
} from "../../infrastructure/prl/index.js";

@Module({
  controllers: [PayrollController],
  providers: [
    PayrollService,
    PrismaPayrollGroupRepository,
    PrismaSalaryComponentRepository,
    PrismaEmployeePayrollRepository,
    PrismaPayrollRunRepository,
    PrismaInsuranceRateRepository,
    PrismaTaxBracketRepository,
    PrismaPayrollPeriodRepository,
  ],
  exports: [
    PayrollService,
    PrismaPayrollGroupRepository,
    PrismaEmployeePayrollRepository,
    PrismaPayrollRunRepository,
  ],
})
export class PrlModule {}
