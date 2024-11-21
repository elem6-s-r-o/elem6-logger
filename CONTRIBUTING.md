# Contributing to elem6-logger

## Contribution Guidelines

1. **No Direct Commits to Main Branch**
   - All changes must go through pull requests
   - Direct commits to main branch are prohibited

2. **Development Process**
   - Create a new branch for your changes: `git checkout -b feature/change-name`
   - Make and test your changes
   - Commit changes with descriptive commit messages
   - Create a pull request to main branch

3. **Pull Request Requirements**
   - Must pass all tests
   - Must have 100% test coverage for new code
   - Must pass formatting checks (black)
   - Must pass import checks (isort)
   - Must pass type checks (mypy)

4. **Code Review**
   - Each pull request should be reviewed for:
     - Functionality
     - Tests
     - Documentation
     - Code quality

5. **Tests**
   - All new features must be tested
   - Tests must be readable and maintainable
   - Use pytest fixtures for shared test setup code

6. **Documentation**
   - All new features must be documented
   - Documentation must include usage examples
   - Keep README.md up to date

## Setting Up Development Environment

1. **Installing Dependencies**
```bash
# Install project and development dependencies
pip install -e ".[dev]"

# Install and set up pre-commit hooks
pre-commit install
```

2. **Pre-commit Hooks**
The project uses pre-commit hooks for automatic code formatting on commit:
- black: Python code formatting
- isort: import sorting

Pre-commit hooks run automatically on each commit. If formatting needs to be fixed:
1. Hook will fail and show errors
2. Changes are automatically fixed
3. Add fixed files back to staging (`git add`)
4. Retry commit

## Running Tests and Checks Manually

```bash
# Run tests
pytest tests/ --cov=src --cov-report=term-missing

# Manual formatting
black .
isort .

# Type checking
mypy src tests

# Run all pre-commit hooks
pre-commit run --all-files
```

## Commit Messages

Use the convention:

```
<type>: <description>

<detailed description>

<ticket number>
```

Types:
- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting, missing semicolons, etc.
- refactor: code refactoring
- test: adding or modifying tests
- chore: build changes, auxiliary tools, etc.

Example:
```
feat: add support for extra fields in logs

- Added extra fields configuration in LoggerConfig
- Extra fields are added to each log message
- Added tests to verify functionality

Ticket: #123
