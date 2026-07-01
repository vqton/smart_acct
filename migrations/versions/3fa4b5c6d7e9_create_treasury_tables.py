"""create treasury tables (Phase 0)

Revision ID: 3fa4b5c6d7e9
Revises: 2fa3b4c5d6e7
Create Date: 2026-06-30

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


revision: str = "3fa4b5c6d7e9"
down_revision: Union[str, None] = "2fa3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trs_cash_in_transit",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="VND"),
        sa.Column("source_account_type", sa.String(length=20), nullable=False),
        sa.Column("source_account_id", sa.Integer(), nullable=False),
        sa.Column("dest_account_type", sa.String(length=20), nullable=False),
        sa.Column("dest_account_id", sa.Integer(), nullable=False),
        sa.Column("transfer_date", sa.Date(), nullable=False),
        sa.Column("expected_clear_date", sa.Date(), nullable=False),
        sa.Column("cleared", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("cleared_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_cash_in_transit_ref", "trs_cash_in_transit", ["reference"], unique=True)

    op.create_table(
        "trs_security_investments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investment_code", sa.String(length=30), nullable=False),
        sa.Column("investment_name", sa.String(length=300), nullable=False),
        sa.Column("investment_type", sa.String(length=30), nullable=False, server_default="trading_security"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("cost_price", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("market_price", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("total_cost", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("fair_value", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("counterparty_name", sa.String(length=300), nullable=True),
        sa.Column("counterparty_id", sa.String(length=50), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("maturity_date", sa.Date(), nullable=True),
        sa.Column("interest_rate", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("interest_basis", sa.String(length=20), nullable=True),
        sa.Column("coa_code", sa.String(length=20), nullable=False),
        sa.Column("coa_income_code", sa.String(length=20), nullable=False, server_default="515"),
        sa.Column("coa_expense_code", sa.String(length=20), nullable=False, server_default="635"),
        sa.Column("period", sa.String(length=10), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_investment_code", "trs_security_investments", ["investment_code"], unique=True)
    op.create_index("ix_trs_investment_type_status", "trs_security_investments", ["investment_type", "status"])
    op.create_index("ix_trs_investment_period", "trs_security_investments", ["period"])

    op.create_table(
        "trs_investment_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investment_id", sa.Integer(), sa.ForeignKey("trs_security_investments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("transaction_type", sa.String(length=20), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("price", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("fee", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("gain_loss", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("counterparty_ref", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "trs_loans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("loan_code", sa.String(length=30), nullable=False),
        sa.Column("loan_name", sa.String(length=300), nullable=False),
        sa.Column("loan_type", sa.String(length=30), nullable=False, server_default="bank_loan"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("principal", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("outstanding_balance", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("interest_rate", sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column("interest_basis", sa.String(length=20), nullable=False, server_default="actual/365"),
        sa.Column("drawdown_date", sa.Date(), nullable=False),
        sa.Column("maturity_date", sa.Date(), nullable=False),
        sa.Column("repayment_frequency", sa.String(length=20), nullable=False, server_default="monthly"),
        sa.Column("repayment_day", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("lender_name", sa.String(length=300), nullable=True),
        sa.Column("lender_id", sa.String(length=50), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="VND"),
        sa.Column("coa_code", sa.String(length=20), nullable=False, server_default="341"),
        sa.Column("coa_interest_code", sa.String(length=20), nullable=False, server_default="635"),
        sa.Column("covenant_dscr_min", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("covenant_icr_min", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("covenant_ltv_max", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_loan_code", "trs_loans", ["loan_code"], unique=True)

    op.create_table(
        "trs_loan_payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("loan_id", sa.Integer(), sa.ForeignKey("trs_loans.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("principal_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("interest_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("is_scheduled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_early_repayment", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("early_repayment_penalty", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_loan_payment_loan_date", "trs_loan_payments", ["loan_id", "payment_date"])

    op.create_table(
        "trs_fx_forwards",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("contract_number", sa.String(length=50), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False, server_default="VND"),
        sa.Column("target_currency", sa.String(length=3), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("forward_rate", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("value_date", sa.Date(), nullable=False),
        sa.Column("maturity_date", sa.Date(), nullable=False),
        sa.Column("counterparty", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("settlement_amount", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_fx_forward_contract", "trs_fx_forwards", ["contract_number"], unique=True)

    op.create_table(
        "trs_cash_flow_forecasts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("forecast_name", sa.String(length=100), nullable=False),
        sa.Column("horizon", sa.String(length=10), nullable=False, server_default="30d"),
        sa.Column("scenario", sa.String(length=10), nullable=False, server_default="base"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="VND"),
        sa.Column("opening_balance", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_inflows", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("total_outflows", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("closing_balance", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("min_balance_threshold", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("min_balance_breach", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("surplus_threshold", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("surplus_identified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("period", sa.String(length=10), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_forecast_period", "trs_cash_flow_forecasts", ["period"])

    op.create_table(
        "trs_forecast_lines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("forecast_id", sa.Integer(), sa.ForeignKey("trs_cash_flow_forecasts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("line_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=False),
        sa.Column("expected_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("expected_date", sa.Date(), nullable=False),
        sa.Column("confidence_pct", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("source_module", sa.String(length=50), nullable=True),
        sa.Column("source_reference", sa.String(length=100), nullable=True),
        sa.Column("is_manual", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_forecast_line_type_date", "trs_forecast_lines", ["forecast_id", "line_type", "expected_date"])

    op.create_table(
        "trs_treasury_positions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="VND"),
        sa.Column("total_cash", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_bank", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_cash_in_transit", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("total_blocked", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("total_available", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_investments", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("total_loans", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("net_liquidity", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("entity_id", sa.String(length=50), nullable=True),
        sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_position_date", "trs_treasury_positions", ["snapshot_date"])
    op.create_index("ix_trs_position_date_entity", "trs_treasury_positions", ["snapshot_date", "entity_id"])

    op.create_table(
        "trs_fx_exposures",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("total_long", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_short", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("net_exposure", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("vnd_equivalent", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("exchange_rate", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("rate_source", sa.String(length=20), nullable=False, server_default="bank_avg"),
        sa.Column("unrealized_gain_loss", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0"),
        sa.Column("policy_limit", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("threshold_breached", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("entity_id", sa.String(length=50), nullable=True),
        sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_fx_exposure_date", "trs_fx_exposures", ["snapshot_date"])
    op.create_index("ix_trs_fx_date_currency", "trs_fx_exposures", ["snapshot_date", "currency", "entity_id"])

    op.create_table(
        "trs_fx_rates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("rate_date", sa.Date(), nullable=False),
        sa.Column("rate_buying", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("rate_selling", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("rate_avg", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("rate_source", sa.String(length=20), nullable=False, server_default="bank_avg"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_fx_rate_currency_date", "trs_fx_rates", ["currency", "rate_date", "rate_source"], unique=True)

    op.create_table(
        "trs_intercompany_loans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("loan_code", sa.String(length=30), nullable=False),
        sa.Column("lender_entity_id", sa.String(length=50), nullable=False),
        sa.Column("borrower_entity_id", sa.String(length=50), nullable=False),
        sa.Column("principal", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("outstanding_balance", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("interest_rate", sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column("interest_basis", sa.String(length=20), nullable=False, server_default="actual/365"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="VND"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("maturity_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("coa_receivable_code", sa.String(length=20), nullable=False, server_default="1368"),
        sa.Column("coa_payable_code", sa.String(length=20), nullable=False, server_default="3368"),
        sa.Column("agreement_ref", sa.String(length=100), nullable=True),
        sa.Column("transfer_pricing_compliant", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_ic_loan_code", "trs_intercompany_loans", ["loan_code"], unique=True)

    op.create_table(
        "trs_intercompany_sweeps",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sweep_type", sa.String(length=20), nullable=False, server_default="zero_balancing"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("sweep_date", sa.Date(), nullable=False),
        sa.Column("source_entity_id", sa.String(length=50), nullable=False),
        sa.Column("target_entity_id", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("source_acct_type", sa.String(length=20), nullable=False, server_default="bank"),
        sa.Column("source_acct_id", sa.Integer(), nullable=False),
        sa.Column("target_acct_type", sa.String(length=20), nullable=False, server_default="bank"),
        sa.Column("target_acct_id", sa.Integer(), nullable=False),
        sa.Column("target_balance_after", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("ic_loan_id", sa.Integer(), sa.ForeignKey("trs_intercompany_loans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_by", sa.String(length=100), nullable=True),
        sa.Column("executed_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "trs_payment_batches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("batch_code", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="VND"),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("approved_by", sa.String(length=100), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("bank_ref", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_batch_code", "trs_payment_batches", ["batch_code"], unique=True)

    op.create_table(
        "trs_payment_batch_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("trs_payment_batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_module", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("source_reference", sa.String(length=50), nullable=False),
        sa.Column("payee_name", sa.String(length=300), nullable=False),
        sa.Column("payee_account", sa.String(length=50), nullable=True),
        sa.Column("payee_bank", sa.String(length=100), nullable=True),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="VND"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("bank_txn_ref", sa.String(length=100), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_batch_item_module_ref", "trs_payment_batch_items", ["source_module", "source_id"])

    op.create_table(
        "trs_bank_connector_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("bank_code", sa.String(length=20), nullable=False),
        sa.Column("bank_name", sa.String(length=200), nullable=False),
        sa.Column("api_endpoint", sa.String(length=500), nullable=True),
        sa.Column("api_version", sa.String(length=20), nullable=True),
        sa.Column("auth_type", sa.String(length=20), nullable=False, server_default="api_key"),
        sa.Column("credentials_encrypted", sa.Text(), nullable=True),
        sa.Column("sync_frequency_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("last_sync_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("supports_balance", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("supports_transactions", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("supports_statements", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("ip_whitelist", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_bank_connector_code", "trs_bank_connector_configs", ["bank_code"], unique=True)

    op.create_table(
        "trs_bank_sync_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("connector_id", sa.Integer(), sa.ForeignKey("trs_bank_connector_configs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sync_type", sa.String(length=50), nullable=False),
        sa.Column("sync_status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("transactions_fetched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transactions_matched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transactions_unmatched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "trs_treasury_policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("policy_code", sa.String(length=30), nullable=False),
        sa.Column("policy_name", sa.String(length=300), nullable=False),
        sa.Column("policy_type", sa.String(length=50), nullable=False),
        sa.Column("threshold_value", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("threshold_pct", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("min_value", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("max_value", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("counterparty_restriction", sa.String(length=500), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_policy_code", "trs_treasury_policies", ["policy_code"], unique=True)

    op.create_table(
        "trs_audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("performed_by", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trs_audit_entity", "trs_audit_logs", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_table("trs_audit_logs")
    op.drop_table("trs_treasury_policies")
    op.drop_table("trs_bank_sync_logs")
    op.drop_table("trs_bank_connector_configs")
    op.drop_table("trs_payment_batch_items")
    op.drop_table("trs_payment_batches")
    op.drop_table("trs_intercompany_sweeps")
    op.drop_table("trs_intercompany_loans")
    op.drop_table("trs_fx_rates")
    op.drop_table("trs_fx_exposures")
    op.drop_table("trs_treasury_positions")
    op.drop_table("trs_forecast_lines")
    op.drop_table("trs_cash_flow_forecasts")
    op.drop_table("trs_fx_forwards")
    op.drop_table("trs_loan_payments")
    op.drop_table("trs_loans")
    op.drop_table("trs_investment_transactions")
    op.drop_table("trs_security_investments")
    op.drop_table("trs_cash_in_transit")
