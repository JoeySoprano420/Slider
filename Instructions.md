# Slider (.sdr) — Zero-to-Running Guide (Absolute Beginner Edition)

This sheet gets you from **nothing** to **running code** in \~10–15 minutes. No prior LLVM/compilers knowledge required. Follow the steps in order.

---

## What you’ll do

1. Install the small set of tools
2. Open the ready-made Slider repo scaffold
3. Build and run “Hello, Twelve!”
4. Build and run the ACS (channels/concurrency) demo
5. Understand the folder layout
6. Learn 10 tiny language examples you can copy/paste
7. Fix common errors fast
8. Know your next steps

---

## 1) Install the basics (one-time)

### macOS (Apple Silicon or Intel)

```bash
# 1) Install Homebrew if you don’t have it:
#/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2) Tools
brew install python llvm git

# 3) (optional) make clang/lli easy to find in PATH
echo 'export PATH="/opt/homebrew/opt/llvm/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Ubuntu/Debian Linux

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip llvm clang git
```

### Windows 10/11

1. Install **Python 3.10+** from python.org (check “Add Python to PATH”)
2. Install **LLVM** from the official installer (ensure `clang.exe` and `lli.exe` are on PATH)
3. Install **Git for Windows**
4. Use **PowerShell** or **Git Bash** for the commands below (PowerShell shown).

---

## 2) Get the Slider repo scaffold

You have a zip named `slider_github_repo.zip` from our prior step. Put it wherever you like (e.g., Desktop), then:

### macOS/Linux

```bash
unzip slider_github_repo.zip
cd slider-repo   # (or cd slider if that’s the folder name after unzip)
```

### Windows (PowerShell)

```powershell
tar -xf slider_github_repo.zip
cd slider-repo   # or cd slider
```

---

## 3) Create a Python virtual environment (keeps things clean)

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> If `pip install` warns about `llvmlite`: make sure LLVM is installed and you’re on Python 3.10+.

---

## 4) Run your first Slider program (“Hello, Twelve!”)

From the repo root:

```bash
# Build .sdr -> LLVM IR (.ll)
python -m sdrc.driver build examples/hello.sdr -o build/hello.ll

# Run with LLVM’s interpreter
lli build/hello.ll
```

You should see:

```
Hail, Twelve!
x (dec): 34
sum 0..9: 45
nonzero
```

> Prefer a single command? Use the Makefile (macOS/Linux):

```bash
make hello
```

---

## 5) Run the concurrency demo (ACS v1: channels, select, timers)

```bash
# Build Slider source to IR
python -m sdrc.driver build examples/demo_acs_v1.sdr -o build/demo_acs_v1.ll

# Compile + link the ACS C runtime and run native
clang build/demo_acs_v1.ll runtime/acs_v1.c -lpthread -o build/demo_acs_v1
./build/demo_acs_v1
```

Expected output (varies):

```
ACS v1 demo — group select with timer (packed)
ix: 2 val: 1
ix: 2 val: 2
...
```

> On Windows with PowerShell:

```powershell
python -m sdrc.driver build examples\demo_acs_v1.sdr -o build\demo_acs_v1.ll
clang.exe build\demo_acs_v1.ll runtime\acs_v1.c -o build\demo_acs_v1.exe
.\build\demo_acs_v1.exe
```

---

## 6) What’s in this repo (map)

```
sdrc/            # the tiny compiler scaffold (lexer, parser, IR generator, CLI)
runtime/         # ACS v1 runtime in C (channels, select, timers)
std/             # standard library specs/seeds (fmt, time, regex, checksum, math)
examples/        # hello.sdr, ACS demo, C interop bits
docs/            # mkdocs site (run: mkdocs serve)
.github/         # CI (build & docs), release workflow, issue templates
containers/      # dev Dockerfile, devcontainer
.vscode/         # tasks & extension recommendations
Makefile         # easy build shortcuts (hello, acs)
requirements.txt # Python deps (llvmlite, mkdocs)
pyproject.toml   # installable package: `sdrc` command
```

---

## 7) 10 tiny Slider snippets you can paste into `examples/hello.sdr`

### 1) Print a string + numbers

```sdr
fn main():
    say("Hello", 123, 456)
```

### 2) Base-12 literal (t=10, e=11)

```sdr
fn main():
    let x:i64 = 2t.b12   # decimal 34
    say("x:", x)
```

### 3) For-loop and sum

```sdr
fn main():
    let s:i64 = 0
    for i in 0..10:
        let s:i64 = s + i
    say("sum 0..9:", s)
```

### 4) If/else

```sdr
fn main():
    let n:i64 = 5
    if n:
        say("nonzero")
    else:
        say("zero")
```

