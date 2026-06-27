# basedpyright-as-pyright

Redirect the pyright engine to basedpyright, gated by the PYRIGHT env var.

## Installation

```bash
# Clone the repository
git clone https://github.com/bukzor/basedpyright-as-pyright
cd basedpyright-as-pyright

# Install dependencies
uv sync

# Install pre-commit hooks (optional but recommended)
uv run pre-commit install
```

## Usage

```bash
# Run the main script
uv run python main.py

# Or install and run as a package
uv pip install -e .
basedpyright_as_pyright
```

## Development

```bash
# Format code
uv run black .

# Type check
uv run pyright

# Run tests
uv run pytest

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the development commands above
5. Submit a pull request

## License

MIT License (or your preferred license)
