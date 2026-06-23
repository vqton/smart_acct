import { Identifier } from "./identifier.js";

export abstract class Entity<TId extends Identifier> {
  abstract get id(): TId;

  equals(other: Entity<TId>): boolean {
    return this.id.equals(other.id);
  }
}
