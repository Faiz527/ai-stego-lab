"""
Tests Module
============
Comprehensive test suite for steganography application.
Organized into unit tests, integration tests, and fixtures.

Test Organization:
  - tests/unit/          : Unit tests (fast, isolated)
  - tests/integration/   : Integration tests (require external services)
  - tests/fixtures/      : Shared test data and utilities
  - conftest.py          : Pytest configuration and shared fixtures

Run all tests:
    pytest

Run specific test type:
    pytest -m unit
    pytest -m integration
    pytest -m "not requires_db"

Run with coverage:
    pytest --cov=src --cov-report=html
"""

__version__ = "1.0.0"
__author__ = "Faiz527"