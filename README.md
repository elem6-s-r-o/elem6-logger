# ELEM6 Logger

[![PyPI version](https://badge.fury.io/py/elem6-logger.svg)](https://badge.fury.io/py/elem6-logger)
[![Python Version](https://img.shields.io/pypi/pyversions/elem6-logger)](https://pypi.org/project/elem6-logger)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A shared logging functionality for ELEM6 projects.

## Features

- Thread-safe singleton logger implementation
- Configurable log formatting and handlers
- Automatic log rotation and cleanup
- Support for extra fields in log messages
- Environment-aware configuration
- Console and file output support

## Installation

```bash
pip install elem6-logger
```

## Usage

Basic usage with default configuration:

```python
from elem6_logger import Elem6Logger

# Initialize logger with default configuration
Elem6Logger.initialize()

# Get logger instance
logger = Elem6Logger.get_logger(__name__)

# Use logger
logger.info("Hello, world!")
logger.error("Something went wrong", extra={"user_id": 123})
```

Custom configuration:

```python
from elem6_logger import Elem6Logger, LoggerConfig

# Create custom configuration
config = LoggerConfig(
    log_level="DEBUG",
    log_dir="custom_logs",
    retention_days=7,
    environment="development",
    extra_fields={"app_name": "my_app", "version": "1.0.0"}
)

# Initialize logger with custom configuration
Elem6Logger.initialize(config)

# Get logger instance
logger = Elem6Logger.get_logger(__name__)

# Use logger
logger.debug("Debug message")
```

## Configuration Options

The `LoggerConfig` class supports the following options:

- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_dir`: Directory for log files
- `module_name`: Module name for log files (defaults to script name)
- `retention_days`: Number of days to keep log files
- `format_string`: Log message format
- `date_format`: Date format in log messages
- `environment`: Environment name (production, development, etc.)
- `add_console_handler`: Enable console output
- `add_file_handler`: Enable file output
- `extra_fields`: Additional fields to include in log messages

## Log File Format

Log files are named using the pattern: `{module_name}_{YYYYMMDD_HHMM}.log`

Default log message format:
```
2024-03-14 12:34:56 - module_name - INFO - 1234 - 5678 - Message text
```

With extra fields:
```
2024-03-14 12:34:56 - module_name - INFO - 1234 - 5678 - Message text - app_name=my_app - version=1.0.0
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
