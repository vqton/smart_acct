import { Controller, Get, Post, Put, Delete, Param, Body, NotFoundException, ConflictException } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaConsolidationGroupRepository, PrismaConsolidationRunRepository } from "../../infrastructure/fr/fr-prisma-repos.js";
import { FrConsolidationGroupId, FrConsolidationRunId } from "../../domain/fr/fr-ids.js";
import { ConsolidationGroup, ConsolidationRun } from "../../domain/fr/fr-consolidation.js";
import { ConsolidationGroupMember } from "../../domain/fr/fr-value-objects.js";
import { ConsolidationEngine } from "../../application/fr/consolidation-engine.js";
import { CreateConsolidationGroupDto, AddGroupMemberDto, CreateConsolidationRunDto } from "./dto/consolidation.dto.js";

@ApiTags("FR Consolidation")
@Controller("api/fr/consolidation")
export class ConsolidationController {
  constructor(
    private readonly groupRepo: PrismaConsolidationGroupRepository,
    private readonly runRepo: PrismaConsolidationRunRepository,
    private readonly engine: ConsolidationEngine,
  ) {}

  // ── Groups ──────────────────────────────────────────────────────────────

  @Post("groups")
  @ApiOperation({ summary: "Create consolidation group" })
  async createGroup(@Body() dto: CreateConsolidationGroupDto) {
    const existing = await this.groupRepo.findByCode(dto.code);
    if (existing) throw new ConflictException(`Group code ${dto.code} already exists`);

    const group = ConsolidationGroup.create({
      code: dto.code,
      name: dto.name,
      description: dto.description,
      parentCompanyId: dto.parentCompanyId,
      currencyCode: dto.currencyCode,
      createdById: dto.createdById,
    });

    await this.groupRepo.save(group);
    return group.toState();
  }

  @Get("groups")
  @ApiOperation({ summary: "List consolidation groups" })
  async listGroups() {
    return this.groupRepo.findAll();
  }

  @Get("groups/:id")
  @ApiOperation({ summary: "Get consolidation group" })
  async getGroup(@Param("id") id: string) {
    const group = await this.groupRepo.findById(new FrConsolidationGroupId(id));
    if (!group) throw new NotFoundException("Group not found");
    return group.toState();
  }

  @Post("groups/:id/members")
  @ApiOperation({ summary: "Add member to consolidation group" })
  async addMember(@Param("id") id: string, @Body() dto: AddGroupMemberDto) {
    const group = await this.groupRepo.findById(new FrConsolidationGroupId(id));
    if (!group) throw new NotFoundException("Group not found");

    const member = new ConsolidationGroupMember(
      dto.legalEntityId,
      dto.legalEntityCode,
      dto.legalEntityName,
      dto.ownershipPercentage,
      dto.consolidationMethod,
      new Date(),
      "VND",
      0,
      true,
    );

    group.addMember(member);
    await this.groupRepo.save(group);
    return group.toState();
  }

  @Delete("groups/:id/members/:entityId")
  @ApiOperation({ summary: "Remove member from consolidation group" })
  async removeMember(@Param("id") id: string, @Param("entityId") entityId: string) {
    const group = await this.groupRepo.findById(new FrConsolidationGroupId(id));
    if (!group) throw new NotFoundException("Group not found");
    group.removeMember(entityId);
    await this.groupRepo.save(group);
    return { success: true };
  }

  @Delete("groups/:id")
  @ApiOperation({ summary: "Delete consolidation group (soft)" })
  async deleteGroup(@Param("id") id: string) {
    const group = await this.groupRepo.findById(new FrConsolidationGroupId(id));
    if (!group) throw new NotFoundException("Group not found");
    group.markDeleted();
    await this.groupRepo.save(group);
    return { success: true };
  }

  // ── Runs ─────────────────────────────────────────────────────────────────

  @Post("runs")
  @ApiOperation({ summary: "Create consolidation run" })
  async createRun(@Body() dto: CreateConsolidationRunDto) {
    return this.engine.createRun({
      groupId: dto.groupId,
      fiscalYearId: dto.fiscalYearId,
      periodId: dto.periodId,
      periodNumber: dto.periodNumber,
      periodName: dto.periodName,
      asOfDate: new Date(dto.asOfDate),
      preparedById: dto.preparedById,
    });
  }

  @Post("runs/:id/generate")
  @ApiOperation({ summary: "Generate consolidation entries" })
  async generateEntries(@Param("id") id: string) {
    await this.engine.generateEntries(id);
    const run = await this.runRepo.findById(new FrConsolidationRunId(id));
    return run?.toState();
  }

  @Get("runs")
  @ApiOperation({ summary: "List consolidation runs" })
  async listRuns() {
    return this.runRepo.findAll();
  }

  @Get("runs/:id")
  @ApiOperation({ summary: "Get consolidation run" })
  async getRun(@Param("id") id: string) {
    const run = await this.runRepo.findById(new FrConsolidationRunId(id));
    if (!run) throw new NotFoundException("Consolidation run not found");
    return run.toState();
  }

  @Post("runs/:id/verify")
  @ApiOperation({ summary: "Verify consolidation run" })
  async verifyRun(@Param("id") id: string, @Body("userId") userId: string) {
    const run = await this.runRepo.findById(new FrConsolidationRunId(id));
    if (!run) throw new NotFoundException("Consolidation run not found");
    run.verify(userId);
    await this.runRepo.save(run);
    return run.toState();
  }

  @Post("runs/:id/approve")
  @ApiOperation({ summary: "Approve consolidation run" })
  async approveRun(@Param("id") id: string, @Body("userId") userId: string) {
    const run = await this.runRepo.findById(new FrConsolidationRunId(id));
    if (!run) throw new NotFoundException("Consolidation run not found");
    run.approve(userId);
    await this.runRepo.save(run);
    return run.toState();
  }

  @Get("groups/:id/consolidated")
  @ApiOperation({ summary: "Get consolidated balances for group" })
  async getConsolidated(
    @Param("id") id: string,
    @Body("fiscalYearId") fiscalYearId: string,
    @Body("periodNumber") periodNumber: number,
  ) {
    return this.engine.getConsolidatedBalances(id, fiscalYearId, periodNumber);
  }
}
