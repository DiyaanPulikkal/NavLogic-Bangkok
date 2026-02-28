# Bangkok Public Transport

Automated tests for LLM intent extraction, Prolog reasoning, name resolution, and exhaustive routing.

## Quick Start

Install dependencies:

```sh
pip install -r requirements.txt
```

Run all tests (includes exhaustive ordered route pairs):

```sh
pytest
```

Run only the exhaustive route test:

```sh
pytest test/test_exhaustive_routes.py
```

Run the standalone exhaustive route runner:

```sh
python scripts/run_exhaustive_routes.py
```

## Notes

- Exhaustive routing checks all ordered station pairs excluding same-station pairs.
- Tests validate structural correctness (path continuity and cost) rather than output formatting.

