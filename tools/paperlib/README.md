# paperlib

![ci status](https://harmattan-ai.ghe.com/hai/paperlib/actions/workflows/ci.yml/badge.svg)

papis based paper library tooling for the thesis

## Installation

This project uses [Poetry](https://python-poetry.org/docs/).

To install the project, run:

```bash
poetry install
```

If you need to contribute to the project, run this instead:

```bash
poetry install --with dev
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg
```

This will install pre-commit and pytest.
