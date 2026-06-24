import { Controller, Get, Post, Put, Patch, Delete, Param, Body, Query, BadRequestException, NotFoundException } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiQuery } from "@nestjs/swagger";
import { FaService } from "../../application/fa/fa-service.js";
import { DomainError } from "../../shared/domain-error.js";
import {
  CreateAssetGroupDto, UpdateAssetGroupDto, CreateAssetClassDto,
  CreateAssetDto, UpdateAssetDto, AcquireAssetDto, DisposeAssetDto,
  TransferAssetDto, RevalueAssetDto, ImpairAssetDto,
  CreateCipProjectDto, AddCipCostDto, CapitalizeCipDto,
  RunDepreciationDto, CreateLeaseDto, CreateMaintenanceRecordDto,
  CreateVerificationDto,
} from "./dto/fa.dto.js";
import { FaAssetStatus, FaAssetType } from "../../domain/fa/fa-enums.js";

function handleError(e: unknown): never {
  if (e instanceof DomainError) {
    if (e.kind === "NotFound") throw new NotFoundException(e.message);
    throw new BadRequestException(e.message);
  }
  throw e;
}

@ApiTags("Fixed Assets")
@Controller("api/fixed-assets")
export class FaController {
  constructor(private readonly svc: FaService) {}

  // ─── Asset Groups ──────────────────────────────────────────────────────────────

  @Post("groups")
  @ApiOperation({ summary: "Create asset group" })
  async createGroup(@Body() dto: CreateAssetGroupDto) {
    try { return await this.svc.createGroup(dto); }
    catch (e) { handleError(e); }
  }

  @Get("groups")
  @ApiOperation({ summary: "List asset groups" })
  async listGroups() {
    return this.svc.listGroups();
  }

  @Get("groups/:id")
  @ApiOperation({ summary: "Get asset group" })
  async getGroup(@Param("id") id: string) {
    try {
      const g = await this.svc.getGroup(id);
      if (!g) throw new NotFoundException("Group not found");
      return g;
    } catch (e) { handleError(e); }
  }

  @Patch("groups/:id")
  @ApiOperation({ summary: "Update asset group" })
  async updateGroup(@Param("id") id: string, @Body() dto: UpdateAssetGroupDto) {
    try { return await this.svc.updateGroup(id, dto as any); }
    catch (e) { handleError(e); }
  }

  // ─── Asset Classes ─────────────────────────────────────────────────────────────

  @Post("classes")
  @ApiOperation({ summary: "Create asset class" })
  async createClass(@Body() dto: CreateAssetClassDto) {
    try { return await this.svc.createClass(dto); }
    catch (e) { handleError(e); }
  }

  @Get("classes")
  @ApiOperation({ summary: "List asset classes" })
  @ApiQuery({ name: "groupId", required: false })
  async listClasses(@Query("groupId") groupId?: string) {
    return this.svc.listClasses(groupId);
  }

  @Get("classes/:id")
  @ApiOperation({ summary: "Get asset class" })
  async getClass(@Param("id") id: string) {
    try {
      const c = await this.svc.getClass(id);
      if (!c) throw new NotFoundException("Class not found");
      return c;
    } catch (e) { handleError(e); }
  }

  // ─── Asset Categories ──────────────────────────────────────────────────────────

  @Post("categories")
  @ApiOperation({ summary: "Create asset category" })
  async createCategory(@Body() dto: { code: string; name: string; classId?: string }) {
    try { return await this.svc.createCategory(dto); }
    catch (e) { handleError(e); }
  }

  @Get("categories")
  @ApiOperation({ summary: "List asset categories" })
  @ApiQuery({ name: "classId", required: false })
  async listCategories(@Query("classId") classId?: string) {
    return this.svc.listCategories(classId);
  }

  // ─── Assets ────────────────────────────────────────────────────────────────────

