# Slider (.sdr) — The Twelvefold Language

Production-focused, optimization-first language that compiles AOT to LLVM and native code.
This repository contains the **compiler scaffold**, **runtime (ACS v1)**, **standard library seeds**,
**examples**, developer tooling, and a **docs site**.

> Repo home: https://github.com/JoeySoprano420/slider

---

## Quick Start

```bash
# 1) Create venv and install compiler deps
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Build and run the Hello sample
python -m sdrc.driver build examples/hello.sdr -o build/hello.ll
lli build/hello.ll
# or native:
clang build/hello.ll -o build/hello && ./build/hello
```

Expected:
```
Hail, Twelve!
x (dec): 34
sum 0..9: 45
nonzero
```

## Repository Layout
```
slider/
  sdrc/            # compiler (Python, llvmlite)
  runtime/         # ACS v1 runtime (C)
  std/             # standard library seeds/specs
  examples/        # .sdr examples (hello, ACS demo, FFI)
  docs/            # mkdocs docs site
  .github/         # CI, issue templates, PR templates
  containers/      # Dockerfile, devcontainer
  scripts/         # helper scripts
  profiles/        # build/opt profiles
  .vscode/         # editor setup
```

## Build the ACS demo (native)
```bash
python -m sdrc.driver build examples/demo_acs_v1.sdr -o build/demo_acs_v1.ll
clang build/demo_acs_v1.ll runtime/acs_v1.c -lpthread -o build/demo_acs_v1
./build/demo_acs_v1
```

## Docs
```bash
pip install mkdocs mkdocs-material
mkdocs serve
# open http://127.0.0.1:8000
```

## License
MIT © 2025 JoeySoprano420
