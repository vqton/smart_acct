import { describe, it, expect } from "vitest";
import {
  ErrorCatalogue, ErrorSeverity, ErrorCategory,
  getError, createPostingError, PostingError,
} from "../errors/error-catalogue.js";

describe("ErrorCatalogue", () => {
  it("contains all expected error codes", () => {
    const codes = Object.keys(ErrorCatalogue);
    expect(codes).toContain("AUTH_001");
    expect(codes).toContain("ACC_001");
    expect(codes).toContain("FIS_001");
    expect(codes).toContain("CUR_001");
    expect(codes).toContain("DIM_001");
    expect(codes).toContain("BUD_001");
    expect(codes).toContain("CON_001");
    expect(codes).toContain("SEC_001");
    expect(codes).toContain("INF_001");
    expect(codes.length).toBeGreaterThan(30);
  });

  it("getError returns definition for known codes", () => {
    const def = getError("ACC_001");
    expect(def.code).toBe("ACC_001");
    expect(def.httpStatus).toBe(422);
    expect(def.severity).toBe(ErrorSeverity.Error);
    expect(def.category).toBe(ErrorCategory.Accounting);
    expect(def.retryable).toBe(false);
  });

  it("getError returns unknown error for undefined codes", () => {
    const def = getError("NONEXISTENT");
    expect(def.code).toBe("UNKNOWN");
    expect(def.httpStatus).toBe(500);
  });

  it("createPostingError interpolates message parameters", () => {
    const err = createPostingError("ACC_001", { totalDebit: 100, totalCredit: 200 });
    expect(err.message).toContain("100");
    expect(err.message).toContain("200");
    expect(err.code).toBe("ACC_001");
    expect(err.category).toBe(ErrorCategory.Accounting);
    expect(err.httpStatus).toBe(422);
    expect(err.retryable).toBe(false);
  });

  it("createPostingError produces error with timestamp", () => {
    const err = createPostingError("FIS_001", { periodName: "Tháng 1" });
    expect(err).toBeInstanceOf(PostingError);
    expect(err.timestamp).toBeInstanceOf(Date);
    expect(err.message).toContain("Tháng 1");
  });

  it("PostingError toJSON includes all fields", () => {
    const err = new PostingError("TEST_001", "Test error", ErrorCategory.System, 500, true, { key: "val" });
    const json = err.toJSON();
    expect(json.code).toBe("TEST_001");
    expect(json.retryable).toBe(true);
    expect(json.details).toEqual({ key: "val" });
  });

  it("concurrency errors are retryable", () => {
    expect(ErrorCatalogue["CON_001"].retryable).toBe(true);
    expect(ErrorCatalogue["CON_002"].retryable).toBe(true);
    expect(ErrorCatalogue["CON_003"].retryable).toBe(true);
  });

  it("infrastructure errors are critical severity", () => {
    expect(ErrorCatalogue["INF_001"].severity).toBe(ErrorSeverity.Critical);
    expect(ErrorCatalogue["INF_002"].severity).toBe(ErrorSeverity.Critical);
  });
});
