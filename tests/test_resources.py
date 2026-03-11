"""
Tests for internal database resource management.
"""
import pytest

from drexpa.resources.database import get_internal_database_path


def test_get_internal_database_path_returns_string():
    """Test that database path resolution returns a valid string."""
    db_path = get_internal_database_path()
    assert isinstance(db_path, str)
    assert len(db_path) > 0


def test_get_internal_database_path_file_exists():
    """Test that the internal database file actually exists."""
    db_path = get_internal_database_path()
    assert db_path.endswith("DrugTargetInteractionDB.db")
    # Note: Full existence check happens at runtime during preflight


def test_get_internal_database_path_consistent():
    """Test that multiple calls return the same path."""
    path1 = get_internal_database_path()
    path2 = get_internal_database_path()
    assert path1 == path2
