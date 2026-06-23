import { DomainError } from "../../shared/domain-error.js";
import {
  FiscalYear, FiscalYearId, FiscalYearState,
  Period, PeriodId, PeriodState, PeriodStatus,
} from "../../domain/gl/period.js";
import { FiscalYearRepository, PeriodRepository, JournalBatchRepository, UnitOfWork } from "../../domain/gl/repositories.js";

export class PeriodService {
  constructor(
    private readonly fiscalYearRepo: FiscalYearRepository,
    private readonly periodRepo: PeriodRepository,
    private readonly batchRepo: JournalBatchRepository,
    private readonly uow: UnitOfWork,
  ) {}

  async createFiscalYear(code: string, name: string, startDate: string, endDate: string): Promise<FiscalYearState> {
    const existing = await this.fiscalYearRepo.findByCode(code);
    if (existing) throw new DomainError("Conflict", `Fiscal year ${code} already exists`);

    const fy = new FiscalYear(
      FiscalYearId.new(),
      code,
      name,
      new Date(startDate),
      new Date(endDate),
    );
    fy.generatePeriods("monthly");

    await this.uow.begin();
    try {
      await this.fiscalYearRepo.save(fy);
      for (const p of fy.periods) {
        await this.periodRepo.save(p);
      }
      await this.uow.commit();
    } catch (error) {
      await this.uow.rollback();
      throw error;
    }
    return fy.toState();
  }

  async findFiscalYearById(id: string): Promise<FiscalYearState> {
    const fy = await this.fiscalYearRepo.findById(new FiscalYearId(id));
    if (!fy) throw new DomainError("NotFound", "Fiscal year not found");
    return fy.toState();
  }

  async findActiveFiscalYear(): Promise<FiscalYearState | null> {
    const fy = await this.fiscalYearRepo.findActive();
    return fy?.toState() ?? null;
  }

  async listFiscalYears(): Promise<FiscalYearState[]> {
    const fys = await this.fiscalYearRepo.findAll();
    return fys.map(fy => fy.toState());
  }

  async closeFiscalYear(id: string, userId: string): Promise<FiscalYearState> {
    const fy = await this.fiscalYearRepo.findById(new FiscalYearId(id));
    if (!fy) throw new DomainError("NotFound", "Fiscal year not found");
    fy.close(userId);

    await this.uow.begin();
    try {
      await this.fiscalYearRepo.save(fy);
      await this.uow.commit();
    } catch (error) {
      await this.uow.rollback();
      throw error;
    }
    return fy.toState();
  }

  async closePeriod(id: string, userId: string): Promise<PeriodState> {
    const period = await this.periodRepo.findById(new PeriodId(id));
    if (!period) throw new DomainError("NotFound", "Period not found");
    period.close(userId);
    await this.periodRepo.save(period);
    return period.toState();
  }

  async reopenPeriod(id: string): Promise<PeriodState> {
    const period = await this.periodRepo.findById(new PeriodId(id));
    if (!period) throw new DomainError("NotFound", "Period not found");
    period.reopen();
    await this.periodRepo.save(period);
    return period.toState();
  }

  async lockPeriod(id: string): Promise<PeriodState> {
    const period = await this.periodRepo.findById(new PeriodId(id));
    if (!period) throw new DomainError("NotFound", "Period not found");
    period.lock();
    await this.periodRepo.save(period);
    return period.toState();
  }

  async findPeriodsByFiscalYear(fiscalYearId: string): Promise<PeriodState[]> {
    const periods = await this.periodRepo.findByFiscalYear(fiscalYearId);
    return periods.map(p => p.toState());
  }
}
