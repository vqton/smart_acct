"""
Infrastructure layer for SmartACCT ERP Accounting application.
Implements database connection management, authentication middleware, and system utilities.
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool, PoolResetter
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class SmartACCTDatabaseConfig:
    """Configuration class for PostgreSQL database with connection pooling"""

    def __init__(self):
        self.database_url = self._get_database_url()
        self.pool_size = 20
        self.max_overflow = 30
        self.pool_recycle = 3600
        self.echo = False
        self.pool_timeout = 30

    def _get_database_url(self) -> str:
        """Get database URL with fallback for development"""
        return os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct"
        )

    def get_engine_kwargs(self) -> dict:
        """Get SQLAlchemy engine configuration"""
        return {
            "poolclass": QueuePool,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_recycle": self.pool_recycle,
            "pool_timeout": self.pool_timeout,
            "echo": self.echo,
            "future": True,
        }

    def get_session_kwargs(self) -> dict:
        """Get SQLAlchemy session configuration"""
        return {
            "expire_on_commit": False,
            "autocommit": False,
            "autoflush": False,
        }
class SmartACCTDatabaseManager:
    """Manages database connections with connection pooling and transaction handling"""

    def __init__(self, config: SmartACCTDatabaseConfig):
        self.config = config
        self._engine = None
        self._session_factory = None
        self._logger = logging.getLogger(__name__)

    def initialize(self) -> bool:
        """Initialize database connection pool"""
        try:
            self._engine = create_engine(
                self.config.database_url,
                **self.config.get_engine_kwargs()
            )

            self._session_factory = sessionmaker(
                bind=self._engine,
                **self.config.get_session_kwargs()
            )

            self._logger.info(
                f"SmartACCT database initialized with connection pool: "
                f"size={self.config.pool_size}, overflow={self.config.max_overflow}"
            )
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    def get_session(self):
        """Get a database session"""
        if self._session_factory is None:
            raise DatabaseError("Database not initialized")
        return self._session_factory()

    def execute_in_transaction(self, func, *args, **kwargs):
        """Execute a function within a database transaction"""
        session = self.get_session()
        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            self._logger.error(f"Transaction failed: {e}")
            raise RepositoryError(f"Transaction failed: {e}")
        finally:
            session.close()

    def close(self):
        """Close database connections"""
        if self._engine:
            self._engine.dispose()
            self._logger.info("SmartACCT database connections closed")

    def get_connection_stats(self) -> dict:
        """Get connection pool statistics"""
        if not self._engine:
            return {"status": "not_initialized"}

        pool = self._engine.pool
        return {
            "pool_type": type(pool).__name__,
            "pool_size": pool.size(),
            "checked_in": pool.checkedout(),
            "overflow": pool.overflow(),
        }
class JWTAuthenticationMiddleware:
    """Custom JWT authentication middleware for SmartACCT"""

    def __init__(self, app: Flask):
        self.app = app
        self._setup_paths()

    def _setup_paths(self):
        """Define protected and public paths"""
        self.protected_paths = [
            "/api/v1/*",
            "/api/reports/*",
            "/dashboard/*",
            "/accounting/*"
        ]

    def authenticate_request(self, request):
        """Authenticate incoming request using JWT"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None, "Unauthorized: No valid token provided"

        token = auth_header.split(" ")[1]
        try:
            from flask_jwt_extended import decode_token

            decoded_token = decode_token(token)
            user_id = decoded_token["sub"]

            # Store user info for request context
            request.user_id = user_id
            return user_id, None
        except Exception as e:
            return None, f"Unauthorized: Invalid token - {str(e)}"

    def initialize(self, app: Flask):
        """Initialize authentication middleware"""
        @app.before_request
        def before_request_func():
            if self._requires_auth():
                user_id, error = self.authenticate_request(request)
                if error:
                    return jsonify({"error": error}), 401

    def _requires_auth(self) -> bool:
        """Check if current request requires authentication"""
        from flask import request

        path = request.path
        return any(
            path.startswith protected_path.replace("*", "")
            for protected_path in self.protected_paths
        )
class SmartACCTCurrencyFormatter:
    """Vietnamese currency formatter for SmartACCT"""

    # Vietnamese currency rules
    VIETNAMESE_CURRENCIES = ["VND", "USD", "EUR", "JPY", "GBP"]

    @staticmethod
    def format_vietnamese_currency(amount: float, currency: str = "VND") -> str:
        """
        Format amount with Vietnamese currency conventions
        Example: 1,500,000.50 đ
        """
        if amount == 0:
            return "0,00 đ"

        # Round to 2 decimal places
        amount = round(amount, 2)

        # Format with Vietnamese decimal separator
        integer_part = int(abs(amount))
        decimal_part = int(round(abs(amount) * 100) % 100)

        # Format with dot as thousands separator
        integer_str = f"{integer_part:,}".replace(",", ".")

        # Add currency symbol
        symbol = "đ" if currency == "VND" else currency

        result = f"{integer_str},{decimal_part:02d} {symbol}"
        return result

    @staticmethod
    def format_vietnamese_number(amount: float) -> str:
        """
        Format number with Vietnamese grouping
        Example: 1,500,000
        """
        return f"{amount:,.0f}"

    @classmethod
    def validate_currency(cls, currency: str) -> bool:
        """Validate currency for Vietnamese accounting"""
        return currency.upper() in cls.VIETNAMESE_CURRENCIES
class DatabaseError(Exception):
    """Base exception for database operations"""

    pass
class RepositoryError(Exception):
    """Base exception for repository operations"""

    pass
class SmartACCTDatabase:
    """Base database model for SmartACCT"""

    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def save(self, session):
        """Save this entity to database"""
        session.add(self)
        session.commit()

    def delete(self, session):
        """Delete this entity from database"""
        session.delete(self)
        session.commit()

    def update(self, **kwargs):
        """Update entity attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
