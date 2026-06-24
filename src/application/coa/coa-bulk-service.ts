import { Injectable, BadRequestException } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { CoaService } from "./coa-service.js";
import { PrismaAccountClassRepository, PrismaAccountTypeRepository, PrismaAccountMappingRepository, PrismaAccountExtensionRepository } from "../../infrastructure/coa/coa-prisma-repos.js";

interface ImportRow {
  entity: "class" | "type" | "mapping" | "extension";
  [key: string]: unknown;
}

export interface ImportResult {
  imported: number;
  skipped: number;
  errors: string[];
}

@Injectable()
export class CoaBulkService {
  constructor(
    private readonly coaService: CoaService,
    private readonly classRepo: PrismaAccountClassRepository,
    private readonly typeRepo: PrismaAccountTypeRepository,
    private readonly mappingRepo: PrismaAccountMappingRepository,
    private readonly extRepo: PrismaAccountExtensionRepository,
  ) {}

  async importCsv(csvContent: string): Promise<ImportResult> {
    const lines = csvContent.split("\n").map(l => l.trim()).filter(l => l.length > 0);
    if (lines.length < 2) throw new BadRequestException("CSV must have header + at least 1 data row");

    const header = this.parseCsvLine(lines[0]);
    const entityIdx = header.indexOf("entity");
    if (entityIdx === -1) throw new BadRequestException("CSV must have 'entity' column (class|type|mapping|extension)");

    const result: ImportResult = { imported: 0, skipped: 0, errors: [] };
    for (let i = 1; i < lines.length; i++) {
      try {
        const values = this.parseCsvLine(lines[i]);
        const row: ImportRow = { entity: values[entityIdx] as ImportRow["entity"] };
        for (let j = 0; j < header.length; j++) {
          if (j !== entityIdx && values[j] !== undefined) row[header[j]] = values[j];
        }
        await this.importRow(row);
        result.imported++;
      } catch (e) {
        result.errors.push(`Row ${i + 1}: ${(e as Error).message}`);
        result.skipped++;
      }
    }
    return result;
  }

  async importJson(jsonContent: string): Promise<ImportResult> {
    let rows: ImportRow[];
    try { rows = JSON.parse(jsonContent); }
    catch { throw new BadRequestException("Invalid JSON"); }
    if (!Array.isArray(rows)) throw new BadRequestException("JSON must be an array");

    const result: ImportResult = { imported: 0, skipped: 0, errors: [] };
    for (let i = 0; i < rows.length; i++) {
      try {
        await this.importRow(rows[i]);
        result.imported++;
      } catch (e) {
        result.errors.push(`Row ${i + 1}: ${(e as Error).message}`);
        result.skipped++;
      }
    }
    return result;
  }

  async exportCsv(entity?: string): Promise<string> {
    const lines: string[] = [];
    if (!entity || entity === "class") {
      const classes = await this.classRepo.findAll();
      if (lines.length === 0) lines.push("entity,code,name,classType,displayOrder,description");
      for (const c of classes) {
        const s = c.toState();
        lines.push(`class,${this.escCsv(s.code)},${this.escCsv(s.name)},${s.classType},${s.displayOrder ?? ""},${this.escCsv(s.description ?? "")}`);
      }
    }
    if (!entity || entity === "type") {
      const types = await this.typeRepo.findAll();
      if (lines.length === 0) lines.push("entity,code,name,classId,category,nature,subType,description,parentTypeId");
      for (const t of types) {
        const s = t.toState();
        lines.push(`type,${this.escCsv(s.code)},${this.escCsv(s.name)},${s.classId},${s.category},${s.nature},${s.subType ?? ""},${this.escCsv(s.description ?? "")},${s.parentTypeId ?? ""}`);
      }
    }
    if (!entity || entity === "mapping") {
      const mappings = await this.mappingRepo.findAll();
      if (lines.length === 0) lines.push("entity,accountId,mappingStandard,mappingType,targetCode,targetName,percentage,effectiveFrom,effectiveTo,description");
      for (const m of mappings) {
        const s = m.toState();
        lines.push(`mapping,${s.accountId},${s.mappingStandard},${s.mappingType},${this.escCsv(s.targetCode)},${this.escCsv(s.targetName ?? "")},${s.percentage ?? ""},${s.effectiveFrom.toISOString()},${s.effectiveTo ? s.effectiveTo.toISOString() : ""},${this.escCsv(s.description ?? "")}`);
      }
    }
    return lines.join("\n");
  }

  async exportJson(entity?: string): Promise<string> {
    const data: Record<string, unknown[]> = {};
    if (!entity || entity === "class") {
      data.classes = (await this.classRepo.findAll()).map(c => c.toState());
    }
    if (!entity || entity === "type") {
      data.types = (await this.typeRepo.findAll()).map(t => t.toState());
    }
    if (!entity || entity === "mapping") {
      data.mappings = (await this.mappingRepo.findAll()).map(m => m.toState());
    }
    return JSON.stringify(data, null, 2);
  }

  private async importRow(row: ImportRow): Promise<void> {
    switch (row.entity) {
      case "class": {
        await this.coaService.createClass({
          code: String(row.code), name: String(row.name),
          classType: row.classType as any,
          displayOrder: row.displayOrder ? Number(row.displayOrder) : undefined,
          description: row.description ? String(row.description) : undefined,
        });
        break;
      }
      case "type": {
        await this.coaService.createType({
          code: String(row.code), name: String(row.name),
          classId: String(row.classId), category: row.category as any,
          nature: row.nature as any, subType: row.subType as any,
          description: row.description ? String(row.description) : undefined,
          parentTypeId: row.parentTypeId ? String(row.parentTypeId) : undefined,
        });
        break;
      }
      case "mapping": {
        await this.coaService.createMapping({
          accountId: String(row.accountId), mappingStandard: row.mappingStandard as any,
          mappingType: row.mappingType as any, targetCode: String(row.targetCode),
          targetName: row.targetName ? String(row.targetName) : undefined,
          mappingRule: row.mappingRule ? String(row.mappingRule) : undefined,
          percentage: row.percentage ? Number(row.percentage) : undefined,
          effectiveFrom: new Date(String(row.effectiveFrom)),
          effectiveTo: row.effectiveTo ? new Date(String(row.effectiveTo)) : undefined,
          description: row.description ? String(row.description) : undefined,
        });
        break;
      }
      case "extension": {
        const { accountId } = row;
        if (!accountId) throw new DomainError("Validation", "accountId required for extension");
        const ext = await this.coaService.getOrCreateExtension(String(accountId));
        ext.modify(row as any);
        await this.extRepo.save(ext);
        break;
      }
      default:
        throw new DomainError("Validation", `Unknown entity: ${row.entity}`);
    }
  }

  private parseCsvLine(line: string): string[] {
    const result: string[] = [];
    let current = "";
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuotes && line[i + 1] === '"') { current += '"'; i++; }
        else inQuotes = !inQuotes;
      } else if (ch === "," && !inQuotes) {
        result.push(current.trim());
        current = "";
      } else {
        current += ch;
      }
    }
    result.push(current.trim());
    return result;
  }

  private escCsv(val: string): string {
    if (val.includes(",") || val.includes('"') || val.includes("\n")) {
      return `"${val.replace(/"/g, '""')}"`;
    }
    return val;
  }
}
