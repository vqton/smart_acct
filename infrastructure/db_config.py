import os
import logging
from sqlalchemy.pool import QueuePool


logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base exception for database operations"""
    pass


class RepositoryError(Exception):
    """Base exception for repository operations"""
    pass


class SmartACCTDatabaseConfig:
    def __init__(self):
        self.database_url = self._get_database_url()
        self.pool_size = 20
        self.max_overflow = 30
        self.pool_recycle = 3600
        self.echo = False
        self.pool_timeout = 30

    def _get_database_url(self) -> str:
        return os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://smartacct:smartacct123@localhost:5432/smartacct"
        )

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
