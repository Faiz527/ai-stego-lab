"""
Database Module
===============
Manages PostgreSQL database operations:
  - User management (registration, authentication)
  - Operation logging
  - Activity tracking
  - Analytics data queries
"""

from .db_utils import (
    get_db_connection,
    initialize_database,
    add_user,
    verify_user,
    log_operation,
    log_activity,
)

# Import create_db for convenience
from . import create_db

__all__ = [
    'get_db_connection',
    'initialize_database',
    'add_user',
    'verify_user',
    'log_operation',
    'log_activity',
    'create_db',
]
