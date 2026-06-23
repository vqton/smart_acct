import { describe, it, expect } from "vitest";
import { ChequeBook, Cheque } from "../cm-cheque.js";
import { ChequeBookStatus, ChequeStatus } from "../cm-enums.js";

describe("ChequeBook", () => {
  it("creates cheque book", () => {
    const cb = ChequeBook.create({ bankAccountId: "ba1", chequeBookNumber: "CB001", startNumber: 1, endNumber: 50, issuedDate: new Date() });
    expect(cb.chequeBookNumber).toBe("CB001");
    expect(cb.currentNumber).toBe(1);
  });

  it("reserves next cheque", () => {
    const cb = ChequeBook.create({ bankAccountId: "ba1", chequeBookNumber: "CB001", startNumber: 1, endNumber: 5, issuedDate: new Date() });
    const ch1 = cb.reserveNext();
    expect(ch1.chequeNumber).toBe(1);
    expect(cb.currentNumber).toBe(2);
    const ch2 = cb.reserveNext();
    expect(ch2.chequeNumber).toBe(2);
  });

  it("marks full used when all cheques gone", () => {
    const cb = ChequeBook.create({ bankAccountId: "ba1", chequeBookNumber: "CB001", startNumber: 1, endNumber: 2, issuedDate: new Date() });
    cb.reserveNext();
    cb.reserveNext();
    expect(() => cb.reserveNext()).toThrow("have been used");
    expect(cb.status).toBe(ChequeBookStatus.FullUsed);
  });
});

describe("Cheque", () => {
  it("issues cheque", () => {
    const cb = ChequeBook.create({ bankAccountId: "ba1", chequeBookNumber: "CB001", startNumber: 1, endNumber: 50, issuedDate: new Date() });
    const ch = cb.reserveNext();
    ch.issue(1000000, "Vendor X", new Date());
    expect(ch.status).toBe(ChequeStatus.Issued);
    expect(ch.payeeName).toBe("Vendor X");
    expect(ch.amount).toBe(1000000);
  });

  it("rejects double issue", () => {
    const cb = ChequeBook.create({ bankAccountId: "ba1", chequeBookNumber: "CB001", startNumber: 1, endNumber: 50, issuedDate: new Date() });
    const ch = cb.reserveNext();
    ch.issue(1000000, "Vendor X", new Date());
    expect(() => ch.issue(500000, "Vendor Y", new Date())).toThrow("already issued");
  });

  it("deposits and clears", () => {
    const cb = ChequeBook.create({ bankAccountId: "ba1", chequeBookNumber: "CB001", startNumber: 1, endNumber: 50, issuedDate: new Date() });
    const ch = cb.reserveNext();
    ch.issue(1000000, "Vendor X", new Date());
    ch.deposit(new Date());
    expect(ch.status).toBe(ChequeStatus.Deposited);
    ch.clear(new Date());
    expect(ch.status).toBe(ChequeStatus.Cleared);
  });

  it("returns cheque", () => {
    const cb = ChequeBook.create({ bankAccountId: "ba1", chequeBookNumber: "CB001", startNumber: 1, endNumber: 50, issuedDate: new Date() });
    const ch = cb.reserveNext();
    ch.issue(1000000, "Vendor X", new Date());
    ch.deposit(new Date());
    ch.returnCheque(new Date(), "insufficient funds");
    expect(ch.status).toBe(ChequeStatus.Returned);
  });

  it("stops cheque", () => {
    const cb = ChequeBook.create({ bankAccountId: "ba1", chequeBookNumber: "CB001", startNumber: 1, endNumber: 50, issuedDate: new Date() });
    const ch = cb.reserveNext();
    ch.issue(500000, "Vendor X", new Date());
    ch.stop("lost cheque");
    expect(ch.status).toBe(ChequeStatus.Stopped);
  });

  it("voids unissued cheque", () => {
    const cb = ChequeBook.create({ bankAccountId: "ba1", chequeBookNumber: "CB001", startNumber: 1, endNumber: 50, issuedDate: new Date() });
    const ch = cb.reserveNext();
    ch.voidCheque("cancelled");
    expect(ch.status).toBe(ChequeStatus.Voided);
  });
});
