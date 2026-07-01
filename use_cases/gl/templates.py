"""TT99/2025 accounting book template generators.

Implements S03a1-DN through S06-DN formats per Phụ lục III TT99/2025.
"""
from typing import Optional, List, Dict
from datetime import date
from decimal import Decimal

from domain import JournalEntry, JournalLine, JournalType, SubsidiaryLedger, AccountType, DCRDirection


VI_MONTH_NAMES = {
    1: "tháng 1", 2: "tháng 2", 3: "tháng 3", 4: "tháng 4",
    5: "tháng 5", 6: "tháng 6", 7: "tháng 7", 8: "tháng 8",
    9: "tháng 9", 10: "tháng 10", 11: "tháng 11", 12: "tháng 12",
}

JOURNAL_TYPE_TEMPLATE_MAP = {
    JournalType.GENERAL: "S03c-DN",
    JournalType.SALES: "S03b2-DN",
    JournalType.PURCHASE: "S03b1-DN",
    JournalType.CASH_RECEIPT: "S03a1-DN",
    JournalType.CASH_PAYMENT: "S03a2-DN",
    JournalType.PAYROLL: "S03c-DN",
    JournalType.INVENTORY: "S11-DN",
    JournalType.FIXED_ASSET: "S12-DN",
    JournalType.ADJUSTMENT: "S03c-DN",
    JournalType.OPENING: "S03c-DN",
    JournalType.CLOSING: "S03c-DN",
}

TEMPLATE_NAMES = {
    "S03c-DN": "SỔ NHẬT KÝ CHUNG",
    "S03a1-DN": "SỔ NHẬT KÝ THU TIỀN",
    "S03a2-DN": "SỔ NHẬT KÝ CHI TIỀN",
    "S03b1-DN": "SỔ NHẬT KÝ MUA HÀNG",
    "S03b2-DN": "SỔ NHẬT KÝ BÁN HÀNG",
    "S07-DN": "SỔ NHẬT KÝ THU TIỀN",
    "S08-DN": "SỔ NHẬT KÝ CHI TIỀN",
    "S09-DN": "SỔ NHẬT KÝ MUA HÀNG",
    "S10-DN": "SỔ NHẬT KÝ BÁN HÀNG",
    "S11-DN": "SỔ NHẬT KÝ KIÊM CHỨNG TỪ GHI SỔ",
    "S12-DN": "SỔ NHẬT KÝ TSCĐ",
    "S01-DN": "SỔ CÁI",
    "S05-DN": "SỔ CHI TIẾT THANH TOÁN VỚI NGƯỜI BÁN",
    "S06-DN": "SỔ CHI TIẾT THANH TOÁN VỚI NGƯỜI MUA",
}

TEMPLATE_NAMES_EN = {
    "S03c-DN": "GENERAL JOURNAL",
    "S03a1-DN": "CASH RECEIPT JOURNAL",
    "S03a2-DN": "CASH DISBURSEMENT JOURNAL",
    "S03b1-DN": "PURCHASE JOURNAL",
    "S03b2-DN": "SALES JOURNAL",
    "S07-DN": "CASH RECEIPT JOURNAL",
    "S08-DN": "CASH DISBURSEMENT JOURNAL",
    "S09-DN": "PURCHASE JOURNAL",
    "S10-DN": "SALES JOURNAL",
    "S11-DN": "COMBINED JOURNAL / VOUCHER",
    "S12-DN": "FIXED ASSET JOURNAL",
    "S01-DN": "GENERAL LEDGER",
    "S05-DN": "ACCOUNTS PAYABLE SUBSIDIARY LEDGER",
    "S06-DN": "ACCOUNTS RECEIVABLE SUBSIDIARY LEDGER",
}


def _fmt_vnd(amount: Decimal) -> str:
    if amount is None or amount == Decimal("0"):
        return "0"
    negative = amount < 0
    n = abs(amount)
    s = f"{n:.2f}"
    int_part, dec_part = s.split(".")
    int_part = ".".join(int_part[::-1][i:i+3] for i in range(0, len(int_part), 3))[::-1]
    result = f"{int_part},{dec_part}"
    return f"-{result}" if negative else result


def _fmt_date(d: date) -> str:
    if not d:
        return ""
    return f"{d.day} {VI_MONTH_NAMES.get(d.month, f'tháng {d.month}')} năm {d.year}"


COUNTERPARTY_LABELS = {
    "S03a1-DN": "Người nộp",
    "S03a2-DN": "Người nhận",
    "S03b1-DN": "Nhà cung cấp",
    "S03b2-DN": "Khách hàng",
    "S07-DN": "Người nộp",
    "S08-DN": "Người nhận",
    "S09-DN": "Nhà cung cấp",
    "S10-DN": "Khách hàng",
    "S11-DN": "Đối tượng",
    "S12-DN": "TSCĐ",
}

COUNTERPARTY_LABELS_EN = {
    "S03a1-DN": "Payer",
    "S03a2-DN": "Receiver",
    "S03b1-DN": "Supplier",
    "S03b2-DN": "Customer",
    "S07-DN": "Payer",
    "S08-DN": "Receiver",
    "S09-DN": "Supplier",
    "S10-DN": "Customer",
    "S11-DN": "Entity",
    "S12-DN": "Fixed Asset",
}


