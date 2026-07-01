from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from domain import (
    ChartOfAccounts, AccountType, DCRDirection,
    AccountingRegime, Result, VASValidationError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.coa_repository import COARepository


STANDARD_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "tt99_2025_standard": {
        "name": "Standard COA (TT99/2025)",
        "description": "Hệ thống tài khoản kế toán theo Thông tư 99/2025/TT-BTC — doanh nghiệp mọi thành phần kinh tế",
        "regime": "tt99_2025",
        "accounts": [
            # TÀI SẢN (ASSETS)
            {"code": "1", "name": "Tài sản", "account_type": "asset", "drcr_direction": "debit", "level": 1},
            {"code": "11", "name": "Tiền và các khoản tương đương tiền", "account_type": "asset", "drcr_direction": "debit", "level": 2},
            {"code": "111", "name": "Tiền mặt", "account_type": "cash", "drcr_direction": "debit", "level": 3},
            {"code": "1111", "name": "Tiền mặt tại quỹ (VND)", "account_type": "cash", "drcr_direction": "debit", "level": 4, "currency": "VND"},
            {"code": "112", "name": "Tiền gửi ngân hàng", "account_type": "bank", "drcr_direction": "debit", "level": 3},
            {"code": "113", "name": "Tiền đang chuyển", "account_type": "cash", "drcr_direction": "debit", "level": 3},
            {"code": "12", "name": "Đầu tư tài chính ngắn hạn", "account_type": "short_term_financial_investment", "drcr_direction": "debit", "level": 2},
            {"code": "121", "name": "Chứng khoán kinh doanh", "account_type": "short_term_financial_investment", "drcr_direction": "debit", "level": 3},
            {"code": "128", "name": "Đầu tư nắm giữ đến ngày đáo hạn", "account_type": "short_term_financial_investment", "drcr_direction": "debit", "level": 3},
            {"code": "13", "name": "Các khoản phải thu ngắn hạn", "account_type": "account_receivable", "drcr_direction": "debit", "level": 2},
            {"code": "131", "name": "Phải thu của khách hàng", "account_type": "account_receivable", "drcr_direction": "debit", "level": 3},
            {"code": "133", "name": "Thuế GTGT được khấu trừ", "account_type": "vat_input", "drcr_direction": "debit", "level": 3},
            {"code": "136", "name": "Phải thu nội bộ", "account_type": "account_receivable", "drcr_direction": "debit", "level": 3},
            {"code": "138", "name": "Phải thu khác", "account_type": "account_receivable", "drcr_direction": "debit", "level": 3},
            {"code": "1383", "name": "Thuế tiêu thụ đặc biệt hàng nhập khẩu", "account_type": "sct_imported_goods", "drcr_direction": "debit", "level": 4},
            {"code": "14", "name": "Hàng tồn kho", "account_type": "inventory_goods", "drcr_direction": "debit", "level": 2},
            {"code": "141", "name": "Tạm ứng", "account_type": "advance", "drcr_direction": "debit", "level": 3},
            {"code": "15", "name": "Tài sản ngắn hạn khác", "account_type": "other_current_assets", "drcr_direction": "debit", "level": 2},
            {"code": "152", "name": "Nguyên liệu, vật liệu", "account_type": "inventory_goods", "drcr_direction": "debit", "level": 3},
            {"code": "153", "name": "Công cụ, dụng cụ", "account_type": "tools_and_accessories", "drcr_direction": "debit", "level": 3},
            {"code": "154", "name": "Chi phí sản xuất kinh doanh dở dang", "account_type": "production_in_progress", "drcr_direction": "debit", "level": 3},
            {"code": "155", "name": "Thành phẩm", "account_type": "inventory_goods", "drcr_direction": "debit", "level": 3},
            {"code": "156", "name": "Hàng hóa", "account_type": "inventory_goods", "drcr_direction": "debit", "level": 3},
            {"code": "157", "name": "Hàng gửi đi bán", "account_type": "inventory_goods", "drcr_direction": "debit", "level": 3},
            {"code": "158", "name": "Hàng tồn kho bất động sản", "account_type": "inventory_goods", "drcr_direction": "debit", "level": 3},
            {"code": "21", "name": "Tài sản cố định", "account_type": "fixed_assets", "drcr_direction": "debit", "level": 2},
            {"code": "211", "name": "TSCĐ hữu hình", "account_type": "fixed_assets", "drcr_direction": "debit", "level": 3},
            {"code": "212", "name": "TSCĐ thuê tài chính", "account_type": "fixed_assets", "drcr_direction": "debit", "level": 3},
            {"code": "213", "name": "TSCĐ vô hình", "account_type": "intangible_assets", "drcr_direction": "debit", "level": 3},
            {"code": "214", "name": "Hao mòn TSCĐ", "account_type": "depreciation_expense", "drcr_direction": "credit", "level": 3},
            {"code": "215", "name": "Tài sản sinh học", "account_type": "biological_asset", "drcr_direction": "debit", "level": 3},
            {"code": "217", "name": "Bất động sản đầu tư", "account_type": "fixed_assets", "drcr_direction": "debit", "level": 3},
            {"code": "22", "name": "Đầu tư tài chính dài hạn", "account_type": "long_term_financial_investment", "drcr_direction": "debit", "level": 2},
            {"code": "221", "name": "Đầu tư vào công ty con", "account_type": "long_term_financial_investment", "drcr_direction": "debit", "level": 3},
            {"code": "222", "name": "Đầu tư vào công ty liên doanh, liên kết", "account_type": "long_term_financial_investment", "drcr_direction": "debit", "level": 3},
            {"code": "228", "name": "Đầu tư khác", "account_type": "long_term_financial_investment", "drcr_direction": "debit", "level": 3},
            {"code": "229", "name": "Dự phòng", "account_type": "provisions", "drcr_direction": "credit", "level": 3},
            {"code": "2295", "name": "Dự phòng giảm giá tài sản sinh học", "account_type": "provision_for_biological_asset", "drcr_direction": "credit", "level": 4},
            {"code": "24", "name": "Tài sản dài hạn khác", "account_type": "other_current_assets", "drcr_direction": "debit", "level": 2},
            {"code": "241", "name": "XDCB dở dang", "account_type": "construction_in_progress", "drcr_direction": "debit", "level": 3},
            {"code": "242", "name": "Chi phí trả trước", "account_type": "prepaid_expenses", "drcr_direction": "debit", "level": 3},
            {"code": "243", "name": "Tài sản thuế thu nhập hoãn lại", "account_type": "other_current_assets", "drcr_direction": "debit", "level": 3},

            # NỢ PHẢI TRẢ (LIABILITIES)
            {"code": "3", "name": "Nợ phải trả", "account_type": "liability", "drcr_direction": "credit", "level": 1},
            {"code": "31", "name": "Nợ ngắn hạn", "account_type": "short_term_liabilities", "drcr_direction": "credit", "level": 2},
            {"code": "33", "name": "Nợ dài hạn", "account_type": "long_term_liabilities", "drcr_direction": "credit", "level": 2},
            {"code": "331", "name": "Phải trả người bán", "account_type": "accounts_payable", "drcr_direction": "credit", "level": 3},
            {"code": "333", "name": "Thuế và các khoản phải nộp NN", "account_type": "taxes_and_charges_payable", "drcr_direction": "credit", "level": 3},
            {"code": "3331", "name": "Thuế GTGT phải nộp", "account_type": "taxes_and_charges_payable", "drcr_direction": "credit", "level": 4},
            {"code": "3334", "name": "Thuế TNDN phải nộp", "account_type": "cit_payment", "drcr_direction": "credit", "level": 4},
            {"code": "3335", "name": "Thuế TNCN phải nộp", "account_type": "pit_payment", "drcr_direction": "credit", "level": 4},
            {"code": "334", "name": "Phải trả người lao động", "account_type": "expenses_payable", "drcr_direction": "credit", "level": 3},
            {"code": "335", "name": "Chi phí phải trả", "account_type": "expenses_payable", "drcr_direction": "credit", "level": 3},
            {"code": "336", "name": "Phải trả nội bộ", "account_type": "accounts_payable", "drcr_direction": "credit", "level": 3},
            {"code": "337", "name": "Doanh thu chưa thực hiện", "account_type": "sales_revenue_payable", "drcr_direction": "credit", "level": 3},
            {"code": "338", "name": "Phải trả, phải nộp khác", "account_type": "accounts_payable", "drcr_direction": "credit", "level": 3},
            {"code": "3381", "name": "Tài sản thừa chờ giải quyết", "account_type": "asset_surplus", "drcr_direction": "credit", "level": 4},
            {"code": "3382", "name": "Kinh phí công đoàn", "account_type": "expenses_payable", "drcr_direction": "credit", "level": 4},
            {"code": "3383", "name": "Bảo hiểm xã hội", "account_type": "expenses_payable", "drcr_direction": "credit", "level": 4},
            {"code": "3384", "name": "Bảo hiểm y tế", "account_type": "expenses_payable", "drcr_direction": "credit", "level": 4},
            {"code": "3385", "name": "Bảo hiểm thất nghiệp", "account_type": "expenses_payable", "drcr_direction": "credit", "level": 4},
            {"code": "3386", "name": "Bảo hiểm tai nạn lao động", "account_type": "expenses_payable", "drcr_direction": "credit", "level": 4},
            {"code": "3387", "name": "Doanh thu chưa thực hiện", "account_type": "sales_revenue_payable", "drcr_direction": "credit", "level": 4},
            {"code": "34", "name": "Vay và nợ thuê tài chính", "account_type": "borrowings_from_credit_institutions", "drcr_direction": "credit", "level": 2},
            {"code": "341", "name": "Vay và nợ thuê tài chính", "account_type": "borrowings_from_credit_institutions", "drcr_direction": "credit", "level": 3},

            # VỐN CHỦ SỞ HỮU (EQUITY)
            {"code": "4", "name": "Vốn chủ sở hữu", "account_type": "equity", "drcr_direction": "credit", "level": 1},
            {"code": "411", "name": "Vốn góp của chủ sở hữu", "account_type": "capital_contributed", "drcr_direction": "credit", "level": 2},
            {"code": "412", "name": "Thặng dư vốn cổ phần", "account_type": "capital_surplus", "drcr_direction": "credit", "level": 2},
            {"code": "413", "name": "Chênh lệch tỷ giá hối đoái", "account_type": "revaluation_surplus", "drcr_direction": "credit", "level": 2},
            {"code": "414", "name": "Quỹ đầu tư phát triển", "account_type": "equity_distribution", "drcr_direction": "credit", "level": 2},
            {"code": "418", "name": "Các quỹ khác thuộc VCSH", "account_type": "equity_distribution", "drcr_direction": "credit", "level": 2},
            {"code": "419", "name": "Cổ phiếu quỹ", "account_type": "equity", "drcr_direction": "debit", "level": 2},
            {"code": "421", "name": "Lợi nhuận sau thuế chưa phân phối", "account_type": "retained_earnings", "drcr_direction": "credit", "level": 2},

            # DOANH THU (REVENUE)
            {"code": "5", "name": "Doanh thu", "account_type": "revenue", "drcr_direction": "credit", "level": 1},
            {"code": "511", "name": "Doanh thu bán hàng và cung cấp dịch vụ", "account_type": "sales_revenue", "drcr_direction": "credit", "level": 2},
            {"code": "515", "name": "Doanh thu hoạt động tài chính", "account_type": "financial_revenue", "drcr_direction": "credit", "level": 2},
            {"code": "521", "name": "Các khoản giảm trừ doanh thu", "account_type": "sales_discounts", "drcr_direction": "debit", "level": 2},

            # CHI PHÍ SẢN XUẤT (PRODUCTION COSTS)
            {"code": "6", "name": "Chi phí sản xuất, kinh doanh", "account_type": "expense", "drcr_direction": "debit", "level": 1},
            {"code": "611", "name": "Chi phí nguyên liệu, vật liệu", "account_type": "cost_of_sales", "drcr_direction": "debit", "level": 2},
            {"code": "621", "name": "Chi phí nguyên vật liệu trực tiếp", "account_type": "cost_of_sales", "drcr_direction": "debit", "level": 3},
            {"code": "622", "name": "Chi phí nhân công trực tiếp", "account_type": "cost_of_sales", "drcr_direction": "debit", "level": 3},
            {"code": "623", "name": "Chi phí sử dụng máy thi công", "account_type": "cost_of_sales", "drcr_direction": "debit", "level": 3},
            {"code": "627", "name": "Chi phí sản xuất chung", "account_type": "cost_of_sales", "drcr_direction": "debit", "level": 3},
            {"code": "631", "name": "Giá thành sản xuất", "account_type": "cost_of_sales", "drcr_direction": "debit", "level": 2},
            {"code": "632", "name": "Giá vốn hàng bán", "account_type": "cost_of_goods_sold", "drcr_direction": "debit", "level": 2},
            {"code": "635", "name": "Chi phí tài chính", "account_type": "financial_expenses", "drcr_direction": "debit", "level": 2},

            # CHI PHÍ HOẠT ĐỘNG (OPERATING EXPENSES)
            {"code": "641", "name": "Chi phí bán hàng", "account_type": "selling_expenses", "drcr_direction": "debit", "level": 2},
            {"code": "642", "name": "Chi phí quản lý doanh nghiệp", "account_type": "administrative_expenses", "drcr_direction": "debit", "level": 2},

            # CHI PHÍ KHÁC (OTHER EXPENSES)
            {"code": "7", "name": "Thu nhập khác", "account_type": "revenue", "drcr_direction": "credit", "level": 1},
            {"code": "711", "name": "Thu nhập khác", "account_type": "other_operational_revenue", "drcr_direction": "credit", "level": 2},
            {"code": "811", "name": "Chi phí khác", "account_type": "other_operational_expenses", "drcr_direction": "debit", "level": 2},
            {"code": "821", "name": "Chi phí thuế TNDN", "account_type": "taxes_and_charges_expense", "drcr_direction": "debit", "level": 2},
            {"code": "8211", "name": "Chi phí thuế TNDN hiện hành", "account_type": "taxes_and_charges_expense", "drcr_direction": "debit", "level": 3},
            {"code": "82111", "name": "Chi phí thuế TNDN hiện hành (theo Luật)", "account_type": "taxes_and_charges_expense", "drcr_direction": "debit", "level": 4},
            {"code": "82112", "name": "Chi phí thuế TNDN bổ sung (GMT)", "account_type": "gmt_cit_expense", "drcr_direction": "debit", "level": 4},
            {"code": "8212", "name": "Chi phí thuế TNDN hoãn lại", "account_type": "taxes_and_charges_expense", "drcr_direction": "debit", "level": 3},

            # XÁC ĐỊNH KẾT QUẢ KINH DOANH
            {"code": "9", "name": "Xác định kết quả kinh doanh", "account_type": "net_profit", "drcr_direction": "credit", "level": 1},
            {"code": "911", "name": "Xác định kết quả kinh doanh", "account_type": "net_profit", "drcr_direction": "credit", "level": 2},

            # NGOÀI BẢNG (OFF-BALANCE SHEET)
            {"code": "001", "name": "Tài sản thuê ngoài", "account_type": "asset", "drcr_direction": "debit", "level": 1},
            {"code": "002", "name": "Vật tư, hàng hóa nhận giữ hộ", "account_type": "asset", "drcr_direction": "debit", "level": 1},
            {"code": "003", "name": "Hàng hóa nhận bán hộ, nhận ký gửi", "account_type": "asset", "drcr_direction": "debit", "level": 1},
            {"code": "004", "name": "Nợ khó đòi đã xử lý", "account_type": "asset", "drcr_direction": "debit", "level": 1},
        ],
    },
    "tt99_2025_sme": {
        "name": "SME Opt-in COA (TT99/2025)",
        "description": "Hệ thống tài khoản kế toán đơn giản hóa theo TT99/2025 (DNNVV chọn áp dụng)",
        "regime": "tt99_2025",
        "accounts": [
            {"code": "1", "name": "Tài sản", "account_type": "asset", "drcr_direction": "debit", "level": 1},
            {"code": "111", "name": "Tiền mặt", "account_type": "cash", "drcr_direction": "debit", "level": 2},
            {"code": "112", "name": "Tiền gửi ngân hàng", "account_type": "bank", "drcr_direction": "debit", "level": 2},
            {"code": "131", "name": "Phải thu khách hàng", "account_type": "account_receivable", "drcr_direction": "debit", "level": 2},
            {"code": "133", "name": "Thuế GTGT được khấu trừ", "account_type": "vat_input", "drcr_direction": "debit", "level": 2},
            {"code": "141", "name": "Tạm ứng", "account_type": "advance", "drcr_direction": "debit", "level": 2},
            {"code": "152", "name": "Nguyên liệu, vật liệu", "account_type": "inventory_goods", "drcr_direction": "debit", "level": 2},
            {"code": "153", "name": "Công cụ, dụng cụ", "account_type": "tools_and_accessories", "drcr_direction": "debit", "level": 2},
            {"code": "154", "name": "Chi phí SXKD dở dang", "account_type": "production_in_progress", "drcr_direction": "debit", "level": 2},
            {"code": "155", "name": "Thành phẩm", "account_type": "inventory_goods", "drcr_direction": "debit", "level": 2},
            {"code": "156", "name": "Hàng hóa", "account_type": "inventory_goods", "drcr_direction": "debit", "level": 2},
            {"code": "211", "name": "TSCĐ hữu hình", "account_type": "fixed_assets", "drcr_direction": "debit", "level": 2},
            {"code": "213", "name": "TSCĐ vô hình", "account_type": "intangible_assets", "drcr_direction": "debit", "level": 2},
            {"code": "214", "name": "Hao mòn TSCĐ", "account_type": "depreciation_expense", "drcr_direction": "credit", "level": 2},
            {"code": "242", "name": "Chi phí trả trước", "account_type": "prepaid_expenses", "drcr_direction": "debit", "level": 2},
            {"code": "2", "name": "Nợ phải trả", "account_type": "liability", "drcr_direction": "credit", "level": 1},
            {"code": "331", "name": "Phải trả người bán", "account_type": "accounts_payable", "drcr_direction": "credit", "level": 2},
            {"code": "333", "name": "Thuế và các khoản phải nộp", "account_type": "taxes_and_charges_payable", "drcr_direction": "credit", "level": 2},
            {"code": "3331", "name": "Thuế GTGT phải nộp", "account_type": "taxes_and_charges_payable", "drcr_direction": "credit", "level": 3},
            {"code": "3334", "name": "Thuế TNDN phải nộp", "account_type": "cit_payment", "drcr_direction": "credit", "level": 3},
            {"code": "3335", "name": "Thuế TNCN phải nộp", "account_type": "pit_payment", "drcr_direction": "credit", "level": 3},
            {"code": "334", "name": "Phải trả người lao động", "account_type": "expenses_payable", "drcr_direction": "credit", "level": 2},
            {"code": "338", "name": "Phải trả, phải nộp khác", "account_type": "accounts_payable", "drcr_direction": "credit", "level": 2},
            {"code": "341", "name": "Vay và nợ thuê tài chính", "account_type": "borrowings_from_credit_institutions", "drcr_direction": "credit", "level": 2},
            {"code": "4", "name": "Vốn chủ sở hữu", "account_type": "equity", "drcr_direction": "credit", "level": 1},
            {"code": "411", "name": "Vốn góp của CSH", "account_type": "capital_contributed", "drcr_direction": "credit", "level": 2},
            {"code": "421", "name": "LNST chưa phân phối", "account_type": "retained_earnings", "drcr_direction": "credit", "level": 2},
            {"code": "5", "name": "Doanh thu", "account_type": "revenue", "drcr_direction": "credit", "level": 1},
            {"code": "511", "name": "Doanh thu bán hàng", "account_type": "sales_revenue", "drcr_direction": "credit", "level": 2},
            {"code": "515", "name": "Doanh thu tài chính", "account_type": "financial_revenue", "drcr_direction": "credit", "level": 2},
            {"code": "6", "name": "Chi phí", "account_type": "expense", "drcr_direction": "debit", "level": 1},
            {"code": "621", "name": "Chi phí NVL trực tiếp", "account_type": "cost_of_sales", "drcr_direction": "debit", "level": 2},
            {"code": "622", "name": "Chi phí nhân công trực tiếp", "account_type": "cost_of_sales", "drcr_direction": "debit", "level": 2},
            {"code": "627", "name": "Chi phí sản xuất chung", "account_type": "cost_of_sales", "drcr_direction": "debit", "level": 2},
            {"code": "632", "name": "Giá vốn hàng bán", "account_type": "cost_of_goods_sold", "drcr_direction": "debit", "level": 2},
            {"code": "635", "name": "Chi phí tài chính", "account_type": "financial_expenses", "drcr_direction": "debit", "level": 2},
            {"code": "641", "name": "Chi phí bán hàng", "account_type": "selling_expenses", "drcr_direction": "debit", "level": 2},
            {"code": "642", "name": "Chi phí quản lý DN", "account_type": "administrative_expenses", "drcr_direction": "debit", "level": 2},
            {"code": "711", "name": "Thu nhập khác", "account_type": "other_operational_revenue", "drcr_direction": "credit", "level": 2},
            {"code": "811", "name": "Chi phí khác", "account_type": "other_operational_expenses", "drcr_direction": "debit", "level": 2},
            {"code": "821", "name": "Chi phí thuế TNDN", "account_type": "taxes_and_charges_expense", "drcr_direction": "debit", "level": 2},
            {"code": "8211", "name": "Chi phí thuế TNDN hiện hành", "account_type": "taxes_and_charges_expense", "drcr_direction": "debit", "level": 3},
            {"code": "911", "name": "Xác định kết quả KD", "account_type": "net_profit", "drcr_direction": "credit", "level": 2},
        ],
    },
    "tt133_2016_standard": {
        "name": "Standard COA (TT133/2016)",
        "description": "Hệ thống tài khoản kế toán theo Thông tư 133/2016/TT-BTC",
        "regime": "tt133_2016",
        "accounts": [
            {"code": "1", "name": "Tài sản", "account_type": "asset", "drcr_direction": "debit", "level": 1},
            {"code": "11", "name": "Tiền và các khoản tương đương tiền", "account_type": "asset", "drcr_direction": "debit", "level": 2},
            {"code": "111", "name": "Tiền mặt", "account_type": "cash", "drcr_direction": "debit", "level": 3},
            {"code": "1111", "name": "Tiền mặt VND", "account_type": "cash", "drcr_direction": "debit", "level": 4},
            {"code": "2", "name": "Nợ phải trả", "account_type": "liability", "drcr_direction": "credit", "level": 1},
            {"code": "331", "name": "Phải trả người bán", "account_type": "accounts_payable", "drcr_direction": "credit", "level": 2},
            {"code": "5", "name": "Doanh thu", "account_type": "revenue", "drcr_direction": "credit", "level": 1},
            {"code": "511", "name": "Doanh thu bán hàng", "account_type": "revenue", "drcr_direction": "credit", "level": 2},
            {"code": "6", "name": "Chi phí", "account_type": "expense", "drcr_direction": "debit", "level": 1},
            {"code": "621", "name": "Chi phí NVL trực tiếp", "account_type": "expense", "drcr_direction": "debit", "level": 2},
        ],
    },
}


