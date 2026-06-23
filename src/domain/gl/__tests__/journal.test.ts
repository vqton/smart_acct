import { describe, it, expect } from "vitest";
import { JournalBatch, JournalEntryStatus, JournalType } from "../journal.js";

describe("JournalBatch", () => {
  const validParams = {
    batchNumber: "JOURNAL-0001",
    journalType: JournalType.Standard,
    periodId: "period-1",
    fiscalYearId: "fy-2026",
    voucherDate: new Date("2026-01-15"),
    postingDate: new Date("2026-01-15"),
    description: "Test journal entry",
    createdById: "user-1",
  };

  it("creates draft batch", () => {
    const batch = JournalBatch.create(validParams);
    expect(batch.status).toBe(JournalEntryStatus.Draft);
    expect(batch.batchNumber).toBe("JOURNAL-0001");
    expect(batch.lines).toHaveLength(0);
    expect(batch.totalDebit).toBe(0);
    expect(batch.totalCredit).toBe(0);
  });

  it("adds lines and tracks totals", () => {
    const batch = JournalBatch.create(validParams);
    batch.addLine({
      accountId: "acc-debit",
      debitAmount: 1000,
      creditAmount: 0,
      foreignDebitAmount: 0,
      foreignCreditAmount: 0,
      currencyCode: "VND",
      exchangeRate: 1,
      description: "Debit line",
      costCenterId: null,
      departmentId: null,
      projectId: null,
    });
    batch.addLine({
      accountId: "acc-credit",
      debitAmount: 0,
      creditAmount: 1000,
      foreignDebitAmount: 0,
      foreignCreditAmount: 0,
      currencyCode: "VND",
      exchangeRate: 1,
      description: "Credit line",
      costCenterId: null,
      departmentId: null,
      projectId: null,
    });
    expect(batch.lines).toHaveLength(2);
    expect(batch.totalDebit).toBe(1000);
    expect(batch.totalCredit).toBe(1000);
  });

  it("validates debit equals credit", () => {
    const batch = JournalBatch.create(validParams);
    batch.addLine({
      accountId: "acc-debit",
      debitAmount: 1000,
      creditAmount: 0,
      foreignDebitAmount: 0,
      foreignCreditAmount: 0,
      currencyCode: "VND",
      exchangeRate: 1,
      description: "Debit",
      costCenterId: null,
      departmentId: null,
      projectId: null,
    });
    expect(() => batch.validateDebitCreditEqual()).toThrow();
  });

  it("rejects empty lines on submit", () => {
    const batch = JournalBatch.create(validParams);
    expect(() => batch.submit()).toThrow("empty batch");
  });

  it("follows full lifecycle: draft -> submit -> approve -> post", () => {
    const batch = JournalBatch.create(validParams);
    batch.addLine({
      accountId: "acc-debit",
      debitAmount: 500, creditAmount: 0,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
      currencyCode: "VND", exchangeRate: 1,
      description: null,
      costCenterId: null, departmentId: null, projectId: null,
    });
    batch.addLine({
      accountId: "acc-credit",
      debitAmount: 0, creditAmount: 500,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
      currencyCode: "VND", exchangeRate: 1,
      description: null,
      costCenterId: null, departmentId: null, projectId: null,
    });

    expect(batch.status).toBe(JournalEntryStatus.Draft);
    batch.submit();
    expect(batch.status).toBe(JournalEntryStatus.Submitted);
    batch.approve("user-1");
    expect(batch.status).toBe(JournalEntryStatus.Approved);
    expect(batch.approvedById).toBe("user-1");
    batch.post("user-2");
    expect(batch.status).toBe(JournalEntryStatus.Posted);
    expect(batch.postedById).toBe("user-2");
  });

  it("generates post event", () => {
    const batch = JournalBatch.create(validParams);
    batch.addLine({
      accountId: "a1",
      debitAmount: 100, creditAmount: 0,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
      currencyCode: "VND", exchangeRate: 1,
      description: null,
      costCenterId: null, departmentId: null, projectId: null,
    });
    batch.addLine({
      accountId: "a2",
      debitAmount: 0, creditAmount: 100,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
      currencyCode: "VND", exchangeRate: 1,
      description: null,
      costCenterId: null, departmentId: null, projectId: null,
    });
    batch.submit();
    batch.approve("u1");
    batch.post("u2");
    const events = batch.clearEvents();
    expect(events.some(e => e.eventName === "JournalBatchPosted")).toBe(true);
  });

  it("rejects posting without approval", () => {
    const batch = JournalBatch.create(validParams);
    expect(() => batch.post("user")).toThrow("Only approved batches can be posted");
  });

  it("prevents modifying posted batch", () => {
    const batch = JournalBatch.create(validParams);
    batch.addLine({
      accountId: "a1",
      debitAmount: 100, creditAmount: 0,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
      currencyCode: "VND", exchangeRate: 1,
      description: null,
      costCenterId: null, departmentId: null, projectId: null,
    });
    batch.addLine({
      accountId: "a2",
      debitAmount: 0, creditAmount: 100,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
      currencyCode: "VND", exchangeRate: 1,
      description: null,
      costCenterId: null, departmentId: null, projectId: null,
    });
    batch.submit();
    batch.approve("u1");
    batch.post("u2");
    expect(() => batch.addLine({
      accountId: "a3",
      debitAmount: 50, creditAmount: 0,
      foreignDebitAmount: 0, foreignCreditAmount: 0,
      currencyCode: "VND", exchangeRate: 1,
      description: null,
      costCenterId: null, departmentId: null, projectId: null,
    })).toThrow("Cannot modify");
  });
});
