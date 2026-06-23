import { DomainError } from "../../shared/domain-error.js";
import { BankAccount, BankAccountState, AuthorizedSigner, AccountLimit } from "./bank-account.js";
import { BankStatement } from "./bank-statement.js";
import { BankReconciliation } from "./bank-reconciliation.js";
import { BankTransaction } from "./bank-transaction.js";
import { Bank, BankState } from "./bank-master.js";
import { BankAccountStatus, TransactionStatus, ReconciliationStatus, BankAccountCategory } from "./bank-enums.js";

export class ActiveAccountSpec {
  static isSatisfiedBy(account: BankAccount): boolean {
    return account.status === BankAccountStatus.Active;
  }

  static check(account: BankAccount): void {
    if (!this.isSatisfiedBy(account)) {
      throw new DomainError("BusinessRule",
        `Account ${account.accountNumber.value} is ${account.status}. Must be active.`);
    }
  }
}

export class PositiveAmountSpec {
  static check(amount: number): void {
    if (amount <= 0) throw new DomainError("BusinessRule", "Amount must be positive");
  }
}

export class SufficientBalanceSpec {
  static check(account: BankAccount, amount: number): void {
    const effective = account.availableBalance + account.overdraftLimit;
    if (amount > effective) {
      throw new DomainError("BusinessRule",
        `Insufficient balance. Available: ${account.availableBalance}, Overdraft: ${account.overdraftLimit}`);
    }
  }
}

export class NonClosedAccountSpec {
  static check(account: BankAccount): void {
    if (account.status === BankAccountStatus.Closed) {
      throw new DomainError("BusinessRule", "Cannot operate on closed account");
    }
  }
}

export class NonReconciledStatementSpec {
  static check(statement: BankStatement): void {
    if (statement.isReconciled) {
      throw new DomainError("BusinessRule", "Statement is already reconciled");
    }
  }
}

export class NonLockedStatementSpec {
  static check(statement: BankStatement): void {
    if (statement.isLocked) {
      throw new DomainError("BusinessRule", "Statement is locked");
    }
  }
}

export class MatchingCurrencySpec {
  static check(account: BankAccount, currencyCode: string): void {
    if (account.currencyCode !== currencyCode) {
      throw new DomainError("BusinessRule",
        `Currency mismatch. Account: ${account.currencyCode}, Transaction: ${currencyCode}`);
    }
  }
}

export class SignerCanSignSpec {
  static check(signer: AuthorizedSigner, amount: number): void {
    if (!signer.canSign(amount)) {
      throw new DomainError("BusinessRule", `Signer cannot authorize amount ${amount}`);
    }
  }
}

export class LimitNotExceededSpec {
  static check(limit: AccountLimit, amount: number): void {
    if (limit.exceedsLimit(amount)) {
      throw new DomainError("BusinessRule", `Amount ${amount} exceeds limit ${limit.maxAmount}`);
    }
  }
}

export class ValidStatementBalanceSpec {
  static check(statement: BankStatement): boolean {
    const expected = statement.openingBalance + statement.totalCredit - statement.totalDebit;
    return Math.abs(expected - statement.closingBalance) <= 0.01;
  }
}

export class ValidReconciliationTransitionSpec {
  static check(status: ReconciliationStatus, target: ReconciliationStatus): void {
    const valid: Record<string, string[]> = {
      [ReconciliationStatus.Open]: [ReconciliationStatus.InProgress],
      [ReconciliationStatus.InProgress]: [ReconciliationStatus.Matched, ReconciliationStatus.DifferenceFound],
      [ReconciliationStatus.Matched]: [ReconciliationStatus.Resolved],
      [ReconciliationStatus.Resolved]: [ReconciliationStatus.Approved],
      [ReconciliationStatus.Approved]: [ReconciliationStatus.Closed],
    };
    const allowed = valid[status] ?? [];
    if (!allowed.includes(target)) {
      throw new DomainError("BusinessRule", `Cannot transition from ${status} to ${target}`);
    }
  }
}

export class DuplicateStatementSpec {
  static check(statementNumber: string, existing: BankStatement | null): void {
    if (existing) {
      throw new DomainError("BusinessRule", `Duplicate statement number: ${statementNumber}`);
    }
  }
}

export class DuplicateTransactionSpec {
  static check(reference: string, existing: BankTransaction | null): void {
    if (existing) {
      throw new DomainError("BusinessRule", `Duplicate transaction reference: ${reference}`);
    }
  }
}

export class ValidTransactionTransitionSpec {
  static check(status: TransactionStatus, target: TransactionStatus): void {
    const valid: Record<string, string[]> = {
      [TransactionStatus.Draft]: [TransactionStatus.Pending, TransactionStatus.Cancelled],
      [TransactionStatus.Pending]: [TransactionStatus.Authorized, TransactionStatus.Cancelled],
      [TransactionStatus.Authorized]: [TransactionStatus.Approved, TransactionStatus.Cancelled],
      [TransactionStatus.Approved]: [TransactionStatus.Executed, TransactionStatus.Cancelled],
      [TransactionStatus.Executed]: [TransactionStatus.Sent, TransactionStatus.Failed],
      [TransactionStatus.Sent]: [TransactionStatus.Completed, TransactionStatus.Failed],
      [TransactionStatus.Completed]: [TransactionStatus.Reversed],
    };
    const allowed = valid[status] ?? [];
    if (!allowed.includes(target)) {
      throw new DomainError("BusinessRule", `Invalid transition from ${status} to ${target}`);
    }
  }
}

export class BankCodeUniquenessSpec {
  static check(code: string, existing: Bank | null): void {
    if (existing) {
      throw new DomainError("BusinessRule", `Bank code already exists: ${code}`);
    }
  }
}
