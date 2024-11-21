"""
Core logging functionality for ELEM6 Logger.

This module provides a thread-safe singleton logger implementation with enhanced capabilities
such as automatic log rotation, dynamic log level changes, and support for extra fields in log messages.

Example:
    >>> from elem6_logger import Elem6Logger, LoggerConfig
    >>> config = LoggerConfig(log_level="INFO", log_dir="logs")
    >>> Elem6Logger.initialize(config)
    >>> logger = Elem6Logger.get_logger("my_app")
    >>> logger.info("Application started")
"""

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Set, Type


@dataclass
class LoggerConfig:
    """
    Configuration class for ELEM6 Logger.

    This class holds all configuration options for the logger, including log level,
    directory for log files, retention period, and formatting options.

    Attributes:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to "INFO".
        log_dir: Directory where log files will be stored. Defaults to "logs".
        module_name: Optional name for the logging module. If None, derived from sys.argv[0].
        retention_days: Number of days to keep log files. Files older than this will be deleted.
        format_string: Format string for log messages. Includes timestamp, level, process ID, etc.
        date_format: Format for timestamps in log messages.
        environment: Environment name (e.g., "production", "development").
        add_console_handler: Whether to output logs to console. Defaults to True.
        add_file_handler: Whether to write logs to file. Defaults to True.
        extra_fields: Optional dictionary of extra fields to include in every log message.
    """

    log_level: str = "INFO"
    log_dir: str = "logs"
    module_name: Optional[str] = None
    retention_days: int = 30
    format_string: str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(thread)d - %(message)s"
    )
    date_format: str = "%Y-%m-%d %H:%M:%S"
    environment: str = "production"
    add_console_handler: bool = True
    add_file_handler: bool = True
    extra_fields: Optional[Dict[str, Any]] = None


