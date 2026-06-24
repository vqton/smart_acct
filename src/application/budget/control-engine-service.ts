import { Injectable } from "@nestjs/common";
import { DomainError } from "../../shared/domain-error.js";
import {
  PrismaBgtBudgetControlRepository,
  PrismaBgtBudgetDetailRepository,
  PrismaBgtReservationRepository,
} from "../../infrastructure/budget/budget-prisma-repos.js";
import { BgtBudgetControl } from "../../domain/budget/bgt-budget-control.js";
import { BgtBudgetReservation, BgtReservationLine } from "../../domain/budget/bgt-reservation.js";
import { BgtBudgetDetail } from "../../domain/budget/bgt-budget-detail.js";
import { BgtControlLevel, BgtCommitmentType, BgtReservationStatus } from "../../domain/budget/bgt-enums.js";

export interface CreateControlInput {
  budgetDetailId: string; controlLevel?: string; controlAction?: string;
  toleranceAmount?: number; tolerancePct?: number;
  effectiveFrom?: Date; effectiveTo?: Date;
}

export interface CreateReservationInput {
  budgetPlanId: string; reservationNumber: string;
  commitmentType?: string; sourceDocumentType?: string;
  sourceDocumentId?: string; sourceLineId?: string;
  description?: string; totalAmount: number; currencyCode?: string;
  expiresAt?: Date; createdById?: string;
}

@Injectable()
export class ControlEngineService {
  constructor(
    private readonly controlRepo: PrismaBgtBudgetControlRepository,
    private readonly detailRepo: PrismaBgtBudgetDetailRepository,
    private readonly reservationRepo: PrismaBgtReservationRepository,
  ) {}

  // ─── Budget Control ────────────────────────────────────────────────────────

  async createControl(p: CreateControlInput): Promise<BgtBudgetControl> {
    const detail = await this.detailRepo.findById(p.budgetDetailId);
    if (!detail) throw new DomainError("NotFound", "Budget detail not found");
    const control = BgtBudgetControl.create(p);
    await this.controlRepo.save(control);
    return control;
  }

  async checkBudget(detailId: string, requestedAmount: number, checkedById?: string): Promise<{ passed: boolean; action: string; message: string; availableAmount: number }> {
    const detail = await this.detailRepo.findById(detailId);
    if (!detail) throw new DomainError("NotFound", "Budget detail not found");
    const controls = await this.controlRepo.findActiveByBudgetDetail(detailId);
    if (controls.length === 0) {
      return { passed: true, action: "none", message: "No budget control configured", availableAmount: detail.availableAmount };
    }
    let passed = true;
    let action = "allow";
    let message = "Budget check passed";
    for (const control of controls) {
      const result = control.check(detail.availableAmount, requestedAmount, checkedById);
      await this.controlRepo.save(control);
      if (!result.passed) {
        passed = false;
        action = result.action;
        message = result.message;
      }
    }
    return { passed, action, message, availableAmount: detail.availableAmount };
  }

  async updateControl(id: string, p: Partial<CreateControlInput>): Promise<BgtBudgetControl> {
    const control = await this.controlRepo.findById(id);
    if (!control) throw new DomainError("NotFound", "Budget control not found");
    control.update(p);
    await this.controlRepo.save(control);
    return control;
  }

  // ─── Budget Reservations ───────────────────────────────────────────────────

  async createReservation(p: CreateReservationInput): Promise<BgtBudgetReservation> {
    const existing = await this.reservationRepo.findByNumber(p.reservationNumber);
    if (existing) throw new DomainError("Conflict", `Reservation ${p.reservationNumber} already exists`);
    const reservation = BgtBudgetReservation.create(p);
    await this.reservationRepo.save(reservation);
    return reservation;
  }

  async activateReservation(id: string): Promise<BgtBudgetReservation> {
    const reservation = await this.reservationRepo.findById(id);
    if (!reservation) throw new DomainError("NotFound", "Reservation not found");
    reservation.activate();
    await this.reservationRepo.save(reservation);
    return reservation;
  }

  async consumeReservation(id: string, amount: number): Promise<BgtBudgetReservation> {
    const reservation = await this.reservationRepo.findById(id);
    if (!reservation) throw new DomainError("NotFound", "Reservation not found");
    reservation.consume(amount);
    await this.reservationRepo.save(reservation);
    return reservation;
  }

  async releaseReservation(id: string, amount: number): Promise<BgtBudgetReservation> {
    const reservation = await this.reservationRepo.findById(id);
    if (!reservation) throw new DomainError("NotFound", "Reservation not found");
    reservation.release(amount);
    await this.reservationRepo.save(reservation);
    return reservation;
  }

  async cancelReservation(id: string, reason: string): Promise<void> {
    const reservation = await this.reservationRepo.findById(id);
    if (!reservation) throw new DomainError("NotFound", "Reservation not found");
    reservation.cancel(reason);
    await this.reservationRepo.save(reservation);
  }

  async getReservation(id: string): Promise<BgtBudgetReservation | null> {
    return this.reservationRepo.findById(id);
  }

  async listReservations(budgetPlanId?: string, status?: string): Promise<BgtBudgetReservation[]> {
    if (status) return this.reservationRepo.findByStatus(status);
    if (budgetPlanId) return this.reservationRepo.findByBudgetPlan(budgetPlanId);
    return this.reservationRepo.findActive();
  }

  async addReservationLine(id: string, p: {
    budgetDetailId: string; lineNumber: number; amount: number;
    glAccountId?: string; costCenterId?: string; departmentId?: string;
    projectId?: string; description?: string; periodNumber?: number;
  }): Promise<BgtBudgetReservation> {
    const reservation = await this.reservationRepo.findById(id);
    if (!reservation) throw new DomainError("NotFound", "Reservation not found");
    const line = BgtReservationLine.create({ reservationId: id, ...p });
    reservation.addLine(line);
    await this.reservationRepo.save(reservation);
    return reservation;
  }
}
