import {
  Controller, Get, Post, Put, Delete, Param, Body, Query, HttpCode,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiQuery } from "@nestjs/swagger";
import { PayrollService } from "../../application/prl/payroll.service.js";
import {
  CreatePayrollGroupDto, UpdatePayrollGroupDto,
  CreateSalaryComponentDto,
  CreateEmployeePayrollDto, UpdateEmployeePayrollDto, TerminateEmployeeDto,
  CreatePayrollPeriodDto,
  CreatePayrollRunDto, AddEmployeesToRunDto, ApproveRunDto, PostRunDto, ReverseRunDto,
  CreateInsuranceRateDto, CreateTaxBracketDto,
} from "./dto/prl.dto.js";

@ApiTags("Payroll")
@Controller("api/payroll")
export class PayrollController {
  constructor(private readonly svc: PayrollService) {}

  // ─── Payroll Groups ──────────────────────────────────────────────────────

  @Post("groups")
  @ApiOperation({ summary: "Create payroll group" })
  async createGroup(@Body() dto: CreatePayrollGroupDto) {
    return this.svc.createGroup({
      ...dto, branchId: dto.branchId, description: dto.description,
    });
  }

  @Get("groups")
  @ApiOperation({ summary: "List payroll groups" })
  @ApiQuery({ name: "companyId", required: false })
  async listGroups(@Query("companyId") companyId?: string) {
    return this.svc.listGroups(companyId);
  }

  @Get("groups/:id")
  @ApiOperation({ summary: "Get payroll group" })
  async getGroup(@Param("id") id: string) {
    return this.svc.getGroup(id);
  }

  @Put("groups/:id")
  @ApiOperation({ summary: "Update payroll group" })
  async updateGroup(@Param("id") id: string, @Body() dto: UpdatePayrollGroupDto) {
    return this.svc.updateGroup(id, dto);
  }

  @Delete("groups/:id")
  @HttpCode(204)
  @ApiOperation({ summary: "Delete payroll group (soft)" })
  async deleteGroup(@Param("id") id: string) {
    await this.svc.deleteGroup(id);
  }

  // ─── Salary Components ───────────────────────────────────────────────────

  @Post("components")
  @ApiOperation({ summary: "Create salary component" })
  async createComponent(@Body() dto: CreateSalaryComponentDto) {
    return this.svc.createComponent(dto);
  }

  @Get("components")
  @ApiOperation({ summary: "List salary components" })
  async listComponents() {
    return this.svc.listComponents();
  }

  @Get("components/:id")
  @ApiOperation({ summary: "Get salary component" })
  async getComponent(@Param("id") id: string) {
    return this.svc.getComponent(id);
  }

  @Delete("components/:id")
  @HttpCode(204)
  @ApiOperation({ summary: "Delete salary component" })
  async deleteComponent(@Param("id") id: string) {
    await this.svc.deleteComponent(id);
  }

  // ─── Employees ───────────────────────────────────────────────────────────

  @Post("employees")
  @ApiOperation({ summary: "Create employee payroll profile" })
  async createEmployee(@Body() dto: CreateEmployeePayrollDto) {
    return this.svc.createEmployee({
      ...dto, hireDate: new Date(dto.hireDate),
    });
  }

  @Get("employees")
  @ApiOperation({ summary: "List employees" })
  @ApiQuery({ name: "companyId", required: false })
  async listEmployees(@Query("companyId") companyId?: string) {
    return this.svc.listEmployees(companyId);
  }

  @Get("employees/by-group/:groupId")
  @ApiOperation({ summary: "List employees by payroll group" })
  async listEmployeesByGroup(@Param("groupId") groupId: string) {
    return this.svc.listEmployeesByGroup(groupId);
  }

  @Get("employees/:id")
  @ApiOperation({ summary: "Get employee payroll profile" })
  async getEmployee(@Param("id") id: string) {
    return this.svc.getEmployee(id);
  }

  @Put("employees/:id")
  @ApiOperation({ summary: "Update employee payroll profile" })
  async updateEmployee(@Param("id") id: string, @Body() dto: UpdateEmployeePayrollDto) {
    return this.svc.updateEmployee(id, dto as any);
  }

  @Post("employees/:id/terminate")
  @ApiOperation({ summary: "Terminate employee" })
  async terminateEmployee(@Param("id") id: string, @Body() dto: TerminateEmployeeDto) {
    return this.svc.terminateEmployee(id, new Date(dto.terminationDate));
  }

  @Delete("employees/:id")
  @HttpCode(204)
  @ApiOperation({ summary: "Delete employee payroll profile" })
  async deleteEmployee(@Param("id") id: string) {
    await this.svc.deleteEmployee(id);
  }

