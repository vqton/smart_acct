import { describe, it, expect } from "vitest";
import {
  TaxRegistration, TaxRegistrationStatus,
} from "../tax-registration.js";
import { DomainError } from "../../../shared/domain-error.js";

describe("TaxRegistration", () => {
  it("creates with pending status", () => {
    const r = TaxRegistration.create({
      taxpayerId: "taxpayer-1", taxTypeId: "vat-1",
      taxAuthorityId: "auth-1", registrationNumber: "REG001",
    });
    expect(r.status).toBe(TaxRegistrationStatus.Pending);
  });

  it("transitions through lifecycle", () => {
    const r = TaxRegistration.create({
      taxpayerId: "taxpayer-1", taxTypeId: "vat-1",
      taxAuthorityId: "auth-1", registrationNumber: "REG002",
    });
    expect(r.status).toBe(TaxRegistrationStatus.Pending);

    r.register("CERT-001");
    expect(r.status).toBe(TaxRegistrationStatus.Registered);
    expect(r.toState().registeredAt).not.toBeNull();

    r.suspend("Late filing");
    expect(r.status).toBe(TaxRegistrationStatus.Suspended);

    r.revoke("Non-compliance");
    expect(r.status).toBe(TaxRegistrationStatus.Revoked);
  });

  it("throws on invalid transition from registered to pending", () => {
    const r = TaxRegistration.create({
      taxpayerId: "tp-1", taxTypeId: "cid",
      taxAuthorityId: "auth-1", registrationNumber: "REG003",
    });
    r.register("CERT-002");
    expect(r.status).toBe(TaxRegistrationStatus.Registered);
  });

  it("loads from state", () => {
    const r = TaxRegistration.create({
      taxpayerId: "tp-1", taxTypeId: "cid", taxAuthorityId: "auth-1",
      registrationNumber: "REG004",
    });
    r.register("CERT-003");
    const state = r.toState();
    const loaded = TaxRegistration.load(state);
    expect(loaded.toState()).toEqual(state);
  });
});
