# Contributing to CollectiveBrain

Thank you for your interest in contributing to CollectiveBrain! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Docker (optional, for full stack testing)

### Setup Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CollectiveBrain_V1.git
   cd CollectiveBrain_V1
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   make install-dev
   # Or manually:
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov black flake8 mypy
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Follow the existing code style
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_consensus_engine.py -v
```

### 4. Format Code

```bash
# Format with black
make format

# Or manually
black *.py tests/ examples/
isort *.py tests/ examples/
```

### 5. Lint Code

```bash
make lint

# Or manually
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### 6. Commit Changes

```bash
git add .
git commit -m "Clear description of changes"
```

Follow conventional commit format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test updates
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 127 characters
- Use docstrings for all modules, classes, and functions

Example:
```python
def process_objective(self, objective: str, require_consensus: bool = True) -> Dict[str, Any]:
    """
    Process a high-level objective through the system.

    Args:
        objective: The high-level objective to process
        require_consensus: Whether to require consensus for finalization

    Returns:
        Complete execution result
    """
    # Implementation
```

### Documentation

- Update README.md for user-facing changes
- Update docs/ for architectural changes
- Add docstrings to all new functions/classes
- Include examples in documentation

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use descriptive test names
- Group related tests in classes

Example:
```python
class TestConsensusEngine:
    def test_calculate_min_agents(self):
        """Test minimum agents calculation (N >= 3f + 1)."""
        engine = DCBFTEngine(max_faulty_agents=1)
        assert engine.min_required_agents == 4
```

## Architecture Principles

Follow these core principles when contributing:

### 1. Spec-Driven Development
Every change should have a clear purpose and be documented.

### 2. Memory-First Design
Consider impact on memory layers for all features.

### 3. Consensus-Based Security
High-impact changes should go through consensus.

### 4. Deterministic Task Allocation
Maintain task ID uniqueness and proper routing.

### 5. Reflection-Based Validation
Use reflection tokens for quality assurance.

## Areas for Contribution

### High Priority
- GitHub Models API integration
- Production Redis/Milvus/Neo4j connectors
- Authentication and authorization
- Rate limiting
- Advanced observability (Prometheus metrics)

### Medium Priority
- WebSocket support for real-time updates
- Additional worker roles
- Enhanced error handling
- Performance optimizations

### Documentation
- Tutorial videos
- More usage examples
- Architecture diagrams
- API client libraries (JavaScript, Go, etc.)

### Testing
- Edge case coverage
- Load testing
- Integration tests with real backends
- End-to-end tests

## Pull Request Process

1. **Create PR** with clear title and description
2. **Link issues** being addressed
3. **Pass CI checks** (tests, linting)
4. **Review process**:
   - Address reviewer comments
   - Keep PR focused and small
   - Update based on feedback
5. **Merge** after approval

### PR Checklist

- [ ] Tests pass locally
- [ ] Code is formatted (black, isort)
- [ ] Linting passes
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)
- [ ] No merge conflicts
- [ ] Commit messages are clear

## Code Review Guidelines

### For Authors
- Keep PRs small and focused
- Respond to comments promptly
- Explain design decisions
- Be open to feedback

### For Reviewers
- Be constructive and respectful
- Focus on code quality and maintainability
- Ask questions when unclear
- Approve when satisfied

## Reporting Issues

### Bug Reports

Include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs
- Minimal reproduction code

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Impact on existing features

## Community

- Be respectful and inclusive
- Help others in discussions
- Share knowledge and insights
- Follow the code of conduct

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues/PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to CollectiveBrain! 🎉
