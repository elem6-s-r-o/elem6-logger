"""Tests for the ELEM6 Logger."""

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Generator

import pytest

from elem6_logger import Elem6Logger, LoggerConfig


@pytest.fixture
def clean_logger() -> Generator[None, None, None]:
    """Reset logger state before each test."""
    Elem6Logger._instance = None
    Elem6Logger._initialized = False
    Elem6Logger._config = None
    yield
    # Cleanup after test
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)


@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Path:
    """Create temporary log directory."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


def test_singleton_pattern(clean_logger: None) -> None:
    """Test that logger follows singleton pattern."""
    logger1 = Elem6Logger()
    logger2 = Elem6Logger()
    assert logger1 is logger2


def test_default_initialization(clean_logger: None, temp_log_dir: Path) -> None:
    """Test logger initialization with default config."""
    config = LoggerConfig(log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)
    logger = Elem6Logger.get_logger("test")

    assert logger.isEnabledFor(logging.INFO)
    assert not logger.isEnabledFor(logging.DEBUG)
    assert len(logging.getLogger().handlers) == 2  # Console and file handler


def test_custom_log_level(clean_logger: None, temp_log_dir: Path) -> None:
    """Test setting custom log level."""
    config = LoggerConfig(log_level="DEBUG", log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)
    logger = Elem6Logger.get_logger("test")

    assert logger.isEnabledFor(logging.DEBUG)


def test_extra_fields(clean_logger: None, temp_log_dir: Path) -> None:
    """Test logging with extra fields."""
    config = LoggerConfig(
        log_dir=str(temp_log_dir), extra_fields={"app": "test_app", "version": "1.0.0"}
    )
    Elem6Logger.initialize(config)
    logger = Elem6Logger.get_logger("test")

    # Log a message and check if it contains extra fields
    log_file = next(temp_log_dir.glob("*.log"))
    logger.info("Test message")

    log_content = log_file.read_text()
    assert "app=test_app" in log_content
    assert "version=1.0.0" in log_content


def test_log_file_creation(clean_logger: None, temp_log_dir: Path) -> None:
    """Test that log files are created correctly."""
    config = LoggerConfig(log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)
    logger = Elem6Logger.get_logger("test")

    logger.info("Test message")

    # Check that log file was created
    log_files = list(temp_log_dir.glob("*.log"))
    assert len(log_files) == 1


def test_log_cleanup(clean_logger: None, temp_log_dir: Path) -> None:
    """Test cleanup of old log files."""
    # Create some old log files
    old_file = temp_log_dir / "test_20230101_0000.log"
    old_file.write_text("old log")

    config = LoggerConfig(log_dir=str(temp_log_dir), retention_days=0)  # Immediate cleanup
    Elem6Logger.initialize(config)

    # Old file should be cleaned up
    assert not old_file.exists()


def test_dynamic_log_level_change(clean_logger: None, temp_log_dir: Path) -> None:
    """Test changing log level dynamically."""
    config = LoggerConfig(log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)
    logger = Elem6Logger.get_logger("test")

    assert logger.isEnabledFor(logging.INFO)
    assert not logger.isEnabledFor(logging.DEBUG)

    Elem6Logger.set_log_level("DEBUG")
    assert logger.isEnabledFor(logging.DEBUG)


def test_invalid_log_level(clean_logger: None, temp_log_dir: Path) -> None:
    """Test handling of invalid log level."""
    with pytest.raises(ValueError):
        config = LoggerConfig(log_level="INVALID", log_dir=str(temp_log_dir))
        Elem6Logger.initialize(config)


def test_console_only_config(clean_logger: None) -> None:
    """Test logger with console output only."""
    config = LoggerConfig(add_file_handler=False)
    Elem6Logger.initialize(config)

    assert len(logging.getLogger().handlers) == 1  # Only console handler


def test_file_only_config(clean_logger: None, temp_log_dir: Path) -> None:
    """Test logger with file output only."""
    config = LoggerConfig(log_dir=str(temp_log_dir), add_console_handler=False)
    Elem6Logger.initialize(config)

    assert len(logging.getLogger().handlers) == 1  # Only file handler


def test_multiple_loggers_same_config(clean_logger: None, temp_log_dir: Path) -> None:
    """Test multiple logger instances share same configuration."""
    config = LoggerConfig(log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)

    logger1 = Elem6Logger.get_logger("test1")
    logger2 = Elem6Logger.get_logger("test2")

    assert logger1.isEnabledFor(logging.INFO) == logger2.isEnabledFor(logging.INFO)
    assert logger1.isEnabledFor(logging.DEBUG) == logger2.isEnabledFor(logging.DEBUG)
    assert logging.getLogger().handlers == logging.getLogger().handlers


def test_cleanup_error_handling(clean_logger: None, temp_log_dir: Path, monkeypatch: Any) -> None:
    """Test error handling during log cleanup."""
    # Create a log file that will raise an error when accessed
    old_file = temp_log_dir / "test_20230101_0000.log"
    old_file.write_text("old log")

    original_stat = Path.stat

    def mock_stat(self: Path) -> Any:
        if str(self).endswith("test_20230101_0000.log"):
            raise PermissionError("Access denied")
        return original_stat(self)

    # Mock Path.stat to raise an error only for our test file
    monkeypatch.setattr(Path, "stat", mock_stat)

    config = LoggerConfig(log_dir=str(temp_log_dir), retention_days=0)
    Elem6Logger.initialize(config)  # Should not raise an exception


def test_cleanup_unlink_error(clean_logger: None, temp_log_dir: Path, monkeypatch: Any) -> None:
    """Test error handling during log file deletion."""
    # Create a log file that will raise an error when deleted
    old_file = temp_log_dir / "test_20230101_0000.log"
    old_file.write_text("old log")

    original_unlink = Path.unlink

    def mock_unlink(self: Path, missing_ok: bool = False) -> None:
        if str(self).endswith("test_20230101_0000.log"):
            raise PermissionError("Cannot delete file")
        return original_unlink(self, missing_ok=missing_ok)

    # Mock Path.unlink to raise an error only for our test file
    monkeypatch.setattr(Path, "unlink", mock_unlink)

    config = LoggerConfig(log_dir=str(temp_log_dir), retention_days=0)
    Elem6Logger.initialize(config)  # Should not raise an exception


def test_invalid_dynamic_log_level(clean_logger: None, temp_log_dir: Path) -> None:
    """Test setting invalid log level dynamically."""
    config = LoggerConfig(log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)

    with pytest.raises(ValueError, match="Invalid log level: INVALID"):
        Elem6Logger.set_log_level("INVALID")


def test_get_logger_without_initialization(clean_logger: None) -> None:
    """Test getting logger without initialization."""
    logger = Elem6Logger.get_logger("test")
    assert logger.getEffectiveLevel() == logging.INFO


def test_negative_retention_days(clean_logger: None, temp_log_dir: Path) -> None:
    """Test logger with negative retention days."""
    # Create some old log files
    old_file = temp_log_dir / "test_20230101_0000.log"
    old_file.write_text("old log")

    config = LoggerConfig(log_dir=str(temp_log_dir), retention_days=-1)
    Elem6Logger.initialize(config)

    # File should not be deleted with negative retention days
    assert old_file.exists()


def test_successful_log_cleanup(clean_logger: None, temp_log_dir: Path) -> None:
    """Test successful cleanup of old log files."""
    # Create an old log file and set its modification time to 2 days ago
    old_file = temp_log_dir / "test_old.log"
    old_file.write_text("old log")
    old_time = time.time() - (2 * 24 * 3600)
    os.utime(old_file, (old_time, old_time))

    # Create a new log file
    new_file = temp_log_dir / "test_new.log"
    new_file.write_text("new log")

    # Initialize logger with 1 day retention
    config = LoggerConfig(log_dir=str(temp_log_dir), retention_days=1)
    logger = Elem6Logger()
    logger.initialize(config)

    # Manually trigger cleanup to ensure the code path is executed
    logger._cleanup_old_logs(temp_log_dir, 1)

    # Verify old file was deleted and new file remains
    assert not old_file.exists()
    assert new_file.exists()


def test_module_name_from_argv(clean_logger: None, temp_log_dir: Path) -> None:
    """Test getting module name from sys.argv[0]."""
    # Save original argv
    original_argv = sys.argv[0]
    try:
        # Set sys.argv[0] to a test value
        sys.argv[0] = "/path/to/test_script.py"

        config = LoggerConfig(log_dir=str(temp_log_dir))
        Elem6Logger.initialize(config)

        # Get the created log file
        log_files = list(temp_log_dir.glob("*.log"))
        assert len(log_files) == 1
        assert "test_script_" in log_files[0].name

    finally:
        # Restore original argv
        sys.argv[0] = original_argv


def test_module_name_from_argv_dash(clean_logger: None, temp_log_dir: Path) -> None:
    """Test getting module name when argv starts with dash."""
    original_argv = sys.argv[0]
    try:
        # Set sys.argv[0] to start with a dash
        sys.argv[0] = "-c"

        config = LoggerConfig(log_dir=str(temp_log_dir))
        Elem6Logger.initialize(config)

        # Get the created log file
        log_files = list(temp_log_dir.glob("*.log"))
        assert len(log_files) == 1
        assert "app_" in log_files[0].name

    finally:
        # Restore original argv
        sys.argv[0] = original_argv
