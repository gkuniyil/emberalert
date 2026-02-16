"""
Database connection management.
Handles PostgreSQL connections and basic operations.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    """PostgreSQL database manager"""
    
    def __init__(self):
        # Create database engine
        # echo=True prints all SQL (useful for learning)
        self.engine = create_engine(
            settings.db.get_url(),
            echo=False,  # Set to True to see SQL queries
            pool_size=5,  # Connection pool
            max_overflow=10
        )
        
        # Session factory for ORM operations
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.
        Automatically commits or rolls back on error.
        
        Usage:
            with db.get_session() as session:
                session.execute(query)
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: dict = None):
        """Execute raw SQL query"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.fetchall()
    
    def init_schema(self):
        """Initialize database schema from SQL file"""
        try:
            with open('database/schema.sql', 'r') as f:
                sql = f.read()
            
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            raise

# Global database instance
db = Database()