import {
  BgtBudgetStatus, BgtBudgetType, BgtControlLevel, BgtVersionStatus,
} from "./bgt-enums.js";

export interface BgtSpecification<T> {
  isSatisfiedBy(candidate: T): boolean;
  and(other: BgtSpecification<T>): BgtSpecification<T>;
  or(other: BgtSpecification<T>): BgtSpecification<T>;
  not(): BgtSpecification<T>;
}

abstract class BgtBaseSpec<T> implements BgtSpecification<T> {
  abstract isSatisfiedBy(c: T): boolean;
  and(o: BgtSpecification<T>): BgtSpecification<T> {
    return new BgtAndSpec(this, o);
  }
  or(o: BgtSpecification<T>): BgtSpecification<T> {
    return new BgtOrSpec(this, o);
  }
  not(): BgtSpecification<T> {
    return new BgtNotSpec(this);
  }
}

class BgtAndSpec<T> extends BgtBaseSpec<T> {
  constructor(private a: BgtSpecification<T>, private b: BgtSpecification<T>) { super(); }
  isSatisfiedBy(c: T): boolean { return this.a.isSatisfiedBy(c) && this.b.isSatisfiedBy(c); }
}
class BgtOrSpec<T> extends BgtBaseSpec<T> {
  constructor(private a: BgtSpecification<T>, private b: BgtSpecification<T>) { super(); }
  isSatisfiedBy(c: T): boolean { return this.a.isSatisfiedBy(c) || this.b.isSatisfiedBy(c); }
}
class BgtNotSpec<T> extends BgtBaseSpec<T> {
  constructor(private a: BgtSpecification<T>) { super(); }
  isSatisfiedBy(c: T): boolean { return !this.a.isSatisfiedBy(c); }
}

// ─── Budget Status Specifications ─────────────────────────────────────────────

export class BgtIsDraftSpec extends BgtBaseSpec<string> {
  isSatisfiedBy(s: string): boolean { return s === BgtBudgetStatus.Draft; }
}

export class BgtIsApprovedSpec extends BgtBaseSpec<string> {
  isSatisfiedBy(s: string): boolean { return s === BgtBudgetStatus.Approved; }
}

export class BgtIsActiveSpec extends BgtBaseSpec<string> {
  isSatisfiedBy(s: string): boolean {
    return [BgtBudgetStatus.Activated, BgtBudgetStatus.Execution, BgtBudgetStatus.Monitoring].includes(s as BgtBudgetStatus);
  }
}

export class BgtCanSubmitSpec extends BgtBaseSpec<string> {
  isSatisfiedBy(s: string): boolean {
    return [BgtBudgetStatus.Draft, BgtBudgetStatus.Preparation, BgtBudgetStatus.Revision].includes(s as BgtBudgetStatus);
  }
}

export class BgtCanApproveSpec extends BgtBaseSpec<string> {
  isSatisfiedBy(s: string): boolean {
    return [BgtBudgetStatus.Submitted, BgtBudgetStatus.Review].includes(s as BgtBudgetStatus);
  }
}

export class BgtCanModifySpec extends BgtBaseSpec<string> {
  isSatisfiedBy(s: string): boolean {
    return [BgtBudgetStatus.Draft, BgtBudgetStatus.Preparation, BgtBudgetStatus.Revision, BgtBudgetStatus.Reopened].includes(s as BgtBudgetStatus);
  }
}

export class BgtCanTransferSpec extends BgtBaseSpec<string> {
  isSatisfiedBy(s: string): boolean {
    return [BgtBudgetStatus.Activated, BgtBudgetStatus.Execution, BgtBudgetStatus.Monitoring, BgtBudgetStatus.Adjustment].includes(s as BgtBudgetStatus);
  }
}

// ─── Version Specifications ───────────────────────────────────────────────────

export class BgtVersionIsWorkingSpec extends BgtBaseSpec<string> {
  isSatisfiedBy(s: string): boolean { return s === BgtVersionStatus.Working; }
}

export class BgtVersionCanApproveSpec extends BgtBaseSpec<string> {
  isSatisfiedBy(s: string): boolean {
    return [BgtVersionStatus.Working, BgtVersionStatus.InReview].includes(s as BgtVersionStatus);
  }
}

// ─── Control Specifications ───────────────────────────────────────────────────

export class BgtBudgetCheckSpec {
  constructor(
    private readonly controlLevel: BgtControlLevel,
    private readonly toleranceAmount: number,
    private readonly tolerancePct: number,
  ) {}

  check(requestedAmount: number, availableAmount: number): { passed: boolean; action: string; message: string } {
    if (this.controlLevel === BgtControlLevel.None) {
      return { passed: true, action: "none", message: "Budget control disabled" };
    }
    if (requestedAmount <= availableAmount) {
      return { passed: true, action: "allow", message: "Sufficient budget available" };
    }
    const excess = requestedAmount - availableAmount;
    const excessPct = availableAmount > 0 ? (excess / availableAmount) * 100 : 100;
    const withinTolerance = this.toleranceAmount > 0 && excess <= this.toleranceAmount
      || this.tolerancePct > 0 && excessPct <= this.tolerancePct;
    if (this.controlLevel === BgtControlLevel.Soft) {
      return {
        passed: withinTolerance,
        action: withinTolerance ? "warn" : "warn",
        message: withinTolerance
          ? `Budget exceeded by ${excess} but within tolerance`
          : `Budget exceeded by ${excess} (${excessPct.toFixed(1)}%)`,
      };
    }
    if (this.controlLevel === BgtControlLevel.Advisory) {
      return {
        passed: withinTolerance,
        action: withinTolerance ? "allow" : "notify",
        message: withinTolerance
          ? "Budget check passed"
          : `Budget exceeded by ${excess} — notification sent`,
      };
    }
    return {
      passed: false,
      action: "block",
      message: `Insufficient budget: need ${requestedAmount}, available ${availableAmount}`,
    };
  }
}

// ─── Allocation Specifications ────────────────────────────────────────────────

export class BgtAllocationTotalMatchesSpec {
  constructor(private readonly totalAmount: number) {}
  isSatisfiedBy(lines: { allocationPct: number; allocationAmount: number }[]): boolean {
    const totalPct = lines.reduce((s, l) => s + l.allocationPct, 0);
    const totalAmt = lines.reduce((s, l) => s + l.allocationAmount, 0);
    if (totalPct > 0 && Math.abs(totalPct - 100) > 0.01) return false;
    if (totalAmt > 0 && Math.abs(totalAmt - this.totalAmount) > 0.01) return false;
    return true;
  }
}
