from flask import Flask, jsonify


class JWTAuthenticationMiddleware:
    def __init__(self, app: Flask):
        self.app = app
        self._setup_paths()

    def _setup_paths(self):
        self.protected_paths = [
            "/api/v1/*",
            "/api/reports/*",
            "/dashboard/*",
            "/accounting/*"
        ]

    def authenticate_request(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None, "Unauthorized: No valid token provided"
        token = auth_header.split(" ")[1]
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = decoded_token["sub"]
            request.user_id = user_id
            return user_id, None
        except Exception as e:
            return None, f"Unauthorized: Invalid token - {str(e)}"

    def initialize(self, app: Flask):
        @app.before_request
        def before_request_func():
            if self._requires_auth():
                user_id, error = self.authenticate_request(request)
                if error:
                    return jsonify({"error": error}), 401

    def _requires_auth(self) -> bool:
        from flask import request
        path = request.path
        return any(
            path.startswith(protected_path.replace("*", ""))
            for protected_path in self.protected_paths
        )


class SmartACCTCurrencyFormatter:
    VIETNAMESE_CURRENCIES = ["VND", "USD", "EUR", "JPY", "GBP"]

    @staticmethod
    def format_vietnamese_currency(amount: float, currency: str = "VND") -> str:
        if amount == 0:
            return "0,00 đ"
        amount = round(amount, 2)
        integer_part = int(abs(amount))
        decimal_part = int(round(abs(amount) * 100) % 100)
        integer_str = f"{integer_part:,}".replace(",", ".")
        symbol = "đ" if currency == "VND" else currency
        return f"{integer_str},{decimal_part:02d} {symbol}"

    @staticmethod
    def format_vietnamese_number(amount: float) -> str:
        return f"{amount:,.0f}"

    @classmethod
    def validate_currency(cls, currency: str) -> bool:
        return currency.upper() in cls.VIETNAMESE_CURRENCIES
