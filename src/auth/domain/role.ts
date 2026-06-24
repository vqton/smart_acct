import { DomainError } from "../../shared/domain-error.js";
import { Entity } from "../../shared/entity.js";
import { RoleId } from "./role-id.js";

export interface RoleState {
  id: string;
  name: string;
  description: string | null;
}

export class Role extends Entity<RoleId> {
  private _id: RoleId;
  private _name: string;
  private _description: string | null;
  private _permissions: string[];

  private constructor(id: RoleId, name: string, description: string | null) {
    super();
    this._id = id;
    this._name = name;
    this._description = description;
    this._permissions = [];
  }

  static create(params: { name: string; description?: string | null }): Role {
    if (!params.name?.trim()) {
      throw new DomainError("Validation", "Role name is required");
    }
    return new Role(RoleId.new(), params.name.toUpperCase(), params.description ?? null);
  }

  static load(state: RoleState): Role {
    return new Role(new RoleId(state.id), state.name, state.description);
  }

  get id(): RoleId { return this._id; }
  get name(): string { return this._name; }
  get description(): string | null { return this._description; }

  hasPermission(permission: string): boolean {
    return this._permissions.includes(permission);
  }

  toState(): RoleState {
    return {
      id: this._id.value,
      name: this._name,
      description: this._description,
    };
  }
}
