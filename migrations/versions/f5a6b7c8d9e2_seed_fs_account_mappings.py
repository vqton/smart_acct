"""seed default FS account mappings for B01-DN and B02-DN

Revision ID: f5a6b7c8d9e2
Revises: f5a6b7c8d9e1
Create Date: 2026-07-01 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'f5a6b7c8d9e2'
down_revision: Union[str, None] = 'f5a6b7c8d9e1'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None

# ── B01-DN: Balance Sheet (fs_ma_so, GL account_code, direction) ──
_B01_MAPPINGS = [
    ("111", "1111", "debit"), ("111", "1112", "debit"), ("111", "1113", "debit"),
    ("112", "1121", "debit"), ("112", "1122", "debit"), ("112", "1123", "debit"),
    ("120", "121", "debit"), ("120", "128", "debit"),
    ("130", "131", "debit"), ("130", "136", "debit"),
    ("130", "137", "debit"), ("130", "138", "debit"),
    ("140", "151", "debit"), ("140", "152", "debit"), ("140", "153", "debit"),
    ("140", "154", "debit"), ("140", "155", "debit"),
    ("140", "156", "debit"), ("140", "157", "debit"),
    ("150", "133", "debit"), ("150", "141", "debit"), ("150", "242", "debit"),
    ("210", "211", "debit"), ("210", "212", "debit"),
    ("210", "213", "debit"), ("210", "218", "debit"),
    ("220", "221", "debit"), ("220", "222", "debit"), ("220", "223", "debit"),
    ("220", "224", "debit"), ("220", "227", "debit"),
    ("230", "231", "debit"), ("230", "237", "debit"),
    ("240", "241", "debit"),
    ("250", "251", "debit"), ("250", "258", "debit"),
    ("260", "261", "debit"), ("260", "262", "debit"), ("260", "268", "debit"),
    ("310", "311", "credit"), ("310", "312", "credit"), ("310", "313", "credit"),
    ("310", "314", "credit"), ("310", "315", "credit"), ("310", "318", "credit"),
    ("310", "319", "credit"), ("310", "321", "credit"), ("310", "322", "credit"),
    ("310", "323", "credit"), ("310", "337", "credit"),
    ("310", "331", "credit"), ("310", "332", "credit"), ("310", "333", "credit"),
    ("310", "334", "credit"), ("310", "335", "credit"), ("310", "336", "credit"),
    ("310", "338", "credit"), ("310", "339", "credit"),
    ("330", "341", "credit"), ("330", "342", "credit"), ("330", "343", "credit"),
    ("330", "347", "credit"), ("330", "348", "credit"), ("330", "349", "credit"),
    ("410", "4111", "credit"), ("410", "4112", "credit"),
    ("420", "412", "credit"),
    ("430", "421", "credit"),
]

# ── B02-DN: Income Statement (fs_ma_so, GL account_code, direction) ─
_B02_MAPPINGS = [
    ("01", "5111", "credit"), ("01", "5112", "credit"), ("01", "5113", "credit"),
    ("02", "5211", "debit"), ("02", "5212", "debit"), ("02", "5213", "debit"),
    ("11", "632", "debit"),
    ("21", "515", "credit"),
    ("22", "635", "debit"),
    ("23", "641", "debit"),
    ("24", "642", "debit"),
    ("40", "711", "credit"),
    ("41", "811", "debit"),
    ("51", "821", "debit"),
    ("52", "8212", "debit"),
]


def _seed(st: str, mappings: list) -> None:
    for fs_ma_so, account_code, direction in mappings:
        op.execute(
            "INSERT INTO fs_account_mappings "
            "(fs_ma_so, account_code, weight, direction, statement_type) "
            "SELECT :ms, :ac, 1.0, :dir, :st "
            "WHERE NOT EXISTS ("
            "  SELECT 1 FROM fs_account_mappings "
            "  WHERE account_code = :ac2 AND fs_ma_so = :ms2 AND statement_type = :st2"
            ")",
            {
                "ms": fs_ma_so, "ac": account_code, "dir": direction,
                "st": st,
                "ac2": account_code, "ms2": fs_ma_so, "st2": st,
            },
        )


def upgrade() -> None:
    _seed("B01_DN", _B01_MAPPINGS)
    _seed("B02_DN", _B02_MAPPINGS)


def downgrade() -> None:
    for fs_ma_so, account_code, direction in _B01_MAPPINGS:
        op.execute(
            "DELETE FROM fs_account_mappings "
            "WHERE account_code = :ac AND fs_ma_so = :ms AND statement_type = :st",
            {"ac": account_code, "ms": fs_ma_so, "st": "B01_DN"},
        )
    for fs_ma_so, account_code, direction in _B02_MAPPINGS:
        op.execute(
            "DELETE FROM fs_account_mappings "
            "WHERE account_code = :ac AND fs_ma_so = :ms AND statement_type = :st",
            {"ac": account_code, "ms": fs_ma_so, "st": "B02_DN"},
        )
