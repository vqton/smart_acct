import "dotenv/config";
import { PrismaClient } from "../src/generated/prisma/client.js";
import { PrismaMariaDb } from "@prisma/adapter-mariadb";

const adapter = new PrismaMariaDb({
  host: process.env.DB_HOST ?? "127.0.0.1",
  port: parseInt(process.env.DB_PORT ?? "3306", 10),
  user: process.env.DB_USER ?? "dev",
  password: process.env.DB_PASSWORD ?? "123456",
  database: process.env.DB_NAME ?? "smart_acct_dev",
});

const prisma = new PrismaClient({ adapter });

const now = new Date();
const uuid = () => crypto.randomUUID();

async function seedAccountClasses() {
  const classes = [
    { id: uuid(), code: "1", name: "Tài sản", classType: "asset" as const, displayOrder: 1 },
    { id: uuid(), code: "2", name: "Nợ phải trả", classType: "liability" as const, displayOrder: 2 },
    { id: uuid(), code: "3", name: "Vốn chủ sở hữu", classType: "equity" as const, displayOrder: 3 },
    { id: uuid(), code: "4", name: "Doanh thu", classType: "revenue" as const, displayOrder: 4 },
    { id: uuid(), code: "5", name: "Chi phí SXKD", classType: "expense" as const, displayOrder: 5 },
    { id: uuid(), code: "6", name: "Chi phí bán hàng", classType: "cost_of_goods_sold" as const, displayOrder: 6 },
    { id: uuid(), code: "7", name: "Thu nhập khác", classType: "other_income" as const, displayOrder: 7 },
    { id: uuid(), code: "8", name: "Chi phí khác", classType: "other_expense" as const, displayOrder: 8 },
    { id: uuid(), code: "9", name: "Xác định KQKD", classType: "manufacturing" as const, displayOrder: 9 },
  ];
  for (const c of classes) {
    await prisma.accountClass.upsert({
      where: { code: c.code },
      update: {},
      create: { ...c, nameEn: null, description: null, createdAt: now, updatedAt: now },
    });
  }
  return classes;
}

async function seedAccountTypes(classMap: Record<string, string>) {
  const types = [
    { code: "11", name: "Tiền và tương đương tiền", category: "current_asset" as const, n: "debit" as const, sub: "cash" as const, cc: "1" },
    { code: "12", name: "Đầu tư tài chính ngắn hạn", category: "current_asset" as const, n: "debit" as const, sub: "investment" as const, cc: "1" },
    { code: "13", name: "Phải thu ngắn hạn", category: "current_asset" as const, n: "debit" as const, sub: "receivable" as const, cc: "1" },
    { code: "14", name: "Hàng tồn kho", category: "current_asset" as const, n: "debit" as const, sub: "inventory" as const, cc: "1" },
    { code: "15", name: "Thanh toán nội bộ", category: "current_asset" as const, n: "debit" as const, sub: "receivable" as const, cc: "1" },
    { code: "21", name: "TSCĐ hữu hình", category: "non_current_asset" as const, n: "debit" as const, sub: "fixed_asset" as const, cc: "2" },
    { code: "22", name: "TSCĐ vô hình", category: "non_current_asset" as const, n: "debit" as const, sub: "intangible_asset" as const, cc: "2" },
    { code: "24", name: "Đầu tư tài chính dài hạn", category: "non_current_asset" as const, n: "debit" as const, sub: "investment" as const, cc: "2" },
    { code: "31", name: "Phải trả người bán", category: "current_liability" as const, n: "credit" as const, sub: "payable" as const, cc: "3" },
    { code: "33", name: "Thuế phải nộp NN", category: "current_liability" as const, n: "credit" as const, sub: "tax_payable" as const, cc: "3" },
    { code: "34", name: "Phải trả người lao động", category: "current_liability" as const, n: "credit" as const, sub: "payable" as const, cc: "3" },
    { code: "41", name: "Vốn đầu tư CSH", category: "equity" as const, n: "credit" as const, sub: "equity_capital" as const, cc: "4" },
    { code: "42", name: "Thặng dư vốn cổ phần", category: "equity" as const, n: "credit" as const, sub: "equity_capital" as const, cc: "4" },
    { code: "51", name: "Doanh thu bán hàng", category: "revenue" as const, n: "credit" as const, sub: "revenue" as const, cc: "5" },
    { code: "61", name: "Giá vốn hàng bán", category: "cost_of_goods_sold" as const, n: "debit" as const, sub: "cost_of_sales" as const, cc: "6" },
  ];

  const result: Record<string, string> = {};
  for (const t of types) {
    const rec = await prisma.accountType.upsert({
      where: { code: t.code },
      update: {},
      create: {
        id: uuid(),
        classId: classMap[t.cc],
        code: t.code,
        name: t.name,
        nameEn: null,
        category: t.category,
        subType: t.sub,
        nature: t.n,
        description: null,
        parentTypeId: null,
        isActive: true,
        displayOrder: 0,
        version: 1,
        createdAt: now,
        updatedAt: now,
      },
    });
    result[t.code] = rec.id;
  }
  return result;
}

