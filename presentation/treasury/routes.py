from datetime import date
from decimal import Decimal
from flask import request, jsonify

from presentation import resolve_error
from presentation.treasury import (
    trs_bp, _get_session,
    _json_cash_in_transit, _json_investment, _json_loan, _json_forecast,
    _json_position, _json_fx_exposure, _json_ic_loan, _json_ic_sweep,
    _json_batch, _json_connector, _json_policy, _json_kpi,
)
from use_cases.treasury import TreasuryUseCases
from domain.treasury import (
    InvestmentType, InvestmentStatus, LoanType, LoanStatus,
    ForecastHorizon, ScenarioType, SweepType,
)
from domain.i18n import ErrorCodes
from domain.common import ValidationError


# ── UC-TRS-01: Consolidated Cash Position ──────────────────────────

@trs_bp.route("/position", methods=["GET"])
def get_cash_position():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        entity_id = request.args.get("entity_id")
        result = uc.get_consolidated_cash_position(entity_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(_json_position(result.get_data()))
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/positions", methods=["GET"])
def list_positions():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        snapshot_date = request.args.get("snapshot_date")
        entity_id = request.args.get("entity_id")
        date_parsed = date.fromisoformat(snapshot_date) if snapshot_date else None
        result = uc.get_position_history(
            days=int(request.args.get("days", 30)),
            entity_id=entity_id,
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        positions = result.get_data()
        return jsonify({"positions": [_json_position(p) for p in positions]})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── UC-TRS-02: Cash Flow Forecasting ───────────────────────────────

@trs_bp.route("/forecasts", methods=["POST"])
def create_forecast():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.create_forecast(
            forecast_name=data["forecast_name"],
            horizon=ForecastHorizon(data.get("horizon", "30d")),
            scenario=ScenarioType(data.get("scenario", "base")),
            opening_balance=Decimal(str(data["opening_balance"])),
            forecast_date=date.fromisoformat(data["forecast_date"]),
            min_balance_threshold=Decimal(str(data["min_balance_threshold"])) if data.get("min_balance_threshold") else None,
            surplus_threshold=Decimal(str(data["surplus_threshold"])) if data.get("surplus_threshold") else None,
            currency=data.get("currency", "VND"),
            period=data.get("period"),
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_forecast(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/forecasts", methods=["GET"])
def list_forecasts():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        period = request.args.get("period")
        horizon = request.args.get("horizon")
        result = uc.list_forecasts(period=period, horizon=horizon)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        forecasts = result.get_data()
        return jsonify({"forecasts": [_json_forecast(f) for f in forecasts]})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/forecasts/<int:forecast_id>", methods=["GET"])
def get_forecast(forecast_id):
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.get_forecast(forecast_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_forecast(result.get_data()))
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/forecasts/<int:forecast_id>/lines", methods=["POST"])
def add_forecast_line(forecast_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.add_forecast_line(
            forecast_id=forecast_id,
            line_type=data["line_type"],
            description=data["description"],
            expected_amount=Decimal(str(data["expected_amount"])),
            expected_date=date.fromisoformat(data["expected_date"]),
            confidence_pct=int(data.get("confidence_pct", 80)),
            source_module=data.get("source_module"),
            source_reference=data.get("source_reference"),
            is_manual=data.get("is_manual", False),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"id": result.get_data().id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/forecasts/<int:forecast_id>/calculate", methods=["POST"])
def run_forecast_calculation(forecast_id):
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.run_forecast_calculation(forecast_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_forecast(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── UC-TRS-03: Investment Management ───────────────────────────────

@trs_bp.route("/investments", methods=["POST"])
def create_investment():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.create_investment(
            investment_code=data["investment_code"],
            investment_name=data["investment_name"],
            investment_type=InvestmentType(data.get("investment_type", "trading_security")),
            cost_price=Decimal(str(data["cost_price"])),
            total_cost=Decimal(str(data.get("total_cost", data["cost_price"]))),
            purchase_date=date.fromisoformat(data["purchase_date"]),
            maturity_date=date.fromisoformat(data["maturity_date"]) if data.get("maturity_date") else None,
            quantity=Decimal(str(data["quantity"])) if data.get("quantity") else None,
            market_price=Decimal(str(data["market_price"])) if data.get("market_price") else None,
            fair_value=Decimal(str(data["fair_value"])) if data.get("fair_value") else None,
            counterparty_name=data.get("counterparty_name"),
            counterparty_id=data.get("counterparty_id"),
            interest_rate=Decimal(str(data["interest_rate"])) if data.get("interest_rate") else None,
            coa_code=data.get("coa_code", "121"),
            period=data.get("period"),
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_investment(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/investments", methods=["GET"])
def list_investments():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        investment_type = request.args.get("investment_type")
        status = request.args.get("status")
        result = uc.list_investments(investment_type=investment_type, status=status)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"investments": [_json_investment(i) for i in result.get_data()]})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/investments/<int:investment_id>", methods=["GET"])
def get_investment(investment_id):
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.get_investment(investment_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_investment(result.get_data()))
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/investments/<int:investment_id>/maturity", methods=["POST"])
def record_investment_maturity(investment_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        actual_amount = Decimal(str(data["actual_amount"]))
        interest_income = Decimal(str(data.get("interest_income", "0")))
        maturity_date_parsed = date.fromisoformat(data.get("maturity_date", str(date.today())))
        result = uc.record_investment_maturity(investment_id, maturity_date_parsed, actual_amount, interest_income)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_investment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/investments/<int:investment_id>/sale", methods=["POST"])
def record_investment_sale(investment_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        sale_date_parsed = date.fromisoformat(data.get("sale_date", str(date.today())))
        sale_price = Decimal(str(data["sale_price"]))
        total_amount = Decimal(str(data.get("total_amount", sale_price)))
        gain_loss = Decimal(str(data.get("gain_loss", "0")))
        result = uc.record_investment_sale(investment_id, sale_date_parsed, Decimal("1"), sale_price, total_amount, gain_loss)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_investment(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/investments/maturing", methods=["GET"])
def get_maturing_investments():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        days = int(request.args.get("days", 30))
        result = uc.get_maturing_investments(days)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"investments": [_json_investment(i) for i in result.get_data()]})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── UC-TRS-04: Debt Management ─────────────────────────────────────

@trs_bp.route("/loans", methods=["POST"])
def create_loan():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.create_loan(
            loan_code=data["loan_code"],
            loan_name=data["loan_name"],
            loan_type=LoanType(data.get("loan_type", "bank_loan")),
            principal=Decimal(str(data["principal"])),
            interest_rate=Decimal(str(data.get("interest_rate", "0"))),
            drawdown_date=date.fromisoformat(data["drawdown_date"]),
            maturity_date=date.fromisoformat(data["maturity_date"]),
            currency=data.get("currency", "VND"),
            lender_name=data.get("lender_name"),
            coa_code=data.get("coa_code", "341"),
            notes=data.get("notes"),
            repayment_frequency=data.get("repayment_frequency", "monthly"),
            repayment_day=int(data.get("repayment_day", 1)),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_loan(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/loans", methods=["GET"])
def list_loans():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        loan_type = request.args.get("loan_type")
        status = request.args.get("status")
        result = uc.list_loans(loan_type=loan_type, status=status)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"loans": [_json_loan(l) for l in result.get_data()]})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/loans/<int:loan_id>", methods=["GET"])
def get_loan(loan_id):
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.get_loan(loan_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_loan(result.get_data()))
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/loans/<int:loan_id>/payments", methods=["POST"])
def record_loan_payment(loan_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.record_loan_payment(
            loan_id=loan_id,
            payment_date=date.fromisoformat(data.get("payment_date", str(date.today()))),
            principal_amount=Decimal(str(data["principal_amount"])),
            interest_amount=Decimal(str(data.get("interest_amount", "0"))),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"data": result.get_data()})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/loans/<int:loan_id>/covenants", methods=["GET"])
def check_loan_covenants(loan_id):
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.check_loan_covenants(loan_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify(result.get_data())
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/loans/upcoming-payments", methods=["GET"])
def get_upcoming_loan_payments():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        days = int(request.args.get("days", 30))
        result = uc.get_upcoming_payments(days)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"payments": result.get_data()})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── UC-TRS-06: FX Exposure ─────────────────────────────────────────

@trs_bp.route("/fx-rates", methods=["POST"])
def record_fx_rate():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.record_fx_rate(
            currency=data["currency"],
            rate_date=date.fromisoformat(data["rate_date"]),
            rate_avg=Decimal(str(data["rate_avg"])),
            rate_buying=Decimal(str(data["rate_buying"])) if data.get("rate_buying") else None,
            rate_selling=Decimal(str(data["rate_selling"])) if data.get("rate_selling") else None,
            rate_source=data.get("rate_source", "bank_avg"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "FX rate recorded", "id": result.get_data().id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/fx-exposures", methods=["GET"])
def get_fx_exposure():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        entity_id = request.args.get("entity_id")
        result = uc.calculate_fx_exposure(entity_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        fx_list = result.get_data()
        if isinstance(fx_list, list):
            return jsonify({"fx_exposures": [_json_fx_exposure(fx) for fx in fx_list]})
        return jsonify(_json_fx_exposure(fx_list))
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── UC-TRS-07: Intercompany ────────────────────────────────────────

@trs_bp.route("/ic-loans", methods=["POST"])
def create_ic_loan():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.create_ic_loan(
            loan_code=data["loan_code"],
            lender_entity_id=data["lender_entity_id"],
            borrower_entity_id=data["borrower_entity_id"],
            principal=Decimal(str(data["principal"])),
            interest_rate=Decimal(str(data.get("interest_rate", "0"))),
            start_date=date.fromisoformat(data["start_date"]),
            maturity_date=date.fromisoformat(data["maturity_date"]),
            currency=data.get("currency", "VND"),
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_ic_loan(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/ic-loans", methods=["GET"])
def list_ic_loans():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.list_ic_loans(
            lender=request.args.get("lender_entity_id"),
            borrower=request.args.get("borrower_entity_id"),
            status=request.args.get("status"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"ic_loans": [_json_ic_loan(l) for l in result.get_data()]})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/ic-sweeps/propose", methods=["POST"])
def propose_ic_sweeps():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        entities_config = data.get("entities", {})
        sweep_date = date.fromisoformat(data.get("sweep_date", str(date.today())))
        result = uc.propose_ic_sweeps(sweep_date, entities_config)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"proposals": result.get_data()})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/ic-sweeps/<int:sweep_id>/execute", methods=["POST"])
def execute_ic_sweep(sweep_id):
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.execute_ic_sweep(sweep_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_ic_sweep(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── UC-TRS-08: Dashboard & KPIs ────────────────────────────────────

@trs_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        entity_id = request.args.get("entity_id")
        result = uc.compute_dashboard_kpis(entity_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"dashboard": _json_kpi(result.get_data())})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/reports", methods=["GET"])
def generate_report():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        report_type = request.args.get("type", "daily")
        period = request.args.get("period")
        result = uc.generate_treasury_report(report_type, period)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"report": result.get_data()})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── UC-TRS-09: Payment Factory ─────────────────────────────────────

@trs_bp.route("/payment-batches", methods=["POST"])
def create_payment_batch():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.create_payment_batch(
            batch_code=data["batch_code"],
            payment_date=date.fromisoformat(data["payment_date"]),
            currency=data.get("currency", "VND"),
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_batch(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/payment-batches", methods=["GET"])
def list_payment_batches():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        status = request.args.get("status")
        result = uc.list_batches(status=status)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"batches": [_json_batch(b) for b in result.get_data()]})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/payment-batches/<int:batch_id>", methods=["GET"])
def get_payment_batch(batch_id):
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.get_batch(batch_id)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 404
        return jsonify(_json_batch(result.get_data()))
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/payment-batches/<int:batch_id>/items", methods=["POST"])
def add_batch_item(batch_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.add_item_to_batch(
            batch_id=batch_id,
            source_module=data["source_module"],
            source_id=int(data["source_id"]),
            source_reference=data["source_reference"],
            payee_name=data["payee_name"],
            amount=Decimal(str(data["amount"])),
            payee_account=data.get("payee_account"),
            payee_bank=data.get("payee_bank"),
            currency=data.get("currency", "VND"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"item_id": result.get_data().id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/payment-batches/<int:batch_id>/approve", methods=["POST"])
def approve_payment_batch(batch_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.approve_batch(batch_id, approved_by=data.get("approved_by", "system"))
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_batch(result.get_data()))
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── UC-TRS-10: Bank Connectivity ───────────────────────────────────

@trs_bp.route("/connectors", methods=["POST"])
def create_connector():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.create_bank_connector(
            bank_code=data["bank_code"],
            bank_name=data["bank_name"],
            api_endpoint=data.get("api_endpoint"),
            auth_type=data.get("auth_type", "api_key"),
            sync_frequency_minutes=int(data.get("sync_frequency_minutes", 60)),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_connector(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/connectors", methods=["GET"])
def list_connectors():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        active_only = request.args.get("active_only", "false").lower() == "true"
        result = uc.list_connectors(active_only=active_only)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"connectors": [_json_connector(c) for c in result.get_data()]})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/connectors/<int:connector_id>/sync", methods=["POST"])
def sync_bank_data(connector_id):
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        sync_type = data.get("sync_type", "balance")
        result = uc.sync_bank_data(connector_id, sync_type)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify({"message": "Sync completed", "log_id": result.get_data().id})
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Treasury Policies ──────────────────────────────────────────────

@trs_bp.route("/policies", methods=["POST"])
def create_policy():
    data = request.get_json() or {}
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        result = uc.create_treasury_policy(
            policy_code=data["policy_code"],
            policy_name=data["policy_name"],
            policy_type=data["policy_type"],
            threshold_value=Decimal(str(data["threshold_value"])) if data.get("threshold_value") else None,
            min_value=Decimal(str(data["min_value"])) if data.get("min_value") else None,
            max_value=Decimal(str(data["max_value"])) if data.get("max_value") else None,
            notes=data.get("notes"),
        )
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        session.commit()
        return jsonify(_json_policy(result.get_data())), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


@trs_bp.route("/policies", methods=["GET"])
def list_policies():
    session = _get_session()
    try:
        uc = TreasuryUseCases(session)
        policy_type = request.args.get("policy_type")
        active_only = request.args.get("active_only", "false").lower() == "true"
        result = uc.list_treasury_policies(policy_type=policy_type, active_only=active_only)
        if result.is_failure():
            return jsonify({"error": resolve_error(result.error)}), 400
        return jsonify({"policies": [_json_policy(p) for p in result.get_data()]})
    except Exception as e:
        return jsonify({"error": resolve_error(e)}), 400
    finally:
        session.close()


# ── Register blueprint ─────────────────────────────────────────────

def register_blueprint(app):
    app.register_blueprint(trs_bp)
