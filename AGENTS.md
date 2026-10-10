# AGENTS.md — HABESEARCHING

## Project Overview
Educational hybrid search algorithm: binary search fast path + linear safety net.
- **Python** (`python/IBESEARCHING.py`) — reference implementation with verbose tracing
- **C++** (`cpp/`) — C++23 templated implementation (planned)
- **Docs** (`docs/IBESEARCHING_notes.md`) — theory, fix list, port plan

## Core Rules
1. **Ask more, write less** — Clarify intent before implementing. No assumptions.
2. **No commits by agent** — Agent writes code and tests; user reviews and commits.
3. **One-line prompts** — Never separate `print()` + `input()`; combine into single `input("prompt: ")`.
4. **AGENTS.md is living** — Any new user instruction or rule gets added here immediately.

## Coding Standards

### Python
- Type hints on all functions
- Docstrings (Google style) for public functions
- Format: `black` (line-length 100)
- Lint: `ruff` (import sorting, unused imports, etc.)
- Target: Python 3.11+

### C++
- Standard: **C++23**
- Compiler flags: `-O2 -std=c++23 -Wall -Wextra -Wpedantic`
- Templates for generic `hybrid_search`
- `std::optional` for invariant tracking
- Half-open ranges `[low, high)` to avoid `size_t` underflow
- No logging in hot path (compile-time `TRACE` flag if needed)

## Test Requirements
- **Automated**: `python/test_ibesearching.py` (pytest)
  - Parametrized cases: sorted hit, small array, invariant violation, sorted miss
  - Edge cases: empty, single element, duplicates
  - Run with `verbose=False`
  - Benchmark smoke test (hit vs miss timing gap)
- **Interactive**: `python python/IBESEARCHING.py` → choice 1 (built-in demo)
- Both must pass before C++ port begins

## Branch Strategy
- `main` — protected, no direct pushes
- Feature branches: `feat/<short-desc>`
- PRs for review (user merges)

## Run Commands
```bash
# Interactive demo
python python/IBESEARCHING.py

# Automated tests
pytest python/test_ibesearching.py -v

# Format / lint
black python/
ruff check python/

# C++ (once implemented)
cmake -B build -S cpp -DCMAKE_CXX_STANDARD=23
cmake --build build -j
./build/tests
./build/bench
```

## Definition of Done (per task)
- Code compiles / runs without errors
- Tests pass (automated + interactive demo works)
- No new lint warnings
- User has reviewed output