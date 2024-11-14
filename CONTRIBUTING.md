# Contributing to AI Tools Curator

First off, thank you for considering contributing to AI Tools Curator! 🎉

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if possible

### Suggesting Enhancements ✨

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests 🚀

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Process

1. **Setup Development Environment**
bash
Clone your fork
git clone https://github.com/your-username/ai-tools-curator.git
cd ai-tools-curator
Create virtual environment
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
Install dependencies
pip install -r requirements.txt

2. **Code Quality Standards**
bash
Format code
black src/ tests/
Sort imports
isort src/ tests/
Type checking
mypy src/
Run tests
pytest tests/

3. **Commit Messages**

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

* `feat:` New feature
* `fix:` Bug fix
* `docs:` Documentation only changes
* `style:` Code style changes
* `refactor:` Code refactoring
* `test:` Adding missing tests
* `chore:` Maintenance tasks

Example:
bash
git commit -m "feat: Add new quality scoring metric"

## Project Structure
ai-tools-curator/
├── data/ # Curated tools and digests
│ ├── tools/ # Individual tool data
│ └── digests/ # Weekly digests
├── docs/ # Generated static site
├── src/ # Source code
│ ├── tools_discovery/ # Tool discovery system
│ ├── github_publisher/ # Publishing system
│ └── utils/ # Shared utilities
├── templates/ # HTML templates
└── tests/ # Test suite

## Testing

* Write tests for new features
* Update tests when modifying existing features
* Ensure all tests pass before submitting PR
* Aim for high test coverage

## Documentation

* Update README.md if needed
* Document new features
* Update API documentation
* Include docstrings for new functions/classes

## Questions?

Feel free to open an issue with the tag `question` if you need any help!

Thank you for contributing! 🙏