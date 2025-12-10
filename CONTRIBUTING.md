# Contributing to AI Startup Research Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
pytest
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for public functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable and function names

## Adding New Data Sources

To add a new data source:

1. Create a new collector in `agent/data_collectors/`
2. Implement the data collection logic
3. Add error handling and logging
4. Respect rate limits and robots.txt
5. Update the main agent to use the new collector

Example:

```python
# agent/data_collectors/new_source.py
from agent.utils.logger import setup_logger

logger = setup_logger(__name__)

class NewSourceCollector:
    def fetch_data(self, category: str) -> List[Dict]:
        logger.info(f"Fetching from new source: {category}")
        # Implementation here
        return []
```

## Adding New Processors

To add data processing functionality:

1. Create a new processor in `agent/processors/`
2. Implement processing logic
3. Add unit tests
4. Update documentation

## Testing

Write tests for new features:

```python
# tests/test_new_feature.py
def test_new_feature():
    agent = StartupResearchAgent()
    result = agent.new_feature()
    assert result is not None
```

## Documentation

- Update README.md for major features
- Add examples to EXAMPLES.md
- Include docstrings in code
- Update this CONTRIBUTING.md if workflow changes

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Create a pull request with clear description

## Code Review

All submissions require review. We'll look for:

- Code quality and style
- Test coverage
- Documentation
- Performance considerations
- Security implications

## Reporting Issues

When reporting issues, include:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

## Feature Requests

We welcome feature requests! Please:

- Check if the feature already exists
- Provide clear use case
- Describe expected behavior
- Consider implementation complexity

## Community Guidelines

- Be respectful and constructive
- Help others when possible
- Follow the code of conduct
- Keep discussions on-topic

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).
