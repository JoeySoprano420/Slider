# Contributing to Slider

Thanks for your interest!

## Dev Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Running
```bash
python -m sdrc.driver build examples/hello.sdr -o build/hello.ll
lli build/hello.ll
```

## Style
- 4-space indentation, colon opens a suite.
- Run `pre-commit` before pushing.

## Tests
```bash
pytest
```

## Releases
- Tag: `vX.Y.Z`
- GitHub Actions will build artifacts and publish.