  // ─── Periods ─────────────────────────────────────────────────────────────

  @Post("periods")
  @ApiOperation({ summary: "Create payroll period" })
  async createPeriod(@Body() dto: CreatePayrollPeriodDto) {
    return this.svc.createPeriod({
      ...dto, startDate: new Date(dto.startDate), endDate: new Date(dto.endDate),
      paymentDate: dto.paymentDate ? new Date(dto.paymentDate) : undefined,
    });
  }

  @Get("periods/by-calendar/:calendarId")
  @ApiOperation({ summary: "List periods by calendar" })
  async listPeriods(@Param("calendarId") calendarId: string) {
    return this.svc.listPeriods(calendarId);
  }

  @Get("periods/:id")
  @ApiOperation({ summary: "Get payroll period" })
  async getPeriod(@Param("id") id: string) {
    return this.svc.getPeriod(id);
  }

  @Post("periods/:id/close")
  @ApiOperation({ summary: "Close payroll period" })
  async closePeriod(@Param("id") id: string, @Body("closedById") closedById: string) {
    return this.svc.closePeriod(id, closedById);
  }

  // ─── Payroll Runs ────────────────────────────────────────────────────────

  @Post("runs")
  @ApiOperation({ summary: "Create payroll run" })
  async createRun(@Body() dto: CreatePayrollRunDto) {
    return this.svc.createRun(dto);
  }

  @Get("runs/:id")
  @ApiOperation({ summary: "Get payroll run" })
  async getRun(@Param("id") id: string) {
    return this.svc.getRun(id);
  }

  @Get("runs/by-group/:groupId")
  @ApiOperation({ summary: "List payroll runs by group" })
  async listRuns(@Param("groupId") groupId: string) {
    return this.svc.listRuns(groupId);
  }

  @Post("runs/:id/add-employees")
  @ApiOperation({ summary: "Add employees to payroll run" })
  async addEmployees(@Param("id") id: string, @Body() dto: AddEmployeesToRunDto) {
    return this.svc.addEmployeesToRun(id, dto.employeeIds);
  }

  @Post("runs/:id/calculate")
  @ApiOperation({ summary: "Calculate payroll run" })
  async calculateRun(@Param("id") id: string) {
    return this.svc.calculateRun(id);
  }

  @Post("runs/:id/approve")
  @ApiOperation({ summary: "Approve payroll run" })
  async approveRun(@Param("id") id: string, @Body() dto: ApproveRunDto) {
    return this.svc.approveRun(id, dto.approvedById);
  }

  @Post("runs/:id/post")
  @ApiOperation({ summary: "Post payroll run" })
  async postRun(@Param("id") id: string, @Body() dto: PostRunDto) {
    return this.svc.postRun(id, dto.postedById);
  }

  @Post("runs/:id/reverse")
  @ApiOperation({ summary: "Reverse payroll run (creates reversal run)" })
  async reverseRun(@Param("id") id: string, @Body() dto: ReverseRunDto) {
    return this.svc.reverseRun(id, dto.reversedById);
  }

  @Post("runs/:id/cancel")
  @ApiOperation({ summary: "Cancel payroll run (draft only)" })
  async cancelRun(@Param("id") id: string) {
    return this.svc.cancelRun(id);
  }

  // ─── Insurance Rates ─────────────────────────────────────────────────────

  @Post("insurance-rates")
  @ApiOperation({ summary: "Create insurance rate" })
  async createInsuranceRate(@Body() dto: CreateInsuranceRateDto) {
    return this.svc.createInsuranceRate({
      ...dto, effectiveFrom: new Date(dto.effectiveFrom),
      ceilingAmount: dto.ceilingAmount ? BigInt(dto.ceilingAmount) : undefined,
    });
  }

  @Get("insurance-rates")
  @ApiOperation({ summary: "List active insurance rates" })
  async listInsuranceRates() {
    return this.svc.listInsuranceRates();
  }

  // ─── Tax Brackets ────────────────────────────────────────────────────────

  @Post("tax-brackets")
  @ApiOperation({ summary: "Create tax bracket" })
  async createTaxBracket(@Body() dto: CreateTaxBracketDto) {
    return this.svc.createTaxBracket({
      ...dto, effectiveFrom: new Date(dto.effectiveFrom),
      fromAmount: BigInt(dto.fromAmount), deductAmount: BigInt(dto.deductAmount),
      toAmount: dto.toAmount ? BigInt(dto.toAmount) : undefined,
    });
  }

  @Get("tax-brackets")
  @ApiOperation({ summary: "List active tax brackets" })
  async listTaxBrackets() {
    return this.svc.listTaxBrackets();
  }
}
