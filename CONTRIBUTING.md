# Contributing to MoatMetrics

Thank you for your interest in contributing to MoatMetrics! We welcome all contributions, including bug reports, feature requests, documentation improvements, and code contributions.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
   ```bash
   git clone https://github.com/your-username/moatmetrics.git
   cd moatmetrics
   ```
3. Set up the development environment (see [Development Setup](#development-setup))
4. Create a new branch for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Making Changes

1. Make your changes following the [Code Style](#code-style) guidelines
2. Add tests for your changes
3. Run the test suite:
   ```bash
   pytest
   ```
4. Ensure all tests pass and there are no linting errors
5. Update documentation as needed

## Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Update the documentation if you've changed APIs
3. Add tests that cover your changes
4. Run the full test suite and ensure all tests pass
5. Submit a pull request with a clear description of your changes
6. Reference any related issues in your PR description

## Reporting Issues

When reporting issues, please include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Any relevant error messages or logs
- Your environment details (OS, Python version, etc.)

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all new code
- Keep functions small and focused on a single task
- Write docstrings for all public functions and classes
- Keep lines under 100 characters

## Documentation

- Update relevant documentation when making changes
- Follow the existing documentation style
- Ensure all new features are documented
- Update the [CHANGELOG.md](CHANGELOG.md) for significant changes

## License

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE).
