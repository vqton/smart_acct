import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import { Role, type RoleState } from "../domain/role.js";
import { RoleId } from "../domain/role-id.js";
import { type RoleRepository } from "../domain/user-repository.js";

@Injectable()
export class PrismaRoleRepository implements RoleRepository {
  constructor(private readonly prisma: PrismaService) {}

  async save(role: Role): Promise<void> {
    const s = role.toState();
    await this.prisma.role.upsert({
      where: { id: s.id },
      create: { id: s.id, name: s.name, description: s.description },
      update: { name: s.name, description: s.description },
    });
  }

  async findById(id: RoleId): Promise<Role | null> {
    const row = await this.prisma.role.findUnique({ where: { id: id.value } });
    return row ? Role.load({ id: row.id, name: row.name, description: row.description }) : null;
  }

  async findByName(name: string): Promise<Role | null> {
    const row = await this.prisma.role.findUnique({ where: { name } });
    return row ? Role.load({ id: row.id, name: row.name, description: row.description }) : null;
  }

  async findAll(): Promise<Role[]> {
    const rows = await this.prisma.role.findMany();
    return rows.map(r => Role.load({ id: r.id, name: r.name, description: r.description }));
  }

  async delete(id: RoleId): Promise<void> {
    await this.prisma.role.delete({ where: { id: id.value } });
  }
}
