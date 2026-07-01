import os
import re
import logging
from typing import Optional
from datetime import timedelta
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.pool import QueuePool


logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base exception for database operations"""
    pass


class RepositoryError(Exception):
    """Base exception for repository operations"""
    pass


class DatabaseSettings(BaseModel):
    """PostgreSQL database configuration with connection pooling"""
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct",
        )
    )
    pool_size: int = 20
    max_overflow: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    pool_timeout: int = 30

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if 'postgresql' not in v:
            raise ValueError("Database URL must use PostgreSQL dialect")
        return v

    def get_engine_kwargs(self) -> dict:
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
        return {
            "expire_on_commit": False,
            "autocommit": False,
            "autoflush": False,
        }

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        return cls(
            database_url=os.getenv("DATABASE_URL", "postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct"),
            pool_size=int(os.getenv("DATABASE_POOL_SIZE", "20")),
            echo=os.getenv("DATABASE_ECHO", "False").lower() == "true",
        )


class SmartACCTDatabaseConfig(DatabaseSettings):
    """Backward-compatible alias for DatabaseSettings with env-var defaults"""
    pass


class JWTSettings(BaseModel):
    """JWT authentication settings"""
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    access_token_expires: int = Field(default=24, description="Access token expiration in hours")
    algorithm: str = Field(default="HS256", description="JWT signing algorithm")

    @property
    def expires_delta(self) -> timedelta:
        return timedelta(hours=self.access_token_expires)


class AppSettings(BaseModel):
    """Application configuration settings for SmartACCT ERP"""
    app_name: str = "Smart ACCT"
    app_version: str = "1.0.0"
    app_description: str = "Vietnamese ERP Accounting Application for SMEs"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 5000

    database_url: Optional[str] = None
    database_echo: bool = False
    database_pool_size: int = 20

    secret_key: Optional[str] = None
    jwt_secret_key: Optional[str] = None

    max_content_length: int = 16 * 1024 * 1024

    default_language: str = "vi"
    default_currency: str = "VND"
    number_format: str = "#,###,##0.00"

    vas_compliance_level: str = "Circular133-2016"
    account_code_format: str = "1.2.3.4"

    enable_query_cache: bool = True
    cache_timeout: int = 300

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: Optional[str]) -> str:
        if v is None:
            v = os.getenv('SECRET_KEY')
        if not v:
            v = "dev-secret-key-change-in-production-32chars"
        if len(v.strip()) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v.strip()

    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret_key(cls, v: Optional[str]) -> str:
        if v is None:
            v = os.getenv('JWT_SECRET_KEY')
        if not v:
            v = "dev-jwt-secret-key-change-in-production-32chars"
        if len(v.strip()) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v.strip()

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> str:
        if v is None:
            v = os.getenv('DATABASE_URL')
        if not v:
            v = "postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct"
        if 'postgresql' not in v and 'psycopg2' not in v:
            raise ValueError("Database URL must be PostgreSQL")
        return v

    @property
    def database_settings(self) -> DatabaseSettings:
        return DatabaseSettings(
            database_url=self.database_url or os.getenv("DATABASE_URL", "postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct"),
            pool_size=self.database_pool_size,
            echo=self.database_echo,
        )

    @property
    def jwt_settings(self) -> JWTSettings:
        return JWTSettings(
            secret_key=self.jwt_secret_key or self.secret_key or os.getenv('JWT_SECRET_KEY', 'change-this-secret-key'),
        )

    @classmethod
    def from_env(cls) -> "AppSettings":
        return cls(
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY'),
            jwt_secret_key=os.getenv('JWT_SECRET_KEY'),
            database_url=os.getenv('DATABASE_URL'),
            database_echo=os.getenv('DATABASE_ECHO', 'False').lower() == 'true',
            database_pool_size=int(os.getenv('DATABASE_POOL_SIZE', '20')),
            default_language=os.getenv('DEFAULT_LANGUAGE', 'vi'),
            vas_compliance_level=os.getenv('VAS_COMPLIANCE_LEVEL', 'Circular133-2016'),
        )


# Global application settings instance
app_config = AppSettings.from_env()
