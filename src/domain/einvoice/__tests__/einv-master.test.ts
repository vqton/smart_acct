import { describe, it, expect } from "vitest";
import { EinvInvoiceType } from "../einv-master.js";
import { EinvTemplate } from "../einv-master.js";
import { EinvSeries } from "../einv-master.js";
import { EinvProvider } from "../einv-master.js";
import { EinvDigitalCertificate } from "../einv-master.js";
import { EinvInvoiceCategory, EinvProviderType, EinvCertStatus } from "../einv-enums.js";

describe("EinvInvoiceType", () => {
  it("creates with category", () => {
    const t = EinvInvoiceType.create({ code: "01GTKT", name: "Hóa đơn GTGT", category: EinvInvoiceCategory.sales });
    expect(t.code).toBe("01GTKT");
    expect(t.category).toBe(EinvInvoiceCategory.sales);
  });
  it("deactivates", () => {
    const t = EinvInvoiceType.create({ code: "02GTTT", name: "Hóa đơn bán hàng", category: EinvInvoiceCategory.sales });
    t.deactivate();
    expect(t.isActive).toBe(false);
  });
  it("round-trips", () => {
    const t = EinvInvoiceType.create({ code: "01GTKT", name: "GTGT", category: EinvInvoiceCategory.sales });
    const state = t.toState();
    const loaded = EinvInvoiceType.load(state);
    expect(loaded.code).toBe("01GTKT");
  });
});

describe("EinvTemplate", () => {
  it("creates with defaults", () => {
    const t = EinvTemplate.create({ code: "TEMPLATE01", name: "Mẫu số 1" });
    expect(t.isDefault).toBe(false);
    expect(t.isActive).toBe(true);
  });
  it("deactivates", () => {
    const t = EinvTemplate.create({ code: "T02", name: "Mẫu 2" });
    t.deactivate();
    expect(t.isActive).toBe(false);
  });
  it("round-trips", () => {
    const t = EinvTemplate.create({ code: "T01", name: "Template" });
    expect(EinvTemplate.load(t.toState()).code).toBe("T01");
  });
});

describe("EinvSeries", () => {
  const valid = { code: "AA24E", name: "Series A", invoiceTypeId: "type-1", prefix: "AA/24E", validFrom: new Date("2024-01-01") };

  it("creates and reserves number", () => {
    const s = EinvSeries.create(valid);
    const num = s.reserveNextNumber();
    expect(num).toContain("AA/24E");
    expect(s.nextNumber).toBe(2);
  });

  it("rejects reserve on inactive series", () => {
    const s = EinvSeries.create(valid);
    s.deactivate();
    expect(() => s.reserveNextNumber()).toThrow("Series is inactive");
  });

  it("pads number to min digits", () => {
    const s = EinvSeries.create({ ...valid, prefix: "AA/", minDigits: 7 });
    const num = s.reserveNextNumber();
    expect(num).toBe("AA/0000001");
  });

  it("round-trips", () => {
    const s = EinvSeries.create(valid);
    const state = s.toState();
    const loaded = EinvSeries.load(state);
    expect(loaded.code).toBe("AA24E");
  });
});

describe("EinvProvider", () => {
  it("creates with API config", () => {
    const p = EinvProvider.create({
      code: "VNPT", name: "VNPT Invoice", providerType: EinvProviderType.vnpt,
      apiEndpoint: "https://api.vnpt-invoice.vn", apiVersion: "1.0",
    });
    expect(p.providerType).toBe(EinvProviderType.vnpt);
    expect(p.isActive).toBe(true);
  });
  it("round-trips", () => {
    const p = EinvProvider.create({
      code: "VTT", name: "Viettel", providerType: EinvProviderType.viettel,
      apiEndpoint: "https://api.viettel.vn", apiVersion: "2.0",
    });
    expect(EinvProvider.load(p.toState()).code).toBe("VTT");
  });
});

describe("EinvDigitalCertificate", () => {
  const valid = {
    serialNumber: "SN001", subjectDN: "CN=Company", issuerDN: "CN=CA",
    issuedTo: "Company ABC", issuedBy: "CA Provider",
    validFrom: new Date("2024-01-01"), validTo: new Date("2025-01-01"),
    thumbprint: "THUMB001", providerId: "prov-1",
  };

  it("creates as active", () => {
    const c = EinvDigitalCertificate.create(valid);
    expect(c.status).toBe(EinvCertStatus.active);
    expect(c.serialNumber).toBe("SN001");
  });

  it("revokes", () => {
    const c = EinvDigitalCertificate.create(valid);
    c.revoke();
    expect(c.status).toBe(EinvCertStatus.revoked);
  });

  it("rejects double revoke", () => {
    const c = EinvDigitalCertificate.create(valid);
    c.revoke();
    expect(() => c.revoke()).toThrow("already revoked");
  });

  it("round-trips", () => {
    const c = EinvDigitalCertificate.create(valid);
    const state = c.toState();
    const loaded = EinvDigitalCertificate.load(state);
    expect(loaded.serialNumber).toBe("SN001");
    expect(loaded.status).toBe(EinvCertStatus.active);
  });
});
