import { describe, it, expect } from "vitest";
import { Vendor } from "../purchasing-vendor.js";
import { VendorStatus, VendorType } from "../purchasing-enums.js";

describe("Vendor", () => {
  it("creates a vendor", () => {
    const v = Vendor.create({ code: "V001", name: "Test Supplier", country: "VN" });
    expect(v.code).toBe("V001");
    expect(v.name).toBe("Test Supplier");
    expect(v.isActive).toBe(true);
    expect(v.status).toBe(VendorStatus.active);
  });

  it("blocks and unblocks vendor", () => {
    const v = Vendor.create({ code: "V002", name: "Block Test", country: "VN" });
    v.block("Non-compliance");
    expect(v.status).toBe(VendorStatus.blocked);
    v.unblock();
    expect(v.status).toBe(VendorStatus.active);
  });

  it("rejects double block", () => {
    const v = Vendor.create({ code: "V003", name: "Double Block", country: "VN" });
    v.block("test");
    expect(() => v.block("again")).toThrow("already blocked");
  });

  it("rejects unblock of non-blocked vendor", () => {
    const v = Vendor.create({ code: "V004", name: "Not Blocked", country: "VN" });
    expect(() => v.unblock()).toThrow("not blocked");
  });

  it("deactivates vendor", () => {
    const v = Vendor.create({ code: "V005", name: "Deactivate", country: "VN" });
    v.deactivate();
    expect(v.isActive).toBe(false);
    expect(v.status).toBe(VendorStatus.inactive);
  });

  it("rejects double deactivate", () => {
    const v = Vendor.create({ code: "V006", name: "Double Deact", country: "VN" });
    v.deactivate();
    expect(() => v.deactivate()).toThrow("already inactive");
  });

  it("round-trips through toState/load", () => {
    const v = Vendor.create({ code: "V007", name: "Roundtrip", country: "VN", email: "test@test.com" });
    const state = v.toState();
    const loaded = Vendor.load(state);
    expect(loaded.code).toBe("V007");
    expect(loaded.name).toBe("Roundtrip");
    expect(loaded.email).toBe("test@test.com");
  });

  it("updates vendor fields", () => {
    const v = Vendor.create({ code: "V008", name: "Original", country: "VN" });
    v.update({ name: "Updated", email: "new@email.com" });
    expect(v.name).toBe("Updated");
    expect(v.email).toBe("new@email.com");
  });
});
