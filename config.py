from typing import Optional
from pydantic.v1 import BaseModel, Field, validator
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.pool import QueuePool
import os
import re
class DatabaseSettings(BaseModel):
    """
    PostgreSQL database configuration with optimized connection pooling for on-premise
    """
    database_url: str = Field(
        default="postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct",
        description="PostgreSQL connection URI with connection pooling"
    )
    pool_size: int = Field(default=20, description="Minimum number of connections to maintain")
    max_overflow: int = Field(default=30, description="Maximum number of connections to create beyond pool_size")
    pool_recycle: int = Field(default=3600, description="Connection recycle time in seconds (1 hour)")
    echo: bool = Field(default=False, description="Enable SQL logging for debugging")

    @validator('database_url')
    def validate_database_url(cls, v):
        required_pattern = r'^postgresql\+psycopg2://[^:]+:[^@]+@[^:]+:\d+/[^?]+$'
        if not re.match(required_pattern, v):
            raise ValueError(
                "Database URL must be in format: "
                "postgresql+psycopg2://user:password@host:port/database"
            )
        return v

    def get_engine_kwargs(self) -> dict:
        """
        Get SQLAlchemy engine configuration for PostgreSQL connection pooling
        """
        return {
            "poolclass": QueuePool,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_recycle": self.pool_recycle,
            "pool_timeout": 30,
            "echo": self.echo,
            "future": True,
        }

    def get_session_kwargs(self) -> dict:
        """
        Get SQLAlchemy session configuration
        """
        return {
            "expire_on_commit": False,
            "autocommit": False,
            "autoflush": False,
        }
class JWTSettings(BaseModel):
    """
    JWT authentication settings for SmartACCT
    """
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
    """
    Application configuration settings for SmartACCT ERP Accounting System
    """
    # Application metadata
    app_name: str = Field(default="Smart ACCT", description="Application display name")
    app_version: str = Field(default="1.0.0", description="Application version number")
    app_description: str = Field(
        default="Vietnamese ERP Accounting Application for SMEs",
        description="Application description"
    )
    debug: bool = Field(default=False, description="Enable debug mode for development")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host (0.0.0.0 for LAN exposure)")
    port: int = Field(default=5000, description="Server port")

    # Database configuration
    database_url: Optional[str] = Field(None, description="PostgreSQL connection URI")
    database_echo: bool = Field(default=False, description="Enable SQL query logging")
    database_pool_size: int = Field(default=20, description="PostgreSQL connection pool size")

    # Authentication configuration
    secret_key: Optional[str] = Field(
        None, description="Flask secret key for session management"
    )
    jwt_secret_key: Optional[str] = Field(
        None, description="Secret key for JWT token signing"
    )

    # Security configuration
    max_content_length: int = Field(
        default=16 * 1024 * 1024, description="Maximum file upload size (16MB)"
    )

    # Vietnamese localization settings
    default_language: str = Field(default="vi", description="Default language code (vi for Vietnamese)")
    default_currency: str = Field(default="VND", description="Default currency code")
    number_format: str = Field(default="#,###,##0.00", description="Vietnamese number format pattern")

    # Vietnamese Accounting Standards compliance
    vas_compliance_level: str = Field(
        default="Circular133-2016", description="VAS compliance standard"
    )
    account_code_format: str = Field(
        default="1.2.3.4", description="Account code format (4 levels supported)"
    )

    # Performance optimization
    enable_query_cache: bool = Field(default=True, description="Enable database query caching")
    cache_timeout: int = Field(default=300, description="Cache timeout in seconds")

    @validator('secret_key')
    def validate_secret_key(cls, v):
        if v is None:
            v = os.getenv('SECRET_KEY')
        if not v:
            # Use a strong default key for development but warn
            v = "dev-secret-key-change-in-production-32chars"
        if len(v.strip()) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v.strip()

    @validator('jwt_secret_key')
    def validate_jwt_secret_key(cls, v):
        if v is None:
            v = os.getenv('JWT_SECRET_KEY')
        if not v:
            # Use a strong default key for development but warn
            v = "dev-jwt-secret-key-change-in-production-32chars"
        if len(v.strip()) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v.strip()

    @validator('database_url')
    def validate_database_url(cls, v):
        if v is None:
            v = os.getenv('DATABASE_URL')
        if not v:
            # Use a development PostgreSQL connection with docker setup
            v = "postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct"
        if 'postgresql' not in v and 'psycopg2' not in v:
            raise ValueError("Database URL must be PostgreSQL")
        return v

    @property
    def database_settings(self):
        """Get database settings instance"""
        return DatabaseSettings(
            database_url=self.database_url,
            pool_size=self.database_pool_size,
            echo=self.database_echo,
        )

    @property
    def jwt_settings(self):
        """Get JWT settings instance"""
        return JWTSettings(
            secret_key=self.jwt_secret_key or self.secret_key or os.getenv('JWT_SECRET_KEY', 'change-this-secret-key'),
        )

    @classmethod
    def from_env(cls):
        """
        Create AppSettings from environment variables
        """
        settings = {
            'debug': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            'secret_key': os.getenv('SECRET_KEY'),
            'jwt_secret_key': os.getenv('JWT_SECRET_KEY'),
            'database_url': os.getenv('DATABASE_URL'),
            'database_echo': os.getenv('DATABASE_ECHO', 'False').lower() == 'true',
            'database_pool_size': int(os.getenv('DATABASE_POOL_SIZE', '20')),
            'default_language': os.getenv('DEFAULT_LANGUAGE', 'vi'),
            'vas_compliance_level': os.getenv('VAS_COMPLIANCE_LEVEL', 'Circular133-2016'),
        }
        return cls(**settings)


# Global application settings instance
app_config = AppSettings.from_env()