async function seedGlAccounts() {
  const accounts: { code: string; name: string; category: string; nature: string; parentCode: string | null }[] = [
    { code: "111", name: "Tiền mặt", category: "short_term_asset", nature: "debit", parentCode: null },
    { code: "1111", name: "Tiền Việt Nam", category: "short_term_asset", nature: "debit", parentCode: "111" },
    { code: "1112", name: "Ngoại tệ", category: "short_term_asset", nature: "debit", parentCode: "111" },
    { code: "112", name: "Tiền gửi ngân hàng", category: "short_term_asset", nature: "debit", parentCode: null },
    { code: "1121", name: "Tiền VN gửi NH", category: "short_term_asset", nature: "debit", parentCode: "112" },
    { code: "1122", name: "Ngoại tệ gửi NH", category: "short_term_asset", nature: "debit", parentCode: "112" },
    { code: "131", name: "Phải thu khách hàng", category: "short_term_asset", nature: "debit", parentCode: null },
    { code: "133", name: "Thuế GTGT được khấu trừ", category: "short_term_asset", nature: "debit", parentCode: null },
    { code: "1331", name: "Thuế GTGT đầu vào", category: "short_term_asset", nature: "debit", parentCode: "133" },
    { code: "141", name: "Tạm ứng", category: "short_term_asset", nature: "debit", parentCode: null },
    { code: "211", name: "TSCĐ hữu hình", category: "long_term_asset", nature: "debit", parentCode: null },
    { code: "214", name: "Hao mòn TSCĐ", category: "long_term_asset", nature: "credit", parentCode: null },
    { code: "2141", name: "Hao mòn TSCĐ hữu hình", category: "long_term_asset", nature: "credit", parentCode: "214" },
    { code: "311", name: "Vay ngắn hạn", category: "short_term_liability", nature: "credit", parentCode: null },
    { code: "331", name: "Phải trả người bán", category: "short_term_liability", nature: "credit", parentCode: null },
    { code: "333", name: "Thuế phải nộp", category: "short_term_liability", nature: "credit", parentCode: null },
    { code: "3331", name: "Thuế GTGT phải nộp", category: "short_term_liability", nature: "credit", parentCode: "333" },
    { code: "334", name: "Phải trả NLĐ", category: "short_term_liability", nature: "credit", parentCode: null },
    { code: "411", name: "Vốn đầu tư CSH", category: "equity", nature: "credit", parentCode: null },
    { code: "421", name: "LNST chưa phân phối", category: "equity", nature: "credit", parentCode: null },
    { code: "511", name: "Doanh thu bán hàng", category: "revenue", nature: "credit", parentCode: null },
    { code: "632", name: "Giá vốn hàng bán", category: "cost_of_goods_sold", nature: "debit", parentCode: null },
    { code: "641", name: "Chi phí bán hàng", category: "operating_expense", nature: "debit", parentCode: null },
    { code: "642", name: "Chi phí QLDN", category: "operating_expense", nature: "debit", parentCode: null },
    { code: "911", name: "Xác định KQKD", category: "manufacturing_cost", nature: "debit", parentCode: null },
  ];

  const result: Record<string, string> = {};
  for (const a of accounts) {
    const rec = await prisma.account.upsert({
      where: { code: a.code },
      update: {},
      create: {
        id: uuid(),
        code: a.code,
        name: a.name,
        nameEn: null,
        category: a.category as any,
        nature: a.nature as any,
        parentId: a.parentCode ? (result[a.parentCode] ?? null) : null,
        isActive: true,
        isControl: a.code.length === 3,
        isPosting: a.code.length > 3,
        allowManualEntry: true,
        balance: 0n,
        foreignBalance: 0n,
        currencyCode: null,
        description: null,
        version: 1,
        createdAt: now,
        updatedAt: now,
      },
    });
    result[a.code] = rec.id;
  }
  return result;
}

