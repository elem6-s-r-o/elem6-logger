# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of elem6-logger
- Thread-safe singleton logger implementation
- Configurable log formatting and handlers
- Automatic log rotation and cleanup
- Support for extra fields in log messages
- Environment-aware configuration
- Console and file output support
- Comprehensive test suite
- GitHub Actions for CI/CD
- PyPI package publishing

### Changed
- Zjednodušen CI/CD workflow odstraněním block-merge jobu
- Vylepšeny typové anotace v celém projektu pro lepší podporu mypy

### Deprecated
- N/A

### Removed
- Block-merge job z GitHub Actions workflow

### Fixed
- Doplněny chybějící typové anotace v logger.py a test_logger.py

### Security
- N/A

## [0.1.0] - 2024-03-14

### Added
- Initial project structure
- Basic logging functionality
- Documentation
