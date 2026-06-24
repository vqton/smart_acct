import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { VendorId, VendorQualificationId } from "../../domain/purchasing/purchasing-ids.js";
import { Vendor, VendorQualification, VendorEvaluation } from "../../domain/purchasing/purchasing-vendor.js";
import { VendorStatus, EvaluationScore, VendorQualificationStatus } from "../../domain/purchasing/purchasing-enums.js";
import { ActiveVendorSpec, VendorNotBlockedSpec } from "../../domain/purchasing/purchasing-specifications.js";
import { PrismaVendorRepository, PrismaVendorQualificationRepository, PrismaVendorEvaluationRepository } from "../../infrastructure/purchasing/purchasing-prisma-repos.js";

@Injectable()
export class PurchasingVendorService {
  constructor(
    private readonly vendorRepo: PrismaVendorRepository,
    private readonly qualRepo: PrismaVendorQualificationRepository,
    private readonly evalRepo: PrismaVendorEvaluationRepository,
  ) {}

  async create(p: {
    code: string; name: string; country: string; nameEn?: string; taxCode?: string;
    vendorType?: string; category?: string; classification?: string;
    phone?: string; email?: string; address?: string; ward?: string;
    district?: string; province?: string; postalCode?: string;
    paymentTermCode?: string; currencyCode?: string;
  }): Promise<Vendor> {
    const existing = await this.vendorRepo.findByCode(p.code);
    if (existing) throw new DomainError("Conflict", `Vendor code ${p.code} already exists`);
    const v = Vendor.create(p as any);
    await this.vendorRepo.save(v);
    return v;
  }

  async getById(id: string): Promise<Vendor | null> {
    return this.vendorRepo.findById(VendorId.from(id));
  }

  async getByCode(code: string): Promise<Vendor | null> {
    return this.vendorRepo.findByCode(code);
  }

  async list(): Promise<Vendor[]> {
    return this.vendorRepo.findAll();
  }

  async search(criteria: { code?: string; name?: string; taxCode?: string; status?: string; category?: string }): Promise<Vendor[]> {
    return this.vendorRepo.search(criteria);
  }

  async update(id: string, data: Partial<{
    name: string; nameEn: string | null; taxCode: string | null; vendorType: string;
    category: string; classification: string; phone: string | null; email: string | null;
    address: string | null; paymentTermCode: string | null; currencyCode: string;
  }>): Promise<Vendor> {
    const v = await this.vendorRepo.findById(VendorId.from(id));
    if (!v) throw new DomainError("NotFound", "Vendor not found");
    v.update(data as any);
    await this.vendorRepo.save(v);
    return v;
  }

  async block(id: string, reason: string): Promise<Vendor> {
    const v = await this.vendorRepo.findById(VendorId.from(id));
    if (!v) throw new DomainError("NotFound", "Vendor not found");
    v.block(reason);
    await this.vendorRepo.save(v);
    return v;
  }

  async unblock(id: string): Promise<Vendor> {
    const v = await this.vendorRepo.findById(VendorId.from(id));
    if (!v) throw new DomainError("NotFound", "Vendor not found");
    v.unblock();
    await this.vendorRepo.save(v);
    return v;
  }

  async deactivate(id: string): Promise<Vendor> {
    const v = await this.vendorRepo.findById(VendorId.from(id));
    if (!v) throw new DomainError("NotFound", "Vendor not found");
    v.deactivate();
    await this.vendorRepo.save(v);
    return v;
  }

  async qualify(vendorId: string, qualifiedBy: string, expiresAt?: Date, notes?: string): Promise<VendorQualification> {
    const v = await this.vendorRepo.findById(VendorId.from(vendorId));
    if (!v) throw new DomainError("NotFound", "Vendor not found");
    ActiveVendorSpec.check(v);
    const q = VendorQualification.create({ vendorId, qualifiedBy, expiresAt, notes });
    q.qualify();
    await this.qualRepo.save(q);
    return q;
  }

  async evaluate(vendorId: string, evaluator: string, score: EvaluationScore, criteria: string, comments?: string): Promise<VendorEvaluation> {
    const v = await this.vendorRepo.findById(VendorId.from(vendorId));
    if (!v) throw new DomainError("NotFound", "Vendor not found");
    const e = VendorEvaluation.create({ vendorId, evaluator, score, criteria, comments });
    await this.evalRepo.save(e);
    return e;
  }

  async getQualifications(vendorId: string): Promise<VendorQualification[]> {
    return this.qualRepo.findByVendorId(vendorId);
  }

  async getEvaluations(vendorId: string): Promise<VendorEvaluation[]> {
    return this.evalRepo.findByVendorId(vendorId);
  }
}
