export class DomainError extends Error {
  constructor(
    readonly kind: "Validation" | "NotFound" | "Conflict" | "Infrastructure" | "BusinessRule",
    message: string,
  ) {
    super(message);
    this.name = "DomainError";
  }
}
