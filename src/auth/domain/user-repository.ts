import { User } from "./user.js";
import { UserId } from "./user-id.js";
import { Role } from "./role.js";
import { RoleId } from "./role-id.js";

export interface UserRepository {
  save(user: User): Promise<void>;
  findById(id: UserId): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  findAll(): Promise<User[]>;
  delete(id: UserId): Promise<void>;
}

export interface RoleRepository {
  save(role: Role): Promise<void>;
  findById(id: RoleId): Promise<Role | null>;
  findByName(name: string): Promise<Role | null>;
  findAll(): Promise<Role[]>;
  delete(id: RoleId): Promise<void>;
}