class COATemplateUseCase:
    def __init__(self, session: Session):
        self.repo = COARepository(session)
        self.session = session

    def list_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": tid,
                "name": tpl["name"],
                "description": tpl["description"],
                "regime": tpl["regime"],
                "account_count": len(tpl["accounts"]),
            }
            for tid, tpl in STANDARD_TEMPLATES.items()
        ]

    def preview_template(self, template_id: str) -> Result:
        if template_id not in STANDARD_TEMPLATES:
            return Result.failure(VASValidationError(ErrorCodes.TEMPLATE_NOT_FOUND, template_id=template_id))
        tpl = STANDARD_TEMPLATES[template_id]
        return Result.success({
            "id": template_id,
            "name": tpl["name"],
            "description": tpl["description"],
            "regime": tpl["regime"],
            "accounts": [
                {
                    "code": a["code"],
                    "name": a["name"],
                    "account_type": a["account_type"],
                    "drcr_direction": a["drcr_direction"],
                    "level": a["level"],
                }
                for a in tpl["accounts"]
            ],
        })

    def apply_template(self, template_id: str, clear_existing: bool = False) -> Result:
        if template_id not in STANDARD_TEMPLATES:
            return Result.failure(VASValidationError(ErrorCodes.TEMPLATE_NOT_FOUND, template_id=template_id))
        template = STANDARD_TEMPLATES[template_id]

        if clear_existing:
            existing = self.repo.list_all()
            for acc in existing:
                self.repo.delete(acc.code)
            self.session.flush()

        created: List[str] = []
        errors: List[str] = []

        for acc_data in template["accounts"]:
            try:
                domain_acc = ChartOfAccounts(
                    code=acc_data["code"],
                    name=acc_data["name"],
                    account_type=AccountType(acc_data["account_type"]),
                    regime=AccountingRegime(template["regime"]),
                    drcr_direction=DCRDirection(acc_data["drcr_direction"]),
                    level=acc_data["level"],
                    currency=acc_data.get("currency", "VND"),
                    unit=acc_data.get("currency", "VND"),
                )
                result = self.repo.create(domain_acc)
                if result.is_success():
                    created.append(acc_data["code"])
                else:
                    errors.append(f"{acc_data['code']}: {result.error}")
            except Exception as e:
                errors.append(f"{acc_data['code']}: {e}")

        return Result.success({
            "template_id": template_id,
            "template_name": template["name"],
            "total_accounts": len(template["accounts"]),
            "created_count": len(created),
            "created": created,
            "error_count": len(errors),
            "errors": errors,
        })
