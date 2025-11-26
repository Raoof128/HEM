# Contributing

Thanks for considering a contribution! This project is an educational, production-style simulation of homomorphic encryption. Please keep security and clarity at the forefront.

## Getting Started
1. Fork the repository and create a feature branch.
2. Install dependencies with `pip install -e .[development]`.
3. Run `ruff` and `pytest` before submitting changes.

## Development Guidelines
- Prefer small, focused pull requests.
- Add docstrings and inline comments explaining *why* decisions were made.
- Keep the simulated nature of encryption clear to users.
- Avoid introducing heavy native dependencies unless necessary.

## Testing
```bash
pytest
```

## Code Style
- Python: PEP8, enforced via `ruff` and formatted with `black` (line length 100).
- JavaScript/HTML/CSS: keep concise, accessible, and lint-friendly.

## Security
- Never expose secret keys in code or documentation.
- Mark any demo-only endpoints clearly.

## Reporting Issues
Open an issue with a clear description and reproduction steps. Security-sensitive findings should follow the guidance in [SECURITY.md](SECURITY.md).
