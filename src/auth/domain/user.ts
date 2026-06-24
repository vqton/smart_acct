import { AggregateRoot } from "../../shared/aggregate-root.js";
import { DomainError } from "../../shared/domain-error.js";
import { UserId } from "./user-id.js";
import { Role } from "./role.js";

export interface UserState {
  id: string;
  email: string;
  passwordHash: string;
  displayName: string;
  isActive: boolean;
  roles: Array<{ id: string; name: string; description: string | null }>;
  lastLoginAt: Date | null;
  createdAt: Date;
  updatedAt: Date;
}

export class User extends AggregateRoot<UserId> {
  private _id: UserId;
  private _email: string;
  private _passwordHash: string;
  private _displayName: string;
  private _isActive: boolean;
  private _roles: Role[];
  private _lastLoginAt: Date | null;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(
    id: UserId,
    email: string,
    passwordHash: string,
    displayName: string,
  ) {
    super();
    this._id = id;
    this._email = email;
    this._passwordHash = passwordHash;
    this._displayName = displayName;
    this._isActive = true;
    this._roles = [];
    this._lastLoginAt = null;
    this._createdAt = new Date();
    this._updatedAt = new Date();
  }

  static create(params: {
    email: string;
    passwordHash: string;
    displayName: string;
  }): User {
    if (!params.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(params.email)) {
      throw new DomainError("Validation", "Invalid email format");
    }
    if (!params.passwordHash) {
      throw new DomainError("Validation", "Password hash is required");
    }
    if (!params.displayName?.trim()) {
      throw new DomainError("Validation", "Display name is required");
    }
    return new User(UserId.new(), params.email, params.passwordHash, params.displayName);
  }

  static load(state: UserState): User {
    const u = new User(
      new UserId(state.id),
      state.email,
      state.passwordHash,
      state.displayName,
    );
    u._isActive = state.isActive;
    u._roles = state.roles.map(r => Role.load({ id: r.id, name: r.name, description: r.description }));
    u._lastLoginAt = state.lastLoginAt;
    u._createdAt = state.createdAt;
    u._updatedAt = state.updatedAt;
    return u;
  }

  get id(): UserId { return this._id; }
  get email(): string { return this._email; }
  get passwordHash(): string { return this._passwordHash; }
  get displayName(): string { return this._displayName; }
  get isActive(): boolean { return this._isActive; }
  get roles(): Role[] { return [...this._roles]; }
  get lastLoginAt(): Date | null { return this._lastLoginAt; }

  hasPermission(permission: string): boolean {
    return this._roles.some(r => r.hasPermission(permission));
  }

  hasRole(roleName: string): boolean {
    return this._roles.some(r => r.name === roleName);
  }

  addRole(role: Role): void {
    if (this._roles.some(r => r.id.equals(role.id))) {
      throw new DomainError("Conflict", "User already has this role");
    }
    this._roles.push(role);
    this._updatedAt = new Date();
  }

  removeRole(roleId: string): void {
    const idx = this._roles.findIndex(r => r.id.value === roleId);
    if (idx === -1) throw new DomainError("NotFound", "Role not found on user");
    this._roles.splice(idx, 1);
    this._updatedAt = new Date();
  }

  markLogin(): void {
    this._lastLoginAt = new Date();
    this._updatedAt = new Date();
  }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
  }

  activate(): void {
    this._isActive = true;
    this._updatedAt = new Date();
  }

  toState(): UserState {
    return {
      id: this._id.value,
      email: this._email,
      passwordHash: this._passwordHash,
      displayName: this._displayName,
      isActive: this._isActive,
      roles: this._roles.map(r => ({
        id: r.id.value,
        name: r.name,
        description: r.description,
      })),
      lastLoginAt: this._lastLoginAt,
      createdAt: this._createdAt,
      updatedAt: this._updatedAt,
    };
  }
}
