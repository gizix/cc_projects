---
description: Run tests with coverage report
allowed-tools: Bash(*)
model: sonnet
---

Execute the test suite with coverage analysis and generate detailed reports.

## Usage

```bash
/coverage
```

## What This Does

1. Runs all tests with coverage tracking
2. Measures line and branch coverage
3. Generates HTML report in `htmlcov/`
4. Displays terminal coverage summary
5. Shows missing coverage areas

## Command

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing --cov-branch
```

## Output

Terminal shows:
- Coverage percentage per file
- Lines missing coverage
- Total coverage summary

HTML report provides:
- Visual coverage highlighting
- Clickable file navigation
- Detailed line-by-line coverage
- Access at `htmlcov/index.html`

## Coverage Goals

- Minimum 80% overall coverage
- 90%+ for critical paths (auth, security)
- 100% for utility functions
- Edge cases and error handling included

## Notes

- Open `htmlcov/index.html` in browser for detailed view
- Red lines indicate missing coverage
- Green lines are covered
- Yellow lines are partially covered (branches)
