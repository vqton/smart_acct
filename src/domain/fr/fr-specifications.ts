import { FrReportStatus, FrRowType, FrConsolidationStatus } from "./fr-enums.js";
import type { ReportDefinition } from "./fr-report-definition.js";
import type { ConsolidationRun } from "./fr-consolidation.js";

export interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
  and(other: Specification<T>): Specification<T>;
  or(other: Specification<T>): Specification<T>;
}

abstract class BaseSpecification<T> implements Specification<T> {
  abstract isSatisfiedBy(candidate: T): boolean;
  and(other: Specification<T>): Specification<T> {
    return new AndSpecification(this, other);
  }
  or(other: Specification<T>): Specification<T> {
    return new OrSpecification(this, other);
  }
}

class AndSpecification<T> extends BaseSpecification<T> {
  constructor(private left: Specification<T>, private right: Specification<T>) { super(); }
  isSatisfiedBy(candidate: T): boolean {
    return this.left.isSatisfiedBy(candidate) && this.right.isSatisfiedBy(candidate);
  }
}

class OrSpecification<T> extends BaseSpecification<T> {
  constructor(private left: Specification<T>, private right: Specification<T>) { super(); }
  isSatisfiedBy(candidate: T): boolean {
    return this.left.isSatisfiedBy(candidate) || this.right.isSatisfiedBy(candidate);
  }
}

export class ActiveReportSpec extends BaseSpecification<ReportDefinition> {
  isSatisfiedBy(report: ReportDefinition): boolean {
    return report.status === FrReportStatus.Active;
  }
}

export class ReportHasRowsSpec extends BaseSpecification<ReportDefinition> {
  isSatisfiedBy(report: ReportDefinition): boolean {
    return report.rows.length > 0;
  }
}

export class ConsolidationCanCompleteSpec extends BaseSpecification<ConsolidationRun> {
  isSatisfiedBy(run: ConsolidationRun): boolean {
    if (run.status !== FrConsolidationStatus.InProgress) return false;
    if (run.entries.length === 0) return false;
    const unbalanced = run.entries.filter(e => e.debitAmount !== e.creditAmount);
    return unbalanced.length === 0;
  }
}

export class ConsolidationCanApproveSpec extends BaseSpecification<ConsolidationRun> {
  isSatisfiedBy(run: ConsolidationRun): boolean {
    return run.status === FrConsolidationStatus.Verified;
  }
}