async function seedFiscalYear() {
  const fy = await prisma.fiscalYear.upsert({
    where: { code: "FY2026" },
    update: {},
    create: {
      id: uuid(),
      code: "FY2026",
      name: "Năm tài chính 2026",
      startDate: new Date("2026-01-01T00:00:00Z"),
      endDate: new Date("2026-12-31T23:59:59Z"),
      isActive: true,
      isClosed: false,
      version: 1,
      createdAt: now,
      updatedAt: now,
    },
  });
  return fy;
}

async function seedPeriods(fiscalYearId: string) {
  const monthNames = [
    "Tháng 1","Tháng 2","Tháng 3","Tháng 4","Tháng 5","Tháng 6",
    "Tháng 7","Tháng 8","Tháng 9","Tháng 10","Tháng 11","Tháng 12",
  ];
  for (let i = 0; i < 12; i++) {
    const m = String(i + 1).padStart(2, "0");
    const endDay = i === 11 ? "12-31" : `${String(i + 2).padStart(2, "0")}-01`;
    await prisma.period.upsert({
      where: { fiscalYearId_periodNumber: { fiscalYearId, periodNumber: i + 1 } },
      update: {},
      create: {
        id: uuid(),
        fiscalYearId,
        periodNumber: i + 1,
        name: monthNames[i],
        startDate: new Date(`2026-${m}-01T00:00:00Z`),
        endDate: new Date(`2026-${endDay}T23:59:59Z`),
        status: "open",
        version: 1,
        createdAt: now,
        updatedAt: now,
      },
    });
  }
}

async function seedVoucherTypes() {
  const types = [
    { code: "PT", name: "Phiếu thu", cat: "receipt" as const },
    { code: "PC", name: "Phiếu chi", cat: "payment" as const },
    { code: "PKT", name: "Phiếu kế toán", cat: "journal" as const },
    { code: "HDGTGT", name: "Hóa đơn GTGT", cat: "sales" as const },
    { code: "HDMH", name: "Hóa đơn mua hàng", cat: "purchase" as const },
  ];
  const result: Record<string, string> = {};
  for (const t of types) {
    const rec = await prisma.voucherType.upsert({
      where: { code: t.code },
      update: {},
      create: {
        id: uuid(), code: t.code, name: t.name, category: t.cat,
        requiresApproval: true, requiresAttachment: false, isActive: true,
        version: 1, createdAt: now, updatedAt: now,
      },
    });
    result[t.code] = rec.id;
  }
  return result;
}

async function seedVoucherSeries(voucherTypeIds: Record<string, string>) {
  for (const [code, typeId] of Object.entries(voucherTypeIds)) {
    const seriesCode = `${code}-2026`;
    await prisma.voucherSeries.upsert({
      where: { code: seriesCode },
      update: {},
      create: {
        id: uuid(), voucherTypeId: typeId, code: seriesCode,
        name: `Số ${code} năm 2026`, prefix: code, suffix: "/26",
        currentNumber: 0, nextNumber: 1, minDigits: 6,
        sequenceMethod: "annual", isActive: true,
        version: 1, createdAt: now, updatedAt: now,
      },
    });
  }
}

async function seedTaxTypes() {
  const types = [
    { code: "GTGT", name: "Thuế GTGT", nature: "indirect", cat: "value_added_tax", basis: "consumption", calc: "deduction", pay: "monthly", freq: "monthly" },
    { code: "TNDN", name: "Thuế TNDN", nature: "direct", cat: "corporate_income_tax", basis: "profit", calc: "direct", pay: "quarterly", freq: "quarterly" },
    { code: "TNCN", name: "Thuế TNCN", nature: "direct", cat: "personal_income_tax", basis: "salary", calc: "withholding", pay: "withholding", freq: "monthly" },
    { code: "MB", name: "Thuế môn bài", nature: "direct", cat: "license_tax", basis: "other", calc: "direct", pay: "annual", freq: "annual" },
  ];
  const result: Record<string, string> = {};
  for (const t of types) {
    const rec = await prisma.taxType.upsert({
      where: { code: t.code },
      update: {},
      create: {
        id: uuid(), code: t.code, name: t.name, nameEn: null,
        nature: t.nature as any, category: t.cat as any, basis: t.basis as any,
        calculationMethod: t.calc as any, paymentMethod: t.pay as any,
        filingFrequency: t.freq as any,
        parentTaxTypeId: null, isActive: true, description: null,
        version: 1, createdAt: now, updatedAt: now,
      },
    });
    result[t.code] = rec.id;
  }
  return result;
}