def generate_journal_template(
    template_code: str,
    entries: List[JournalEntry],
    period: str,
    company_name: str = "Công ty",
    address: str = "",
    counterparty: str = "",
) -> dict:
    """Generate journal data in standard TT99 format."""
    year = period.split("-")[0] if "-" in period else period
    month_name = VI_MONTH_NAMES.get(int(period.split("-")[1])) if "-" in period else ""

    rows = []
    debit_total = Decimal("0")
    credit_total = Decimal("0")

    for entry in entries:
        entry_counterparty = counterparty
        for line in entry.lines:
            opposite_accounts = _get_opposite_accounts(entry.lines, line.account_id)
            rows.append({
                "posting_date": _fmt_date(entry.posted_date.date() if entry.posted_date else entry.transaction_date),
                "journal_number": entry.journal_number,
                "description": line.description or entry.description,
                "account_code": line.account_id,
                "opposite_account": ", ".join(sorted(opposite_accounts)) if opposite_accounts else "",
                "debit": _fmt_vnd(line.debit) if line.debit > 0 else "",
                "credit": _fmt_vnd(line.credit) if line.credit > 0 else "",
                "counterparty": entry_counterparty,
            })
            debit_total += line.debit
            credit_total += line.credit

    counterparty_label = COUNTERPARTY_LABELS.get(template_code, "")
    counterparty_label_en = COUNTERPARTY_LABELS_EN.get(template_code, "")

    return {
        "template_code": template_code,
        "template_name": TEMPLATE_NAMES.get(template_code, template_code),
        "template_name_en": TEMPLATE_NAMES_EN.get(template_code, template_code),
        "company_name": company_name,
        "address": address,
        "period": period,
        "year": year,
        "month_name": month_name,
        "rows": rows,
        "debit_total": _fmt_vnd(debit_total),
        "credit_total": _fmt_vnd(credit_total),
        "row_count": len(rows),
        "generated_at": _fmt_date(date.today()),
        "counterparty_label": counterparty_label,
        "counterparty_label_en": counterparty_label_en,
    }


def _get_opposite_accounts(lines: List[JournalLine], account_id: str) -> List[str]:
    return [l.account_id for l in lines if l.account_id != account_id]


def generate_s01_ledger(
    account_code: str,
    account_name: str,
    entries: List[JournalEntry],
    period: str,
    opening_balance: Decimal = Decimal("0"),
    company_name: str = "Công ty",
    address: str = "",
) -> dict:
    """Generate S01-DN General Ledger for a single account."""
    year = period.split("-")[0] if "-" in period else period

    rows = []
    period_debit = Decimal("0")
    period_credit = Decimal("0")
    running_balance = opening_balance

    for entry in entries:
        for line in entry.lines:
            if line.account_id != account_code:
                continue
            opposite_accounts = _get_opposite_accounts(entry.lines, line.account_id)
            running_balance += line.debit - line.credit
            rows.append({
                "posting_date": _fmt_date(entry.posted_date.date() if entry.posted_date else entry.transaction_date),
                "journal_number": entry.journal_number,
                "description": line.description or entry.description,
                "opposite_account": ", ".join(sorted(opposite_accounts)) if opposite_accounts else "",
                "debit": _fmt_vnd(line.debit) if line.debit > 0 else "",
                "credit": _fmt_vnd(line.credit) if line.credit > 0 else "",
                "balance": _fmt_vnd(running_balance),
            })
            period_debit += line.debit
            period_credit += line.credit

    closing_balance = opening_balance + period_debit - period_credit

    return {
        "template_code": "S01-DN",
        "template_name": TEMPLATE_NAMES["S01-DN"],
        "template_name_en": TEMPLATE_NAMES_EN["S01-DN"],
        "company_name": company_name,
        "address": address,
        "period": period,
        "year": year,
        "account_code": account_code,
        "account_name": account_name,
        "opening_balance": _fmt_vnd(opening_balance),
        "rows": rows,
        "period_debit": _fmt_vnd(period_debit),
        "period_credit": _fmt_vnd(period_credit),
        "closing_balance": _fmt_vnd(closing_balance),
        "row_count": len(rows),
        "generated_at": _fmt_date(date.today()),
    }


def generate_subsidiary_template(
    template_code: str,
    subsidiary_type: str,
    entries: List[SubsidiaryLedger],
    period: str,
    company_name: str = "Công ty",
    address: str = "",
) -> dict:
    """Generate S05-DN or S06-DN subsidiary ledger."""
    year = period.split("-")[0] if "-" in period else period

    entity_map: Dict[int, Dict] = {}
    for e in entries:
        if e.entity_id not in entity_map:
            entity_map[e.entity_id] = {
                "entity_id": e.entity_id,
                "entity_name": e.entity_name,
                "rows": [],
                "debit_total": Decimal("0"),
                "credit_total": Decimal("0"),
            }
        em = entity_map[e.entity_id]
        em["rows"].append({
            "posting_date": _fmt_date(e.transaction_date),
            "doc_ref": e.doc_ref,
            "doc_type": e.doc_type,
            "description": e.description,
            "account_code": e.account_code,

            "debit": _fmt_vnd(e.debit) if e.debit > 0 else "",
            "credit": _fmt_vnd(e.credit) if e.credit > 0 else "",
            "balance": _fmt_vnd(e.balance),
        })
        em["debit_total"] += e.debit
        em["credit_total"] += e.credit

    entities = []
    for eid in sorted(entity_map.keys()):
        em = entity_map[eid]
        entities.append({
            "entity_id": em["entity_id"],
            "entity_name": em["entity_name"],
            "rows": em["rows"],
            "debit_total": _fmt_vnd(em["debit_total"]),
            "credit_total": _fmt_vnd(em["credit_total"]),
        })

    return {
        "template_code": template_code,
        "template_name": TEMPLATE_NAMES.get(template_code, template_code),
        "template_name_en": TEMPLATE_NAMES_EN.get(template_code, template_code),
        "company_name": company_name,
        "address": address,
        "period": period,
        "year": year,
        "subsidiary_type": subsidiary_type,
        "entities": entities,
        "entity_count": len(entities),
        "generated_at": _fmt_date(date.today()),
    }
