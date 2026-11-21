# Contributing

Thank you for your interest in improving this project.

## Development Setup

1. Fork/clone the repository and create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and adjust settings as needed.
4. Run the API locally:
   ```bash
   uvicorn app.main:app --reload
   ```

## Code Quality

- Keep code readable and consistent with the existing project structure.
- Add or update tests for behavior changes.
- Run tests before submitting changes:
  ```bash
  pytest
  ```
- Run lint checks if available:
  ```bash
  ruff check .
  ```

## Pull Requests

- Describe the problem and solution clearly.
- Include test coverage for new features or bug fixes.
- Update documentation (`README.md`, `docs/`) when API behavior changes.
