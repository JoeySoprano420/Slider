# Changelog

All notable changes to **Slider (.sdr)** will be documented here.  
This project follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2025-09-01
### Added
- **Language Core**
  - Functions, loops, conditionals, contracts, constants, variables, namespaces.
  - Base-12 numerics (`0–9, t=10, e=11`) with `.b12` suffix.
  - `say(...)` intrinsic for structured output.
  - Statically mutable instances with scoped lifetimes and RAII drops.

- **Optimization-Oriented Programming (2-O-P)**
  - Full AOT compilation → LLVM IR → native.
  - Dead code purging, tapered inlining, coil/uncoil loop folding.
  - Profile-guided optimization (Insight).
  - Vectorization, tail-call compression.

- **ACS Runtime v1**
  - Assigned-Channel-Superimposed concurrency model.
  - Typed channels, groups, timers, N-way `select`.
  - Deterministic, resource-scoped scheduling.

- **Safety**
  - Contract-based memory banks and checkpoints.
  - Quarantined unsafe zones for raw pointers/FFI.
  - Hardened builds (stack protectors, CFI, RELRO, PIE).
  - Compile-time regex validation.
  - Reproducible builds + checksums.

- **Interoperability**
  - Direct C ABI support (zero-cost for PODs).
  - C++ FFI via headers/shims.
  - Rust/Go/Ada/Fortran bridges via C.
  - Python ctypes/cffi, Node.js N-API.
  - Wasm target (`wasm32-wasip1`).

- **Tooling & Repo**
  - Compiler scaffold (`sdrc` CLI).
  - ACS runtime (`runtime/acs_v1.c`).
  - Standard library seeds (`std/`).
  - Examples: hello, ACS demo, C FFI sample.
  - CI/CD workflows: lint, build, CodeQL, GHCR publishing.
  - Containers: Dockerfile + DevContainer.
  - S.U.E.T. License integration.
  - Author signature script.

- **Docs & Training**
  - Whitepaper (hybrid academic + business).
  - Dark Futuristic landing page (`landing_dark.html`).
  - Clean Professional landing page (`landing_clean.md`).
  - Day 1 Workshop Lab (60 minutes, checkpoints, verifier).
  - Video storyboard script.

### Roadmap
- ACS Runtime v2: async I/O (epoll, kqueue, IOCP).
- GPU kernels and accelerator support.
- Expanded standard library.
- Package manager (`sdrp`), runtime manager (`sdrr`).
- Incremental compilation, IDE LSP integration.
- Formal proof engine integration.
