import pytest
import json
from io import BytesIO
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from infrastructure.models.coa_models import Base, COAModel, AccountingRegime as DBRegime, AccountStatus as DBStatus
from use_cases.coa_use_cases import COAUseCases
from presentation.coa_routes import coa_bp


class FakeDBManager:
    def __init__(self, engine):
        self._engine = engine

    def get_session(self):
        return Session(self._engine)

    def close(self):
        pass


@pytest.fixture(scope="function")
def app():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    _seed(sess)
    sess.commit()
    sess.close()

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.db_manager = FakeDBManager(engine)
    app.register_blueprint(coa_bp, url_prefix="/api/v1/coa")
    return app


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


def _seed(sess):
    accounts = [
        COAModel(code="1", name="Tài sản", account_type="asset",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction="debit", level=1, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="1111", name="Tiền mặt", account_type="asset",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction="debit", level=2, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="5111", name="Doanh thu bán hàng", account_type="revenue",
                 regime=DBRegime.TT99_2025, vas_compliant=True,
                 drcr_direction="credit", level=2, status=DBStatus.ACTIVE,
                 currency="VND", unit="VND"),
    ]
    for a in accounts:
        sess.add(a)


class TestCOAIntegration:
    def test_list_accounts(self, client):
        resp = client.get("/api/v1/coa/accounts")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 3

    def test_get_account(self, client):
        resp = client.get("/api/v1/coa/accounts/1111")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["code"] == "1111"
        assert data["name"] == "Tiền mặt"

    def test_get_account_not_found(self, client):
        resp = client.get("/api/v1/coa/accounts/NONEXIST")
        assert resp.status_code == 404

    def test_create_account(self, client):
        payload = {
            "code": "3331",
            "name": "Phải trả người bán",
            "account_type": "liability",
            "regime": "tt99_2025",
            "drcr_direction": "credit",
            "level": 2,
            "currency": "VND",
            "unit": "VND",
        }
        resp = client.post("/api/v1/coa/accounts", json=payload)
        assert resp.status_code == 201, resp.get_json()
        data = resp.get_json()
        assert data["code"] == "3331"

    def test_create_account_duplicate(self, client):
        payload = {
            "code": "1111",
            "name": "Duplicate",
            "account_type": "asset",
            "regime": "tt99_2025",
            "drcr_direction": "debit",
            "level": 2,
            "currency": "VND",
            "unit": "VND",
        }
        resp = client.post("/api/v1/coa/accounts", json=payload)
        assert resp.status_code == 400

    def test_update_account(self, client):
        resp = client.put("/api/v1/coa/accounts/1111", json={"name": "Tiền mặt (VND)"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Tiền mặt (VND)"

    def test_delete_account(self, client):
        resp = client.delete("/api/v1/coa/accounts/1111")
        assert resp.status_code == 200
        resp2 = client.get("/api/v1/coa/accounts/1111")
        assert resp2.status_code == 404

    def test_search_accounts(self, client):
        resp = client.get("/api/v1/coa/accounts/search?q=tiền")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) >= 1

    def test_summary(self, client):
        resp = client.get("/api/v1/coa/summary")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 3

    def test_import_json(self, client):
        payload = {
            "accounts": [
                {
                    "code": "4441",
                    "name": "Test Account",
                    "account_type": "asset",
                    "regime": "tt99_2025",
                    "drcr_direction": "debit",
                    "level": 1,
                    "currency": "VND", "unit": "VND",
                }
            ]
        }
        resp = client.post("/api/v1/coa/import", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["created_count"] == 1

    def test_export_json(self, client):
        resp = client.get("/api/v1/coa/export?format=json")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 3

    def test_export_csv(self, client):
        resp = client.get("/api/v1/coa/export?format=csv")
        assert resp.status_code == 200
        assert resp.content_type.startswith("text/csv")

    def test_versioning(self, client):
        resp = client.post("/api/v1/coa/versions", json={"created_by": "admin", "notes": "Test snapshot"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert "id" in data

        resp2 = client.get("/api/v1/coa/versions")
        assert resp2.status_code == 200
        versions = resp2.get_json()
        assert versions["total"] >= 1

    def test_ifrs_mapping(self, client):
        payload = {
            "vas_account_code": "1111",
            "ifrs_account_code": "IFRS_CASH_001",
            "mapping_type": "1:1",
            "created_by": "admin",
        }
        resp = client.post("/api/v1/coa/ifrs-mapping", json=payload)
        assert resp.status_code == 201, resp.get_json()
        data = resp.get_json()
        assert data["vas_account_code"] == "1111"
        assert data["ifrs_account_code"] == "IFRS_CASH_001"

        resp2 = client.get("/api/v1/coa/ifrs-mapping")
        assert resp2.status_code == 200
        mappings = resp2.get_json()
        assert mappings["total"] == 1

    def test_ifrs_coverage(self, client):
        client.post("/api/v1/coa/ifrs-mapping", json={
            "vas_account_code": "1111",
            "ifrs_account_code": "IFRS_CASH",
            "created_by": "admin",
        })
        resp = client.get("/api/v1/coa/ifrs-mapping/coverage")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_vas_accounts"] == 3
        assert data["mapped_accounts"] >= 1

    def test_compliance_scan(self, client):
        resp = client.get("/api/v1/coa/compliance/scan")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["summary"]["total_accounts"] == 3

    def test_compliance_check(self, client):
        resp = client.get("/api/v1/coa/compliance/1111")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["compliant"] is True

    def test_usage_check(self, client):
        resp = client.get("/api/v1/coa/usage/1111")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["code"] == "1111"
        assert data["transaction_count"] == 0

    def test_usage_check_not_found(self, client):
        resp = client.get("/api/v1/coa/usage/NONEXIST")
        assert resp.status_code == 404
