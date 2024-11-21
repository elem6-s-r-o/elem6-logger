"""Tests for the ELEM6 Logger."""

import logging
import os
import pytest
from pathlib import Path
from elem6_logger import Elem6Logger, LoggerConfig


@pytest.fixture
def clean_logger():
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
def temp_log_dir(tmp_path):
    """Create temporary log directory."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


def test_singleton_pattern(clean_logger):
    """Test that logger follows singleton pattern."""
    logger1 = Elem6Logger()
    logger2 = Elem6Logger()
    assert logger1 is logger2


def test_default_initialization(clean_logger, temp_log_dir):
    """Test logger initialization with default config."""
    config = LoggerConfig(log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)
    logger = Elem6Logger.get_logger("test")

    assert logger.isEnabledFor(logging.INFO)
    assert not logger.isEnabledFor(logging.DEBUG)
    assert len(logging.getLogger().handlers) == 2  # Console and file handler


def test_custom_log_level(clean_logger, temp_log_dir):
    """Test setting custom log level."""
    config = LoggerConfig(log_level="DEBUG", log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)
    logger = Elem6Logger.get_logger("test")

    assert logger.isEnabledFor(logging.DEBUG)


def test_extra_fields(clean_logger, temp_log_dir):
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


def test_log_file_creation(clean_logger, temp_log_dir):
    """Test that log files are created correctly."""
    config = LoggerConfig(log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)
    logger = Elem6Logger.get_logger("test")

    logger.info("Test message")

    # Check that log file was created
    log_files = list(temp_log_dir.glob("*.log"))
    assert len(log_files) == 1


def test_log_cleanup(clean_logger, temp_log_dir):
    """Test cleanup of old log files."""
    # Create some old log files
    old_file = temp_log_dir / "test_20230101_0000.log"
    old_file.write_text("old log")

    config = LoggerConfig(log_dir=str(temp_log_dir), retention_days=0)  # Immediate cleanup
    Elem6Logger.initialize(config)

    # Old file should be cleaned up
    assert not old_file.exists()


def test_dynamic_log_level_change(clean_logger, temp_log_dir):
    """Test changing log level dynamically."""
    config = LoggerConfig(log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)
    logger = Elem6Logger.get_logger("test")

    assert logger.isEnabledFor(logging.INFO)
    assert not logger.isEnabledFor(logging.DEBUG)

    Elem6Logger.set_log_level("DEBUG")
    assert logger.isEnabledFor(logging.DEBUG)


def test_invalid_log_level(clean_logger, temp_log_dir):
    """Test handling of invalid log level."""
    with pytest.raises(ValueError):
        config = LoggerConfig(log_level="INVALID", log_dir=str(temp_log_dir))
        Elem6Logger.initialize(config)


def test_console_only_config(clean_logger):
    """Test logger with console output only."""
    config = LoggerConfig(add_file_handler=False)
    Elem6Logger.initialize(config)

    assert len(logging.getLogger().handlers) == 1  # Only console handler


def test_file_only_config(clean_logger, temp_log_dir):
    """Test logger with file output only."""
    config = LoggerConfig(log_dir=str(temp_log_dir), add_console_handler=False)
    Elem6Logger.initialize(config)

    assert len(logging.getLogger().handlers) == 1  # Only file handler


def test_multiple_loggers_same_config(clean_logger, temp_log_dir):
    """Test multiple logger instances share same configuration."""
    config = LoggerConfig(log_dir=str(temp_log_dir))
    Elem6Logger.initialize(config)

    logger1 = Elem6Logger.get_logger("test1")
    logger2 = Elem6Logger.get_logger("test2")

    assert logger1.isEnabledFor(logging.INFO) == logger2.isEnabledFor(logging.INFO)
    assert logger1.isEnabledFor(logging.DEBUG) == logger2.isEnabledFor(logging.DEBUG)
    assert logging.getLogger().handlers == logging.getLogger().handlers
