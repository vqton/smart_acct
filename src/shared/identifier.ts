export abstract class Identifier {
  constructor(readonly value: string) {}

  equals(other: Identifier): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }
}

export class IdGenerator {
  static uuid(): string {
    return crypto.randomUUID();
  }
}
