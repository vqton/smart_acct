import { Controller, Post, Get, Body, Query, Header, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiQuery } from "@nestjs/swagger";
import { CoaBulkService, ImportResult } from "../../application/coa/coa-bulk-service.js";

@ApiTags("COA Bulk Import/Export")
@Controller("api/coa/bulk")
export class CoaBulkController {
  constructor(private readonly bulkService: CoaBulkService) {}

  @Post("import/csv")
  @ApiOperation({ summary: "Import COA from CSV" })
  @Header("content-type", "application/json")
  async importCsv(@Body("content") content: string): Promise<ImportResult> {
    if (!content) throw new BadRequestException("CSV content required");
    return this.bulkService.importCsv(content);
  }

  @Post("import/json")
  @ApiOperation({ summary: "Import COA from JSON array" })
  async importJson(@Body("content") content: string): Promise<ImportResult> {
    if (!content) throw new BadRequestException("JSON content required");
    return this.bulkService.importJson(content);
  }

  @Get("export/csv")
  @ApiOperation({ summary: "Export COA as CSV" })
  @ApiQuery({ name: "entity", required: false, description: "class|type|mapping|extension" })
  @Header("content-type", "text/csv")
  @Header("content-disposition", "attachment; filename=coa-export.csv")
  async exportCsv(@Query("entity") entity?: string) {
    return this.bulkService.exportCsv(entity);
  }

  @Get("export/json")
  @ApiOperation({ summary: "Export COA as JSON" })
  @ApiQuery({ name: "entity", required: false, description: "class|type|mapping|extension" })
  @Header("content-type", "application/json")
  @Header("content-disposition", "attachment; filename=coa-export.json")
  async exportJson(@Query("entity") entity?: string) {
    return this.bulkService.exportJson(entity);
  }
}