class Elem6Logger:
    """
    Thread-safe singleton logger implementation with enhanced logging capabilities.

    This class provides a centralized logging solution that can be shared between
    different parts of a project. It supports features like:
    - Automatic log file rotation and cleanup
    - Dynamic log level changes at runtime
    - Extra fields in log messages
    - Console and file output
    - Environment-aware configuration

    The logger follows the singleton pattern, ensuring that only one instance
    exists throughout the application lifecycle.

    Example:
        >>> logger = Elem6Logger.get_logger("my_component")
        >>> logger.info("Component initialized")
        >>> logger.debug("Detailed debug information")

        # With extra fields
        >>> config = LoggerConfig(extra_fields={"version": "1.0.0"})
        >>> Elem6Logger.initialize(config)
        >>> logger.info("Starting up")  # Will include version=1.0.0 in output
    """

    _instance: Optional["Elem6Logger"] = None
    _initialized: bool = False
    _config: Optional[LoggerConfig] = None
    _numeric_level: int = logging.INFO
    _loggers: Set[logging.Logger] = set()

    def __new__(cls: Type["Elem6Logger"]) -> "Elem6Logger":
        """Create or return the singleton instance of Elem6Logger."""
        if cls._instance is None:
            cls._instance = super(Elem6Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the logger if not already initialized."""
        if self._initialized:
            return
        self._initialized = True

    @classmethod
    def initialize(cls, config: Optional[LoggerConfig] = None) -> None:
        """
        Initialize logger with configuration.

        This method sets up the logger with the provided configuration. If no configuration
        is provided, default values from LoggerConfig are used. The method validates the
        log level and configures both console and file handlers as specified.

        Args:
            config: Logger configuration. If None, default config will be used.

        Raises:
            ValueError: If an invalid log level is provided.
            RuntimeError: If logger initialization fails.
        """
        instance = cls()
        if config is None:
            config = LoggerConfig()

        # Validate and set log level first
        if config.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {config.log_level}")
        cls._numeric_level = getattr(logging, config.log_level.upper(), logging.INFO)

        cls._config = config
        cls._loggers.clear()  # Reset loggers on initialization
        instance._configure_logging()

    def _configure_logging(self) -> None:
        """
        Configure logging with the provided configuration.

        This internal method sets up the logging system according to the current
        configuration. It creates necessary directories, configures handlers,
        and sets up log formatting.

        Raises:
            RuntimeError: If called before logger initialization.
        """
        if not self._config:
            raise RuntimeError("Logger not initialized. Call initialize() first.")

        config = self._config

        # Create logs directory
        logs_dir = Path(config.log_dir)
        logs_dir.mkdir(exist_ok=True)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self._numeric_level)

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create formatter with extra fields if provided
        format_string = config.format_string
        if config.extra_fields:
            extra_fields = " ".join(f"- {k}={v}" for k, v in config.extra_fields.items())
            format_string = f"{format_string} - {extra_fields}"

        formatter = logging.Formatter(
            format_string,
            config.date_format,
        )

        # Determine module name
        module_name = config.module_name
        if not module_name:
            if sys.argv[0].startswith("-"):
                module_name = "app"
            else:
                module_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

        # Add file handler if enabled
        if config.add_file_handler:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            log_filename = logs_dir / f"{module_name}_{timestamp}.log"

            file_handler = logging.FileHandler(
                filename=log_filename,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(self._numeric_level)
            root_logger.addHandler(file_handler)

        # Add console handler if enabled
        if config.add_console_handler:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(self._numeric_level)
            root_logger.addHandler(console_handler)

        # Clean up old log files
        if config.add_file_handler:
            self._cleanup_old_logs(logs_dir, config.retention_days)

        # Log initial configuration
        root_logger.info(
            "Logger configured:"
            f"\n\tLog directory: {logs_dir}"
            f"\n\tLog level: {config.log_level}"
            f"\n\tRetention days: {config.retention_days}"
            f"\n\tFile format: {module_name}_YYYYMMDD_HHMM.log"
            f"\n\tEnvironment: {config.environment}"
            f"\n\tConsole handler: {config.add_console_handler}"
            f"\n\tFile handler: {config.add_file_handler}"
        )

    def _cleanup_old_logs(self, logs_dir: Path, retention_days: int) -> None:
        """
        Clean up log files older than retention_days.

        Args:
            logs_dir: Directory containing log files.
            retention_days: Number of days to keep log files. Files older than this will be deleted.
                          If negative, no files will be deleted.
        """
        if retention_days < 0:
            return

        current_time = datetime.now().timestamp()
        for log_file in logs_dir.glob("*.log"):
            try:
                file_age_days = (current_time - log_file.stat().st_mtime) / (24 * 3600)
                if file_age_days > retention_days:
                    log_file.unlink()
            except Exception:
                pass

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.

        This method returns a logger instance configured with the current settings.
        If the logger hasn't been initialized yet, it will be initialized with
        default settings.

        Args:
            name: Name for the logger instance.

        Returns:
            logging.Logger: Configured logger instance.
        """
        if cls._instance is None:
            cls()
        logger = logging.getLogger(name)
        logger.setLevel(cls._numeric_level)
        cls._loggers.add(logger)
        return logger

    @classmethod
    def set_log_level(cls, level: str) -> None:
        """
        Dynamically update the log level.

        This method allows changing the log level at runtime. The change affects
        all existing loggers and handlers.

        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Raises:
            ValueError: If an invalid log level is provided.
        """
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            root_logger = logging.getLogger()
            root_logger.error(f"Attempted to set invalid log level: {level}")
            raise ValueError(f"Invalid log level: {level}")

        cls._numeric_level = numeric_level

        # Update root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)

        # Update all handlers
        for handler in root_logger.handlers:
            handler.setLevel(numeric_level)

        # Update all tracked loggers
        for logger in cls._loggers:
            logger.setLevel(numeric_level)

        root_logger.info(f"Log level changed to: {level}")
