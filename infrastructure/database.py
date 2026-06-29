"""
Infrastructure layer for SmartACCT ERP Accounting application.
Database connection manager — delegates config to db_config.py.
"""

import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from infrastructure.db_config import SmartACCTDatabaseConfig, DatabaseError, RepositoryError


logger = logging.getLogger(__name__)


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
# Re-exports for backward compatibility
from infrastructure.db_config import (
    SmartACCTDatabaseConfig, DatabaseError, RepositoryError,
)
