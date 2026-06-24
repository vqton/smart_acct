import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import { CustomerId } from "../../domain/sales/sales-ids.js";
import { Customer, type CustomerState } from "../../domain/sales/sales-customer.js";
import { SlsCustomerStatus, SlsCustomerType, SlsCustomerCategory, SlsPriceGroup, SlsDiscountGroup } from "../../domain/sales/sales-enums.js";
import { ActiveCustomerSpec } from "../../domain/sales/sales-specifications.js";
import { PrismaCustomerRepository } from "../../infrastructure/sales/sales-prisma-repos.js";

@Injectable()
export class SalesCustomerService {
  constructor(private readonly custRepo: PrismaCustomerRepository) {}

  async create(p: {
    code: string; name: string; nameEn?: string; groupId?: string;
    customerType?: SlsCustomerType; category?: SlsCustomerCategory;
    taxCode?: string; phone?: string; email?: string;
    address?: string; ward?: string; district?: string; province?: string;
    priceGroup?: SlsPriceGroup; discountGroup?: SlsDiscountGroup;
    creditLimit?: number; paymentTermCode?: string;
    storeId?: string; salespersonId?: string; branchId?: string;
  }): Promise<Customer> {
    const existing = await this.custRepo.findByCode(p.code);
    if (existing) throw new DomainError("Conflict", `Customer code ${p.code} already exists`);
    const customer = Customer.create(p);
    await this.custRepo.save(customer);
    return customer;
  }

  async update(id: string, p: Partial<{ name: string; nameEn: string; phone: string; email: string; address: string; ward: string; district: string; province: string; priceGroup: SlsPriceGroup; discountGroup: SlsDiscountGroup; paymentTermCode: string; salespersonId: string; branchId: string }>): Promise<Customer> {
    const customer = await this.custRepo.findById(CustomerId.from(id));
    if (!customer) throw new DomainError("NotFound", "Customer not found");
    customer.update(p as any);
    await this.custRepo.save(customer);
    return customer;
  }

  async getById(id: string): Promise<Customer | null> {
    return this.custRepo.findById(CustomerId.from(id));
  }

  async getByCode(code: string): Promise<Customer | null> {
    return this.custRepo.findByCode(code);
  }

  async search(criteria: Partial<{ code: string; name: string; taxCode: string; status: string; phone: string; email: string }>): Promise<CustomerState[]> {
    return this.custRepo.search(criteria);
  }

  async list(): Promise<CustomerState[]> {
    return this.custRepo.findAll();
  }

  async block(id: string, reason: string): Promise<Customer> {
    const customer = await this.custRepo.findById(CustomerId.from(id));
    if (!customer) throw new DomainError("NotFound", "Customer not found");
    customer.block(reason);
    await this.custRepo.save(customer);
    return customer;
  }

  async unblock(id: string): Promise<Customer> {
    const customer = await this.custRepo.findById(CustomerId.from(id));
    if (!customer) throw new DomainError("NotFound", "Customer not found");
    customer.unblock();
    await this.custRepo.save(customer);
    return customer;
  }

  async setCreditLimit(id: string, limit: number, reason?: string): Promise<Customer> {
    const customer = await this.custRepo.findById(CustomerId.from(id));
    if (!customer) throw new DomainError("NotFound", "Customer not found");
    customer.setCreditLimit(limit, reason);
    await this.custRepo.save(customer);
    return customer;
  }

  async blacklist(id: string, reason: string): Promise<Customer> {
    const customer = await this.custRepo.findById(CustomerId.from(id));
    if (!customer) throw new DomainError("NotFound", "Customer not found");
    customer.blacklist(reason);
    await this.custRepo.save(customer);
    return customer;
  }

  async removeBlacklist(id: string): Promise<Customer> {
    const customer = await this.custRepo.findById(CustomerId.from(id));
    if (!customer) throw new DomainError("NotFound", "Customer not found");
    customer.removeBlacklist();
    await this.custRepo.save(customer);
    return customer;
  }

  async checkActive(customerId: CustomerId): Promise<Customer> {
    const customer = await this.custRepo.findById(customerId);
    if (!customer) throw new DomainError("NotFound", "Customer not found");
    ActiveCustomerSpec.check(customer.status, customer.isBlacklisted, customer.code);
    return customer;
  }
}
