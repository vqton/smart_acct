import { describe, it, expect } from "vitest";
import {
  TaxAuthority, TaxRegion, JurisdictionLevel, TaxRegionType,
} from "../tax-jurisdiction.js";

describe("TaxAuthority", () => {
  it("creates national tax authority", () => {
    const a = new TaxAuthority("GDT", "General Department of Taxation", "GDT-001", JurisdictionLevel.National);
    const s = a.toState();
    expect(s.code).toBe("GDT");
    expect(s.jurisdictionLevel).toBe(JurisdictionLevel.National);
  });

  it("loads from state", () => {
    const a = new TaxAuthority("HCMC", "Ho Chi Minh City Tax Department", "HCMC-01", JurisdictionLevel.Provincial);
    const state = a.toState();
    const loaded = TaxAuthority.load(state);
    expect(loaded.toState()).toEqual(state);
  });
});

describe("TaxRegion", () => {
  it("creates economic zone", () => {
    const r = new TaxRegion("EZ-HCMC", "HCMC Hi-Tech Park", TaxRegionType.EconomicZone, "VN");
    const s = r.toState();
    expect(s.code).toBe("EZ-HCMC");
    expect(s.regionType).toBe(TaxRegionType.EconomicZone);
  });

  it("loads from state", () => {
    const r = new TaxRegion("DT-DA", "Da Nang Industrial Zone", TaxRegionType.IndustrialZone, "VN");
    const state = r.toState();
    const loaded = TaxRegion.load(state);
    expect(loaded.toState()).toEqual(state);
  });
});

describe("TaxJurisdiction", () => {
  it("creates authority and region combo", () => {
    const a = new TaxAuthority("HN", "Hanoi Tax", "HN-01", JurisdictionLevel.Provincial);
    const r = new TaxRegion("IZ-HN", "Hanoi Industrial Zone", TaxRegionType.IndustrialZone, "VN");
    expect(a.code).toBe("HN");
    expect(r.code).toBe("IZ-HN");
  });
});
