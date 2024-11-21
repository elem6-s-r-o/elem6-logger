"""Core logging functionality."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Set
from dataclasses import dataclass


@dataclass
class LoggerConfig:
    """Configuration for logger."""
    log_level: str = "INFO"
    log_dir: str = "logs"
    module_name: Optional[str] = None
    retention_days: int = 30
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(thread)d - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    environment: str = "production"
    add_console_handler: bool = True
    add_file_handler: bool = True
    extra_fields: Optional[Dict[str, Any]] = None


class Elem6Logger:
    """
    Thread-safe singleton logger implementation with enhanced logging capabilities.
    Can be shared between different projects.
    """

    _instance = None
    _initialized = False
    _config: Optional[LoggerConfig] = None
    _numeric_level: int = logging.INFO
    _loggers: Set[logging.Logger] = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Elem6Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    @classmethod
    def initialize(cls, config: Optional[LoggerConfig] = None) -> None:
        """
        Initialize logger with configuration.
        
        Args:
            config: Logger configuration. If None, default config will be used.
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
        """Configure logging with the provided configuration."""
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
        """Clean up log files older than retention_days."""
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
        """Get a logger instance with the specified name."""
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

        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
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
