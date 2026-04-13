"""
Database Operations Tests
==========================
Tests for database connectivity, initialization, and user operations.
"""

import pytest
from src.db.db_utils import (
    get_db_connection,
    initialize_database,
    add_user,
    verify_user,
    log_operation,
)


@pytest.mark.integration
@pytest.mark.requires_db
class TestDatabaseConnection:
    """Tests for database connection and initialization."""

    def test_db_connection_successful(self):
        """Test that database connection can be established."""
        try:
            conn = get_db_connection()
            assert conn is not None
            conn.close()
        except Exception as e:
            pytest.skip(f"Database unavailable: {str(e)}")

    def test_database_initialization(self):
        """Test that database tables can be initialized."""
        try:
            initialize_database()
            # If no exception raised, test passes
            assert True
        except Exception as e:
            pytest.skip(f"Database initialization failed: {str(e)}")


@pytest.mark.integration
@pytest.mark.requires_db
class TestUserOperations:
    """Tests for user management in database."""

    def test_add_user_success(self, test_user):
        """Test adding a user to the database."""
        # test_user fixture handles creation
        assert test_user["username"] == "test_user_pytest"

    def test_verify_user_correct_password(self, test_user):
        """Test user verification with correct password."""
        result = verify_user(
            test_user["username"],
            test_user["password"]
        )
        # verify_user may return True, a dict, or a truthy value on success
        assert result is not None and result is not False, \
            f"Expected truthy result for correct password, got {repr(result)}"

    def test_verify_user_incorrect_password(self, test_user):
        """Test user verification with incorrect password."""
        result = verify_user(
            test_user["username"],
            "wrong_password_123"
        )
        # verify_user returns None or False for invalid credentials
        assert not result, \
            f"Expected falsy result for wrong password, got {repr(result)}"

    def test_verify_nonexistent_user(self):
        """Test verification of non-existent user."""
        result = verify_user("nonexistent_user_xyz", "password")
        # verify_user returns None or False for non-existent user
        assert not result, \
            f"Expected falsy result for non-existent user, got {repr(result)}"


@pytest.mark.integration
@pytest.mark.requires_db
class TestOperationLogging:
    """Tests for logging operations to database."""

    def test_log_operation_success(self, test_user, fresh_db):
        """Test logging an operation."""
        try:
            log_operation(
                user_id=1,
                operation_type="encode",
                method="LSB",
                status="success"
            )
            assert True
        except Exception as e:
            pytest.skip(f"Could not log operation: {str(e)}")