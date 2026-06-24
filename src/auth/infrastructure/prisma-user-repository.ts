import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service.js";
import { User, type UserState } from "../domain/user.js";
import { UserId } from "../domain/user-id.js";
import { Role } from "../domain/role.js";
import { type UserRepository } from "../domain/user-repository.js";

@Injectable()
export class PrismaUserRepository implements UserRepository {
  constructor(private readonly prisma: PrismaService) {}

  private toDomain(row: any, roles?: any[]): User {
    return User.load({
      id: row.id,
      email: row.email,
      passwordHash: row.passwordHash,
      displayName: row.displayName,
      isActive: row.isActive,
      lastLoginAt: row.lastLoginAt ?? null,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      roles: (roles ?? row.roles ?? []).map((ur: any) => ({
        id: ur.role?.id ?? ur.id,
        name: ur.role?.name ?? ur.name,
        description: ur.role?.description ?? ur.description,
      })),
    });
  }

  async save(user: User): Promise<void> {
    const s = user.toState();
    await this.prisma.user.upsert({
      where: { id: s.id },
      create: {
        id: s.id,
        email: s.email,
        passwordHash: s.passwordHash,
        displayName: s.displayName,
        isActive: s.isActive,
        lastLoginAt: s.lastLoginAt,
      },
      update: {
        email: s.email,
        passwordHash: s.passwordHash,
        displayName: s.displayName,
        isActive: s.isActive,
        lastLoginAt: s.lastLoginAt,
      },
    });
  }

  async findById(id: UserId): Promise<User | null> {
    const row = await this.prisma.user.findUnique({
      where: { id: id.value },
      include: { roles: { include: { role: true } } },
    });
    return row ? this.toDomain(row, row.roles) : null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const row = await this.prisma.user.findUnique({
      where: { email },
      include: { roles: { include: { role: true } } },
    });
    return row ? this.toDomain(row, row.roles) : null;
  }

  async findAll(): Promise<User[]> {
    const rows = await this.prisma.user.findMany({
      include: { roles: { include: { role: true } } },
    });
    return rows.map(r => this.toDomain(r, r.roles));
  }

  async delete(id: UserId): Promise<void> {
    await this.prisma.user.delete({ where: { id: id.value } });
  }
}