async function seedTaxCodes(taxTypeIds: Record<string, string>) {
  const codes = [
    { code: "VAT0", name: "Thuế GTGT 0%", tt: "GTGT", recov: false, app: "both" as const },
    { code: "VAT5", name: "Thuế GTGT 5%", tt: "GTGT", recov: true, app: "both" as const },
    { code: "VAT8", name: "Thuế GTGT 8%", tt: "GTGT", recov: true, app: "both" as const },
    { code: "VAT10", name: "Thuế GTGT 10%", tt: "GTGT", recov: true, app: "both" as const },
    { code: "CIT20", name: "Thuế TNDN 20%", tt: "TNDN", recov: false, app: "sales" as const },
    { code: "PIT", name: "Thuế TNCN", tt: "TNCN", recov: false, app: "sales" as const },
    { code: "LT", name: "Lệ phí môn bài", tt: "MB", recov: false, app: "sales" as const },
  ];
  for (const c of codes) {
    await prisma.taxCode.upsert({
      where: { code: c.code },
      update: {},
      create: {
        id: uuid(), taxTypeId: taxTypeIds[c.tt],
        code: c.code, name: c.name,
        taxRateType: "percentage", application: c.app,
        roundingMethod: "half_up", precision: 2,
        isRecoverable: c.recov, isRefundable: false, isDeductible: c.recov,
        effectiveFrom: new Date("2026-01-01T00:00:00Z"), effectiveTo: null,
        description: null, isActive: true,
        version: 1, createdAt: now, updatedAt: now,
      },
    });
  }
}

async function seedBankGroups() {
  const groups = [
    { code: "NHNN", name: "Ngân hàng Nhà nước", type: "central" as const },
    { code: "NHTMNN", name: "Ngân hàng TM Nhà nước", type: "government" as const },
    { code: "NHTMCP", name: "Ngân hàng TM cổ phần", type: "commercial" as const },
    { code: "NHNNg", name: "Ngân hàng nước ngoài", type: "foreign" as const },
    { code: "NHLD", name: "Ngân hàng liên doanh", type: "joint_venture" as const },
    { code: "QTD", name: "Quỹ tín dụng ND", type: "cooperative" as const },
  ];
  const result: Record<string, string> = {};
  for (const g of groups) {
    const rec = await prisma.bnkGroup.upsert({
      where: { code: g.code },
      update: {},
      create: {
        id: uuid(), code: g.code, name: g.name, groupType: g.type,
        nameEn: null, isActive: true,
        version: 1, createdAt: now, updatedAt: now,
      },
    });
    result[g.code] = rec.id;
  }
  return result;
}

async function seedBanks(bankGroupIds: Record<string, string>) {
  const banks = [
    { code: "VB", name: "Vietcombank", swift: "BFTVVNVX", grp: "NHTMCP" },
    { code: "CT", name: "VietinBank", swift: "ICBVVNVX", grp: "NHTMNN" },
    { code: "TCB", name: "Techcombank", swift: "VTCBVNVX", grp: "NHTMCP" },
    { code: "AGR", name: "Agribank", swift: "VBAAVNVX", grp: "NHTMNN" },
    { code: "MB", name: "MB Bank", swift: "MSCBVNVX", grp: "NHTMCP" },
    { code: "ACB", name: "ACB", swift: "ASCBVNVX", grp: "NHTMCP" },
    { code: "VPB", name: "VPBank", swift: "VPBKVNVX", grp: "NHTMCP" },
    { code: "HDB", name: "HDBank", swift: "HDBCVNVX", grp: "NHTMCP" },
  ];
  for (const b of banks) {
    await prisma.bnkBank.upsert({
      where: { code: b.code },
      update: {},
      create: {
        id: uuid(), groupId: bankGroupIds[b.grp], code: b.code, name: b.name,
        nameEn: null, shortName: b.code, swiftCode: b.swift,
        routingNumber: null, bankCode: b.code, countryCode: "VN",
        isActive: true, isCorrespondent: false,
        version: 1, createdAt: now, updatedAt: now,
      },
    });
  }
}

