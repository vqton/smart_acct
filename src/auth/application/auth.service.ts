import { Injectable, UnauthorizedException, ConflictException } from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import * as bcrypt from "bcrypt";
import { PrismaUserRepository } from "../infrastructure/prisma-user-repository.js";
import { User } from "../domain/user.js";
import { UserId } from "../domain/user-id.js";
import { Role } from "../domain/role.js";

const BCRYPT_ROUNDS = 12;

@Injectable()
export class AuthService {
  constructor(
    private readonly userRepo: PrismaUserRepository,
    private readonly jwtService: JwtService,
  ) {}

  async register(params: { email: string; password: string; displayName: string }): Promise<{ id: string; email: string }> {
    const existing = await this.userRepo.findByEmail(params.email);
    if (existing) throw new ConflictException("Email already registered");

    const passwordHash = await bcrypt.hash(params.password, BCRYPT_ROUNDS);
    const user = User.create({ email: params.email, passwordHash, displayName: params.displayName });
    await this.userRepo.save(user);
    return { id: user.id.value, email: user.email };
  }

  async login(params: { email: string; password: string }): Promise<{ accessToken: string; user: { id: string; email: string; displayName: string } }> {
    const user = await this.userRepo.findByEmail(params.email);
    if (!user) throw new UnauthorizedException("Invalid email or password");
    if (!user.isActive) throw new UnauthorizedException("Account is deactivated");

    const valid = await bcrypt.compare(params.password, user.passwordHash);
    if (!valid) throw new UnauthorizedException("Invalid email or password");

    user.markLogin();
    await this.userRepo.save(user);

    const payload = { sub: user.id.value, email: user.email };
    return {
      accessToken: this.jwtService.sign(payload),
      user: { id: user.id.value, email: user.email, displayName: user.displayName },
    };
  }

  async getProfile(userId: string): Promise<{ id: string; email: string; displayName: string; roles: string[] }> {
    const user = await this.userRepo.findById(new UserId(userId));
    if (!user) throw new UnauthorizedException("User not found");
    return {
      id: user.id.value,
      email: user.email,
      displayName: user.displayName,
      roles: user.roles.map(r => r.name),
    };
  }
}
