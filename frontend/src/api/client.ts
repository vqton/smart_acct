import type {
  AccountClass,
  AccountType,
  BankGroup,
  TaxType,
  TaxCode,
  GlAccount,
} from "../types/index.js";

const BASE = "/api";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const RETRY_MAX = 3;
const RETRY_BASE_MS = 500;

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

async function request<T>(path: string, attempt = 1): Promise<T> {
  try {
    const res = await fetch(`${BASE}${path}`);
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new ApiError(res.status, body || res.statusText);
    }
    return res.json() as Promise<T>;
  } catch (err) {
    const isNetworkError =
      err instanceof TypeError &&
      (err.message.includes("fetch") || err.message.includes("NetworkError"));

    if (isNetworkError && attempt < RETRY_MAX) {
      const delay = RETRY_BASE_MS * 2 ** (attempt - 1) + Math.random() * 200;
      await sleep(delay);
      return request<T>(path, attempt + 1);
    }
    throw err;
  }
}

export function getAccountClasses() {
  return request<AccountClass[]>("/coa/classes");
}

export function getAccountTypes() {
  return request<AccountType[]>("/coa/types");
}

export function getBankGroups() {
  return request<BankGroup[]>("/bank/groups");
}

export function getTaxTypes() {
  return request<TaxType[]>("/tax/types");
}

export function getTaxCodes() {
  return request<TaxCode[]>("/tax/codes");
}

export function getGlAccounts() {
  return request<GlAccount[]>("/gl/accounts");
}
