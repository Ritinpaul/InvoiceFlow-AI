# Contributing to InvoiceFlow AI

Thank you for your interest in contributing to InvoiceFlow AI! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

---

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/invoiceflow-ai.git
cd invoiceflow-ai
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Set up database
cd ..
docker-compose up -d

# Seed database
python backend/seed_database.py
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

---

## Development Workflow

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

Examples:
- `feature/email-integration`
- `fix/duplicate-detection-bug`
- `docs/api-examples`

### Commit Message Guidelines

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Add: Email integration for invoice ingestion"
git commit -m "Fix: Duplicate detection false positives"
git commit -m "Update: API documentation with examples"
git commit -m "Refactor: Extract fraud scoring logic"

# Bad examples (avoid these)
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "wip"
```

---

## Coding Standards

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small (< 50 lines ideally)

**Example:**

```python
def calculate_risk_score(invoice_data: dict) -> float:
    """
    Calculate fraud risk score for an invoice.
    
    Args:
        invoice_data: Dictionary containing invoice information
        
    Returns:
        Risk score between 0.0 and 1.0
    """
    # Implementation here
    pass
```

### Type Hints

Use type hints for function parameters and return values:

```python
from typing import List, Dict, Optional

def process_invoices(invoices: List[Dict], limit: Optional[int] = None) -> Dict:
    pass
```

### Error Handling

Always use proper exception handling:

```python
try:
    result = process_invoice(invoice)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

---

## Testing Guidelines

### Running Tests

```bash
# Run all tests
cd backend
python test_pipeline.py
python test_db_workflow.py
python test_phase4.py

cd ../test_invoices
python test_phase5_e2e.py
```

### Writing Tests

- Add tests for all new features
- Ensure existing tests still pass
- Aim for high test coverage (80%+)
- Include edge cases and error scenarios

**Example Test:**

```python
def test_vision_agent_with_valid_invoice():
    """Test Vision Agent correctly extracts text from valid invoice"""
    agent = VisionAgent()
    result = agent.process("test_invoice.png")
    
    assert result["status"] == "success"
    assert len(result["text"]) > 0
    assert "INVOICE" in result["text"].upper()
```

---

## Pull Request Process

### 1. Ensure Quality

Before submitting a PR:
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No merge conflicts with main branch

### 2. Create Pull Request

1. Push your branch to GitHub
2. Go to the repository and click "New Pull Request"
3. Fill out the PR template with:
   - **Description**: What changes were made and why
   - **Testing**: How you tested the changes
   - **Screenshots**: If UI changes were made

### 3. PR Title Format

```
[Type] Brief description of changes

Examples:
[Feature] Add email integration for invoice ingestion
[Fix] Resolve duplicate detection false positives
[Docs] Add API usage examples to README
```

### 4. Review Process

- Maintainers will review your PR
- Address any feedback or requested changes
- Once approved, your PR will be merged

---

## What to Contribute

### Good First Issues

Look for issues labeled `good first issue` or `help wanted`:
- Documentation improvements
- Adding tests
- Bug fixes
- Code refactoring

### Feature Ideas

Consider contributing:
- **Email Integration**: Automatic invoice ingestion from email
- **Multi-language Support**: OCR for non-English invoices
- **Analytics Dashboard**: Advanced reporting and insights
- **Mobile App**: Invoice scanning on mobile devices
- **Integration APIs**: QuickBooks, Xero, SAP connectors

### Bug Reports

Found a bug? Please report it:
1. Check if it's already reported
2. Create a new issue with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots/logs if applicable

---

## Questions?

- Open an issue for general questions
- Tag maintainers in discussions
- Check existing documentation first

---

Thank you for contributing to InvoiceFlow AI! 🎉
