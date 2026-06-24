import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class RoleId extends Identifier {
  static new(): RoleId {
    return new RoleId(IdGenerator.uuid());
  }
}
