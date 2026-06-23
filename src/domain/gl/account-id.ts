import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class AccountId extends Identifier {
  static new(): AccountId {
    return new AccountId(IdGenerator.uuid());
  }
}
