import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class UserId extends Identifier {
  static new(): UserId {
    return new UserId(IdGenerator.uuid());
  }
}