  @Post("assets")
  @ApiOperation({ summary: "Create asset" })
  async createAsset(@Body() dto: CreateAssetDto) {
    try {
      const asset = await this.svc.createAsset(dto);
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  @Get("assets")
  @ApiOperation({ summary: "List assets" })
  @ApiQuery({ name: "status", required: false, enum: FaAssetStatus })
  @ApiQuery({ name: "type", required: false, enum: FaAssetType })
  async listAssets(
    @Query("status") status?: FaAssetStatus,
    @Query("type") type?: FaAssetType,
  ) {
    const assets = await this.svc.listAssets(status, type);
    return assets.map(a => a.toState());
  }

  @Get("assets/:id")
  @ApiOperation({ summary: "Get asset" })
  async getAsset(@Param("id") id: string) {
    try {
      const asset = await this.svc.getAsset(id);
      if (!asset) throw new NotFoundException("Asset not found");
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  @Patch("assets/:id")
  @ApiOperation({ summary: "Update asset" })
  async updateAsset(@Param("id") id: string, @Body() dto: UpdateAssetDto) {
    try {
      const asset = await this.svc.updateAsset(id, dto as any);
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/acquire")
  @ApiOperation({ summary: "Acquire asset" })
  async acquireAsset(@Param("id") id: string, @Body() dto: AcquireAssetDto) {
    try {
      const asset = await this.svc.acquireAsset(id, {
        ...dto, acquisitionDate: new Date(dto.acquisitionDate),
      });
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/capitalize")
  @ApiOperation({ summary: "Capitalize asset" })
  async capitalizeAsset(@Param("id") id: string, @Body() body: { capitalizationDate: string }) {
    try {
      const asset = await this.svc.capitalizeAsset(id, new Date(body.capitalizationDate));
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/activate")
  @ApiOperation({ summary: "Put asset in use" })
  async activateAsset(@Param("id") id: string, @Body() body: { inUseDate: string }) {
    try {
      const asset = await this.svc.putAssetInUse(id, new Date(body.inUseDate));
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/suspend")
  @ApiOperation({ summary: "Suspend asset" })
  async suspendAsset(@Param("id") id: string, @Body() body: { fromDate: string; toDate?: string }) {
    try {
      const asset = await this.svc.suspendAsset(id, new Date(body.fromDate), body.toDate ? new Date(body.toDate) : undefined);
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/resume")
  @ApiOperation({ summary: "Resume asset" })
  async resumeAsset(@Param("id") id: string) {
    try {
      const asset = await this.svc.resumeAsset(id);
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/transfer")
  @ApiOperation({ summary: "Transfer asset" })
  async transferAsset(@Param("id") id: string, @Body() dto: TransferAssetDto) {
    try {
      const transfer = await this.svc.transferAsset(id, {
        ...dto, transferDate: new Date(dto.transferDate),
      });
      return transfer.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/dispose")
  @ApiOperation({ summary: "Dispose asset" })
  async disposeAsset(@Param("id") id: string, @Body() dto: DisposeAssetDto) {
    try {
      const disposal = await this.svc.disposeAsset(id, {
        ...dto, disposalDate: new Date(dto.disposalDate),
      });
      return disposal.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/write-off")
  @ApiOperation({ summary: "Write off asset" })
  async writeOffAsset(@Param("id") id: string, @Body() body: { reason: string }) {
    try {
      const asset = await this.svc.writeOffAsset(id, body.reason);
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/revalue")
  @ApiOperation({ summary: "Revalue asset" })
  async revalueAsset(@Param("id") id: string, @Body() dto: RevalueAssetDto) {
    try {
      const reval = await this.svc.revalueAsset(id, {
        ...dto, revaluationDate: new Date(dto.revaluationDate),
      });
      return reval.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/impair")
  @ApiOperation({ summary: "Record impairment" })
  async impairAsset(@Param("id") id: string, @Body() dto: ImpairAssetDto) {
    try {
      const impair = await this.svc.impairAsset(id, {
        ...dto, impairmentDate: new Date(dto.impairmentDate),
      });
      return impair.toState();
    } catch (e) { handleError(e); }
  }

  @Post("assets/:id/reopen")
  @ApiOperation({ summary: "Reopen asset" })
  async reopenAsset(@Param("id") id: string) {
    try {
      const asset = await this.svc.getAsset(id);
      if (!asset) throw new NotFoundException("Asset not found");
      asset.reopen();
      await this.svc["assetRepo"].save(asset);
      return asset.toState();
    } catch (e) { handleError(e); }
  }

  // ─── Depreciation ──────────────────────────────────────────────────────────────

  @Post("depreciation/run")
  @ApiOperation({ summary: "Run depreciation" })
  async runDepreciation(@Body() dto: RunDepreciationDto) {
    try {
      return await this.svc.runDepreciation(dto);
    } catch (e) { handleError(e); }
  }

  @Get("depreciation/runs")
  @ApiOperation({ summary: "List depreciation runs" })
  @ApiQuery({ name: "periodId", required: false })
  async listDepreciationRuns(@Query("periodId") periodId?: string) {
    return this.svc.listDepreciationRuns(periodId);
  }

  @Get("depreciation/runs/:id")
  @ApiOperation({ summary: "Get depreciation run" })
  async getDepreciationRun(@Param("id") id: string) {
    try {
      const run = await this.svc.getDepreciationRun(id);
      if (!run) throw new NotFoundException("Depreciation run not found");
      return run;
    } catch (e) { handleError(e); }
  }

  // ─── CIP ───────────────────────────────────────────────────────────────────────

  @Post("cip/projects")
  @ApiOperation({ summary: "Create CIP project" })
  async createCipProject(@Body() dto: CreateCipProjectDto) {
    try {
      const project = await this.svc.createCipProject({
        ...dto, startDate: new Date(dto.startDate),
      });
      return project.toState();
    } catch (e) { handleError(e); }
  }

  @Get("cip/projects")
  @ApiOperation({ summary: "List CIP projects" })
  @ApiQuery({ name: "status", required: false })
  async listCipProjects(@Query("status") status?: string) {
    return this.svc.listCipProjects(status);
  }

  @Get("cip/projects/:id")
  @ApiOperation({ summary: "Get CIP project" })
  async getCipProject(@Param("id") id: string) {
    try {
      const project = await this.svc.getCipProject(id);
      if (!project) throw new NotFoundException("CIP project not found");
      return project.toState();
    } catch (e) { handleError(e); }
  }

  @Post("cip/projects/:id/costs")
  @ApiOperation({ summary: "Add CIP cost" })
  async addCipCost(@Param("id") id: string, @Body() dto: AddCipCostDto) {
    try {
      await this.svc.addCipCost(id, { ...dto, costDate: new Date(dto.costDate) });
      return { success: true };
    } catch (e) { handleError(e); }
  }

  @Post("cip/projects/:id/capitalize")
  @ApiOperation({ summary: "Capitalize CIP to asset" })
  async capitalizeCip(@Param("id") id: string, @Body() dto: CapitalizeCipDto) {
    try {
      await this.svc.capitalizeCipProject(id, dto.assetId, dto.amount);
      return { success: true };
    } catch (e) { handleError(e); }
  }

  @Post("cip/projects/:id/complete")
  @ApiOperation({ summary: "Complete CIP project" })
  async completeCip(@Param("id") id: string, @Body() body: { endDate: string }) {
    try {
      await this.svc.completeCipProject(id, new Date(body.endDate));
      return { success: true };
    } catch (e) { handleError(e); }
  }

  // ─── Leases ────────────────────────────────────────────────────────────────────

  @Post("leases")
  @ApiOperation({ summary: "Create lease" })
  async createLease(@Body() dto: CreateLeaseDto) {
    try {
      const lease = await this.svc.createLease({
        ...dto, startDate: new Date(dto.startDate), endDate: new Date(dto.endDate),
      });
      return lease.toState();
    } catch (e) { handleError(e); }
  }

  @Get("leases")
  @ApiOperation({ summary: "List leases" })
  async listLeases() {
    return this.svc.listLeases();
  }

  @Get("leases/:id")
  @ApiOperation({ summary: "Get lease" })
  async getLease(@Param("id") id: string) {
    try {
      const lease = await this.svc.getLease(id);
      if (!lease) throw new NotFoundException("Lease not found");
      return lease.toState();
    } catch (e) { handleError(e); }
  }

  // ─── Maintenance ───────────────────────────────────────────────────────────────

  @Post("maintenance")
  @ApiOperation({ summary: "Create maintenance record" })
  async createMaintenance(@Body() dto: CreateMaintenanceRecordDto) {
    try {
      const record = await this.svc.createMaintenanceRecord({
        ...dto, maintenanceDate: new Date(dto.maintenanceDate),
      });
      return record.toState();
    } catch (e) { handleError(e); }
  }

  @Get("maintenance")
  @ApiOperation({ summary: "List maintenance records" })
  @ApiQuery({ name: "assetId", required: false })
  async listMaintenance(@Query("assetId") assetId?: string) {
    return this.svc.listMaintenanceRecords(assetId);
  }

  @Get("maintenance/:id")
  @ApiOperation({ summary: "Get maintenance record" })
  async getMaintenance(@Param("id") id: string) {
    try {
      const record = await this.svc.getMaintenanceRecord(id);
      if (!record) throw new NotFoundException("Maintenance record not found");
      return record;
    } catch (e) { handleError(e); }
  }

  // ─── Physical Verification ─────────────────────────────────────────────────────

  @Post("verifications")
  @ApiOperation({ summary: "Create physical verification" })
  async createVerification(@Body() dto: CreateVerificationDto) {
    try {
      const verification = await this.svc.createVerification({
        ...dto, verificationDate: new Date(dto.verificationDate),
      });
      return verification;
    } catch (e) { handleError(e); }
  }

  @Get("verifications")
  @ApiOperation({ summary: "List verifications" })
  @ApiQuery({ name: "status", required: false })
  async listVerifications(@Query("status") status?: string) {
    return this.svc.listVerifications(status);
  }

  @Get("verifications/:id")
  @ApiOperation({ summary: "Get verification" })
  async getVerification(@Param("id") id: string) {
    try {
      const v = await this.svc.getVerification(id);
      if (!v) throw new NotFoundException("Verification not found");
      return v;
    } catch (e) { handleError(e); }
  }

  @Post("verifications/:id/complete")
  @ApiOperation({ summary: "Complete verification" })
  async completeVerification(@Param("id") id: string) {
    try {
      return await this.svc.completeVerification(id);
    } catch (e) { handleError(e); }
  }

  @Post("verifications/:id/approve")
  @ApiOperation({ summary: "Approve verification" })
  async approveVerification(@Param("id") id: string, @Body() body: { userId: string }) {
    try {
      return await this.svc.approveVerification(id, body.userId);
    } catch (e) { handleError(e); }
  }
}
