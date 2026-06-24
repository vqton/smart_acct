import { describe, it, expect } from "vitest";
import { BankGroup, Bank, BankBranch, CorrespondentBank } from "../bank-master.js";
import { BankGroupType, CorrespondentType } from "../bank-enums.js";

describe("BankGroup", () => {
  it("creates a bank group", () => {
    const g = BankGroup.create({ code: "CM", name: "Commercial Banks", groupType: BankGroupType.Commercial });
    expect(g.code).toBe("CM");
    expect(g.name).toBe("Commercial Banks");
    expect(g.groupType).toBe(BankGroupType.Commercial);
    expect(g.isActive).toBe(true);
  });

  it("deactivates bank group", () => {
    const g = BankGroup.create({ code: "CB", name: "Central Bank", groupType: BankGroupType.Central });
    g.deactivate();
    expect(g.isActive).toBe(false);
  });

  it("rejects double deactivate", () => {
    const g = BankGroup.create({ code: "GV", name: "Government", groupType: BankGroupType.Government });
    g.deactivate();
    expect(() => g.deactivate()).toThrow("already inactive");
  });

  it("round-trips through toState/load", () => {
    const g = BankGroup.create({ code: "FB", name: "Foreign Bank", nameEn: "Foreign Bank", groupType: BankGroupType.Foreign });
    const state = g.toState();
    const loaded = BankGroup.load(state);
    expect(loaded.code).toBe("FB");
    expect(loaded.name).toBe("Foreign Bank");
    expect(loaded.groupType).toBe(BankGroupType.Foreign);
  });
});

describe("Bank", () => {
  it("creates a bank", () => {
    const b = Bank.create({ code: "VCB", name: "Vietcombank", countryCode: "VN", swiftCode: "VCBVVNVX" });
    expect(b.code).toBe("VCB");
    expect(b.swiftCode).toBe("VCBVVNVX");
    expect(b.countryCode).toBe("VN");
    expect(b.isActive).toBe(true);
  });

  it("updates bank fields", () => {
    const b = Bank.create({ code: "CTG", name: "VietinBank", countryCode: "VN" });
    b.update({ name: "VietinBank Updated", address: "108 Tran Hung Dao" });
    expect(b.name).toBe("VietinBank Updated");
  });

  it("deactivates and reactivates", () => {
    const b = Bank.create({ code: "BIDV", name: "BIDV", countryCode: "VN" });
    b.deactivate();
    expect(b.isActive).toBe(false);
    b.activate();
    expect(b.isActive).toBe(true);
  });

  it("rejects double deactivate", () => {
    const b = Bank.create({ code: "AGR", name: "Agribank", countryCode: "VN" });
    b.deactivate();
    expect(() => b.deactivate()).toThrow("already inactive");
  });

  it("rejects double activate", () => {
    const b = Bank.create({ code: "TCB", name: "Techcombank", countryCode: "VN" });
    expect(() => b.activate()).toThrow("already active");
  });

  it("round-trips through toState/load", () => {
    const b = Bank.create({ code: "VPB", name: "VPBank", countryCode: "VN", swiftCode: "VPBVVNVX" });
    const state = b.toState();
    const loaded = Bank.load(state);
    expect(loaded.code).toBe("VPB");
    expect(loaded.swiftCode).toBe("VPBVVNVX");
  });
});

describe("BankBranch", () => {
  it("creates a branch", () => {
    const br = BankBranch.create({ bankId: "bank1", code: "HCMC", name: "Ho Chi Minh Branch" });
    expect(br.code).toBe("HCMC");
    expect(br.bankId).toBe("bank1");
    expect(br.isActive).toBe(true);
  });

  it("deactivates branch", () => {
    const br = BankBranch.create({ bankId: "bank1", code: "HN", name: "Hanoi Branch" });
    br.deactivate();
    expect(br.isActive).toBe(false);
  });

  it("rejects double deactivate", () => {
    const br = BankBranch.create({ bankId: "bank1", code: "DN", name: "Da Nang Branch" });
    br.deactivate();
    expect(() => br.deactivate()).toThrow("already inactive");
  });
});

describe("CorrespondentBank", () => {
  it("creates correspondent relationship", () => {
    const c = CorrespondentBank.create({
      bankId: "bank1", correspondentBankId: "bank2",
      correspondentType: CorrespondentType.Vostro, currencyCode: "USD",
    });
    expect(c.correspondentType).toBe(CorrespondentType.Vostro);
    expect(c.currencyCode).toBe("USD");
    expect(c.isActive).toBe(true);
  });

  it("creates with account number", () => {
    const c = CorrespondentBank.create({
      bankId: "bank1", correspondentBankId: "bank2",
      accountNumber: "123456789", correspondentType: CorrespondentType.Nostro, currencyCode: "EUR",
    });
    expect(c.isActive).toBe(true);
  });
});
