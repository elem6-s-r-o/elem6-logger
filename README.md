# ELEM6 Logger

Thread-safe singleton logger implementation with enhanced capabilities for Python 3.9+.

## Features

- Thread-safe singleton pattern
- Flexible configuration (console/file)
- Support for extra fields in log messages
- Automatic log rotation and cleanup
- Dynamic log level changes at runtime
- Fully typed (mypy)
- 98% test coverage

## Installation

### From PyPI (recommended)

```bash
pip install elem6-logger
```

### From GitHub

To install the latest version directly from GitHub:

```bash
pip install git+https://github.com/elem6-s-r-o/elem6-logger.git
```

To install a specific version (e.g., v1.1.0):

```bash
pip install git+https://github.com/elem6-s-r-o/elem6-logger.git@v1.1.0
```

## Usage

### Basic Usage

```python
from elem6_logger import Elem6Logger, LoggerConfig

# Logger configuration
config = LoggerConfig(
    log_level="INFO",
    log_dir="logs",
    add_console_handler=True,
    add_file_handler=True
)

# Initialize logger
Elem6Logger.initialize(config)

# Get logger instance
logger = Elem6Logger.get_logger("my_app")

# Logging
logger.info("Application started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Extra Fields in Logs

```python
config = LoggerConfig(
    log_level="INFO",
    extra_fields={
        "app": "my_app",
        "version": "1.0.0",
        "environment": "production"
    }
)

Elem6Logger.initialize(config)
logger = Elem6Logger.get_logger("my_app")

# Log will include extra fields
logger.info("Message")  # Contains: app=my_app version=1.0.0 environment=production
```

### Dynamic Log Level Changes

```python
logger = Elem6Logger.get_logger("my_app")
logger.info("Visible message")
logger.debug("Invisible debug message")

# Change level to DEBUG
Elem6Logger.set_log_level("DEBUG")

logger.debug("Now visible debug message")
```

### Log Cleanup

```python
config = LoggerConfig(
    log_dir="logs",
    retention_days=7  # Automatically deletes logs older than 7 days
)

Elem6Logger.initialize(config)
```

## Development

To install development dependencies:

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Code Quality Checks

```bash
# Formatting
black .
isort .

# Type checking
mypy src tests
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
