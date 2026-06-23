import { Identifier, IdGenerator } from "../../shared/identifier.js";

export class CoaAccountId extends Identifier {
  static new(): CoaAccountId {
    return new CoaAccountId(IdGenerator.uuid());
  }
}

export class AccountTypeId extends Identifier {
  static new(): AccountTypeId {
    return new AccountTypeId(IdGenerator.uuid());
  }
}

export class AccountClassId extends Identifier {
  static new(): AccountClassId {
    return new AccountClassId(IdGenerator.uuid());
  }
}

export class AccountMappingId extends Identifier {
  static new(): AccountMappingId {
    return new AccountMappingId(IdGenerator.uuid());
  }
}

export class AccountExtensionId extends Identifier {
  static new(): AccountExtensionId {
    return new AccountExtensionId(IdGenerator.uuid());
  }
}

export class HierarchyChangeId extends Identifier {
  static new(): HierarchyChangeId {
    return new HierarchyChangeId(IdGenerator.uuid());
  }
}

export class CodeChangeId extends Identifier {
  static new(): CodeChangeId {
    return new CodeChangeId(IdGenerator.uuid());
  }
}

export class StatusChangeId extends Identifier {
  static new(): StatusChangeId {
    return new StatusChangeId(IdGenerator.uuid());
  }
}
