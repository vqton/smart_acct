import { describe, it, expect } from "vitest";
import { EinvTransmission } from "../einv-transmission.js";
import { EinvTransmissionStatus } from "../einv-enums.js";

describe("EinvTransmission", () => {
  it("creates as pending", () => {
    const t = EinvTransmission.create({ invoiceId: "inv-1", providerId: "prov-1" });
    expect(t.status).toBe(EinvTransmissionStatus.pending);
  });

  it("transitions through lifecycle", () => {
    const t = EinvTransmission.create({ invoiceId: "inv-1", providerId: "prov-1" });
    t.markSending();
    expect(t.status).toBe(EinvTransmissionStatus.sending);

    t.markSent("{}");
    expect(t.status).toBe(EinvTransmissionStatus.sent);

    t.markAcknowledged("txn-1", "{}", "200", "Success");
    expect(t.status).toBe(EinvTransmissionStatus.acknowledged);
    expect(t.transmissionId).toBe("txn-1");
  });

  it("retries on failure", () => {
    const t = EinvTransmission.create({ invoiceId: "inv-1", providerId: "prov-1", maxRetries: 3 });
    t.markSending();
    t.markSent("{}");
    t.markFailed("Connection timeout");
    expect(t.status).toBe(EinvTransmissionStatus.retrying);
    expect(t.retryCount).toBe(1);
    expect(t.nextRetryAt).toBeTruthy();
  });

  it("fails after max retries", () => {
    const t = EinvTransmission.create({ invoiceId: "inv-1", providerId: "prov-1", maxRetries: 2 });
    t.markSending(); t.markSent("{}"); t.markFailed("err1");
    expect(t.status).toBe(EinvTransmissionStatus.retrying);
    t.markSending(); t.markSent("{}"); t.markFailed("err2");
    expect(t.status).toBe(EinvTransmissionStatus.failed);
    expect(t.retryCount).toBe(2);
  });

  it("round-trips through toState/load", () => {
    const t = EinvTransmission.create({ invoiceId: "inv-1", providerId: "prov-1" });
    t.markSending(); t.markSent("{}");
    t.markAcknowledged("txn-1", "{}", "200", "OK");
    const state = t.toState();
    const loaded = EinvTransmission.load(state);
    expect(loaded.status).toBe(EinvTransmissionStatus.acknowledged);
    expect(loaded.transmissionId).toBe("txn-1");
  });
});