async function seedInvUoms() {
  const uoms = [
    { id: uuid(), code: "CAI", name: "Cái", decimalPlaces: 0 },
    { id: uuid(), code: "CHIEC", name: "Chiếc", decimalPlaces: 0 },
    { id: uuid(), code: "HOP", name: "Hộp", decimalPlaces: 0 },
    { id: uuid(), code: "THUNG", name: "Thùng", decimalPlaces: 0 },
    { id: uuid(), code: "KG", name: "Kilogram", decimalPlaces: 2 },
    { id: uuid(), code: "G", name: "Gram", decimalPlaces: 2 },
    { id: uuid(), code: "L", name: "Lít", decimalPlaces: 2 },
    { id: uuid(), code: "M", name: "Mét", decimalPlaces: 2 },
    { id: uuid(), code: "M2", name: "Mét vuông", decimalPlaces: 2 },
    { id: uuid(), code: "M3", name: "Mét khối", decimalPlaces: 2 },
    { id: uuid(), code: "BALE", name: "Bale", decimalPlaces: 0 },
    { id: uuid(), code: "TAN", name: "Tấn", decimalPlaces: 2 },
  ];
  for (const u of uoms) {
    await prisma.invUom.upsert({ where: { code: u.code }, update: {}, create: { ...u, isActive: true, version: 1, createdAt: now, updatedAt: now } });
  }
  const m: Record<string, string> = {};
  uoms.forEach(u => { m[u.code] = u.id; });
  return m;
}

async function seedInvWarehouses() {
  const whs = [
    { id: uuid(), code: "KHO1", name: "Kho chính", type: "main" as const, storageType: "dry" as const },
    { id: uuid(), code: "KHO2", name: "Kho phụ", type: "main" as const, storageType: "dry" as const },
    { id: uuid(), code: "DC1", name: "Trung tâm phân phối 1", type: "distribution_center" as const, storageType: "dry" as const },
    { id: uuid(), code: "STORE1", name: "Kho cửa hàng 1", type: "store" as const, storageType: "dry" as const },
  ];
  const company = await prisma.company.findUnique({ where: { code: "DEFAULT" } });
  for (const w of whs) {
    await prisma.invWarehouse.upsert({
      where: { code: w.code },
      update: {},
      create: { ...w, companyId: company!.id, status: "active", isActive: true, country: "VN", allowNegative: false, version: 1, createdAt: now, updatedAt: now },
    });
  }
  const m: Record<string, string> = {};
  whs.forEach(w => { m[w.code] = w.id; });
  return m;
}

async function seedCompany() {
  await prisma.company.upsert({
    where: { code: "DEFAULT" },
    update: {},
    create: {
      id: uuid(), code: "DEFAULT", name: "Công ty TNHH Mặc định",
      nameEn: "Default Company Ltd.", taxCode: "0000000000",
      address: null, phone: null, email: null,
      isActive: true, version: 1, createdAt: now, updatedAt: now,
    },
  });
}

async function main() {
  console.log("Seeding database...");

  await seedCompany();
  console.log("  Company ✓");

  const cmap: Record<string, string> = {};
  (await seedAccountClasses()).forEach(c => { cmap[c.code] = c.id; });
  console.log("  Account classes (9) ✓");

  await seedAccountTypes(cmap);
  console.log("  Account types (15) ✓");

  await seedGlAccounts();
  console.log("  GL accounts (25) ✓");

  const fy = await seedFiscalYear();
  console.log("  Fiscal year ✓");

  await seedPeriods(fy.id);
  console.log("  Periods (12) ✓");

  const vt = await seedVoucherTypes();
  console.log("  Voucher types ✓");

  await seedVoucherSeries(vt);
  console.log("  Voucher series ✓");

  const tt = await seedTaxTypes();
  console.log("  Tax types ✓");

  await seedTaxCodes(tt);
  console.log("  Tax codes ✓");

  const bg = await seedBankGroups();
  console.log("  Bank groups ✓");

  await seedBanks(bg);
  console.log("  Banks ✓");

  const uomMap = await seedInvUoms();
  console.log("  Inventory UOMs (12) ✓");

  const whMap = await seedInvWarehouses();
  console.log("  Inventory warehouses (4) ✓");

  console.log("Seed complete");
}

main()
  .catch(e => { console.error("Seed failed:", e); process.exit(1); })
  .finally(() => prisma.$disconnect());