### 5) Functions with return

```sdr
fn add(a:i64, b:i64):
    return a + b

fn main():
    say("add:", add(7,5))
```

### 6) Call C via C ABI (already in repo under `examples/cdeps`)

```sdr
extern "C" fn c_add(a:i32, b:i32) -> i32

fn main():
    say("C add(7,5) =", c_add(7,5))
```

Compile native with the C file at link time:

```bash
python -m sdrc.driver build examples/hello.sdr -o build/hello.ll
clang build/hello.ll examples/cdeps/add.c -o build/hello && ./build/hello
```

### 7) Minimal while-loop

```sdr
fn main():
    let i:i64 = 0
    while i < 3:
        say("i:", i)
        let i:i64 = i + 1
```

### 8) Simple arithmetic

```sdr
fn main():
    say("mul:", 6 * 7, "sub:", 10 - 3)
```

### 9) Two functions, call chain

```sdr
fn square(x:i64): return x * x
fn main(): say(square(12))
```

### 10) (Preview) ACS timer from Slider (uses FFI behind the scenes)

```sdr
fn main():
    let t:i64 = acs_timer_new(100, 1)         # every 100ms
    let g:i64 = acs_group_new()
    acs_group_add(g, t)
    let i:i64 = 0
    while i < 5:
        let p:i64 = acs_group_select_recv_i64_packed(g, 1000)
        if acs_unpack_sel_status(p) == 0:
            say("tick:", acs_unpack_sel_value(p))
            let i:i64 = i + 1
```

Build + link like the ACS demo (with `runtime/acs_v1.c`).

---

## 8) Common errors & super-quick fixes

**“`lli: command not found`”**
→ Install LLVM and ensure its `bin` directory is on your PATH.

* macOS (brew): `echo 'export PATH="/opt/homebrew/opt/llvm/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc`
* Ubuntu: `sudo apt-get install llvm`
* Windows: re-run LLVM installer, check “Add to PATH”.

**`clang: command not found`**
→ Install LLVM/clang and add to PATH (same as above).

**`pip install llvmlite` fails**
→ Make sure you’re on Python 3.10+ and have LLVM installed. If still stuck, try:
`pip install --upgrade pip wheel setuptools` then re-install requirements.

**Link error: undefined reference to `c_add`**
→ Include the C file when building native:
`clang build/app.ll examples/cdeps/add.c -o build/app`

**Windows cannot execute .sh**
→ Use PowerShell commands (provided) or Git Bash.

**Weird terminal characters**
→ Set your terminal to UTF-8. On Windows Terminal, set UTF-8 encoding.

---

## 9) Use VS Code tasks (optional but comfy)

Open the repo in VS Code. Then:
**Terminal → Run Task →** `sdrc: build hello IR`, then **Run Task →** `run hello (lli)`.

The `.vscode/tasks.json` is already included.

---

## 10) See the docs locally

```bash
pip install mkdocs mkdocs-material
mkdocs serve
# http://127.0.0.1:8000
```

This site explains language ideas, ACS, FFI, optimization philosophy, and security features.

---

## 11) Ready to share? Push to GitHub

```bash
git init
git branch -M main
git add .
git commit -m "feat: initial Slider scaffold"
git remote add origin https://github.com/JoeySoprano420/slider.git
git push -u origin main
```

* CI will auto-build samples and deploy docs to GitHub Pages.
* Tag a release as `v0.1.0` to publish artifacts.

---

## 12) Your 3 next moves (fast wins)

1. **Change the message** in `examples/hello.sdr` and rebuild → feel the loop.
2. **Add a second C function** in `examples/cdeps`, call it from Slider, link native.
3. **Duplicate the ACS demo**, change timer interval and iterations, re-run.

---

## Cheat-Sheet Commands (copy/paste)

**Build IR + run (hello):**

```bash
python -m sdrc.driver build examples/hello.sdr -o build/hello.ll
lli build/hello.ll
```

**Build native (hello + C dep):**

```bash
clang build/hello.ll examples/cdeps/add.c -o build/hello && ./build/hello
```

**ACS demo (IR → native):**

```bash
python -m sdrc.driver build examples/demo_acs_v1.sdr -o build/demo_acs_v1.ll
clang build/demo_acs_v1.ll runtime/acs_v1.c -lpthread -o build/demo_acs_v1
./build/demo_acs_v1
```

**One-shot (Linux/macOS):**

```bash
make hello
make acs
```

---

## You’re up!

You can now:

* Build & run Slider code
* Call C from Slider
* Use channels/timers via the ACS runtime
* Browse docs and extend the examples

