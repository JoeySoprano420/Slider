🚀 Slider (.sdr) v1.0.0 — The Optimization-Oriented Epoch

Release Date: 2025-09-01
Tag: v1.0.0

Slider (.sdr) reaches its first production-ready release.
This version fuses performance, safety, concurrency, and interoperability into a single Optimization-Oriented Programming Language.

✨ Highlights

Optimization-Oriented Programming (2-O-P): optimizations as first-class citizens.

ACS Runtime v1: Assigned-Channel-Superimposed concurrency with channels, timers, and N-way select.

Contracts & Memory Banks: contract-based safety, deterministic allocation (stack, heap, arena).

Base-12 Numerics (Dodecagrams): 0–9, t=10, e=11 literals with .b12 suffix.

Full AOT Compilation: .sdr → LLVM IR → Native with no JIT.

C ABI Interop: direct calls with packed FFI helpers; C++/Rust/Go/Ada/Fortran supported via bridges.

Security Features: compile-time regex validation, hardened builds, quarantined unsafe zones.

Docs & Examples: MkDocs-powered site, Hello demo, ACS demo, C FFI sample.

CI/CD: GitHub Actions for linting, builds, docs deploy, CodeQL, and GHCR container publishing.

S.U.E.T. License: official license integration across all files.

🔧 Language Features

Functions (fn), loops (for, while), conditionals (if/else, match).

Instances: statically mutable, scoped lifetimes, RAII drops.

Constants, variables, expressions, arithmetic, operators.

say(...) intrinsic for output.

Contracts: init, requires/ensures, localized checkpoints.

Scoped imports, namespaces, and resource banks.

🧩 Runtime & Concurrency

ACS Channels: typed message passing.

ACS Groups: N-way select across channels/timers.

ACS Timers: millisecond-precision scheduling.

Thread Safety: capabilities + channel-based transfers.

⚡ Performance

Startup: OS-loader bound; milliseconds.

Hot Paths: vectorization, tail-call compression, loop unrolling.

Dead Code Purging: expired/bloated code eliminated AOT.

PGO (Insight): resource- and runtime-aware profile-guided optimization.

Inlining Tapering & Coil/Uncoil Folding: precise optimization shaping.

🛡️ Safety

Rust/Ada-class safety in the safe subset.

Quarantined unsafe zones for FFI/pointer ops.

Hardened builds: stack protectors, CFI, RELRO, PIE.

Compile-time regex safety.

Reproducible builds & checksums.

🌍 Interoperability

Native: C ABI (direct, zero-cost for PODs).

C++: header/shim-based integration.

Rust/Go/Ada/Fortran: via C bridges.

Python: ctypes/cffi support.

Node.js: N-API compiled addons.

Wasm: --target wasm32-wasip1 for sandboxing.

📚 Documentation & Assets

Whitepaper (Hybrid Academic + Business): Slider_Whitepaper.pdf

Landing Pages:

Dark/Futuristic VACU-style (landing_dark.html)

Clean/Professional Open Source (landing_clean.md)

Day 1 Workshop Lab: 60-minute self-paced training with checkpoints + verifier.

Generated Video Storyboard: step-by-step teaching script.

🛠️ Tooling & Repo Setup

Compiler scaffold (sdrc) with CLI driver.

ACS runtime (runtime/acs_v1.c).

Standard library seeds (std/ specs: fmt, time, regex, checksum, math).

Examples: hello, ACS demo, C FFI sample.

Containers: Dockerfile + DevContainer.

CI/CD: GitHub Actions for build, docs, GHCR release.

Scripts: add author signature, license integration.

📝 License

Licensed under the S.U.E.T. License by Joey Soprano.

Full text: S.U.E.T. License

🔮 Roadmap

ACS Runtime v2: async I/O (epoll, kqueue, IOCP).

GPU kernels + accelerator backends.

Expanded standard library.

Package manager (sdrp) & runtime manager (sdrr).

Formal proof engines feeding contract system.

Incremental compiles, LSP, richer IDE integration.

📢 Tagline

“Slider (.sdr): C-class performance, Rust/Ada safety, Go/Erlang concurrency, Python clarity — fused under Optimization-Oriented Programming.”
