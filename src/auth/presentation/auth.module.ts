import { Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { JwtModule } from "@nestjs/jwt";
import { PassportModule } from "@nestjs/passport";
import { AuthController } from "./auth.controller.js";
import { AuthService } from "../application/auth.service.js";
import { JwtStrategy } from "../infrastructure/jwt.strategy.js";
import { PrismaUserRepository } from "../infrastructure/prisma-user-repository.js";
import { PrismaRoleRepository } from "../infrastructure/prisma-role-repository.js";
import { PrismaModule } from "../../prisma/prisma.module.js";
import { JwtAuthGuard } from "../infrastructure/jwt-auth.guard.js";
import { RolesGuard } from "../infrastructure/roles.guard.js";

@Module({
  imports: [
    PrismaModule,
    PassportModule.register({ defaultStrategy: "jwt" }),
    JwtModule.registerAsync({
      useFactory: () => ({
        secret: process.env.JWT_SECRET ?? "smart-acct-dev-secret",
        signOptions: { expiresIn: "8h" },
      }),
    }),
  ],
  controllers: [AuthController],
  providers: [
    AuthService,
    JwtStrategy,
    JwtAuthGuard,
    RolesGuard,
    { provide: APP_GUARD, useClass: JwtAuthGuard },
    { provide: "UserRepository", useClass: PrismaUserRepository },
    { provide: "RoleRepository", useClass: PrismaRoleRepository },
    PrismaUserRepository,
    PrismaRoleRepository,
  ],
  exports: [JwtAuthGuard, RolesGuard, JwtModule],
})
export class AuthModule {}
