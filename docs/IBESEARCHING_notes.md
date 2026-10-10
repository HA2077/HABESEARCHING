# IBESEARCHING: Notes, Fix List and C/C++ Port Plan

Adaptive hybrid search: binary search as the fast path, linear search as the safety net.

---

## 1. The core result

**No algorithm can detect a single out-of-place element in an unverified array with fewer than Ω(n) reads.**

Adversary argument: if you read only k elements (k constant or O(log n)), an adversary corrupts one index you did not read. Everything you saw still looks sorted, so you cannot tell the two arrays apart. Your "check the first half, the boundary, the second half" idea is just three more probes, and the adversary hides the bad element somewhere else.

Why Case 3 (`[1, 2, 999, 4, ...]`, target 999) cannot be fixed by a trick: binary search never touches index 2, so nothing it sees can reveal the 999.

### Options that actually work

1. **Document the precondition.** Input must be sorted (what `bisect` and `std::binary_search` do).
2. **Verify on a miss.** Hits stay O(log n), misses become O(n).
3. **Check once, cache the flag.** One O(n) sortedness check, then reuse. Pays off after roughly n / log n queries.
4. **Random sampling (property testing).** Catches arrays that are far from sorted in O(1/ε) samples. Cannot catch a single bad element.

### The chosen design

- **Hit:** O(log n) on sorted data. Any returned index is correct by construction, because `arr[idx] == target`.
- **Miss:** O(n). A miss cannot be self-certified, so the safety net must run.
- State this honestly in the docs: *misses on possibly-unsorted data must be O(n).*

---

## 2. The algorithm (Python reference version)

```python
def LinearSearch(arr, target, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    for i in range(low, high + 1):
        if arr[i] == target:
            return i
    return -1


def HybridSearch(arr, target):
    """
    - Binary search while the window is large, linear scan once it is small.
    - Path invariant: each probed value must lie between the values of the
      earlier probes that bounded it. A violation proves the array is
      unsorted and triggers an immediate full linear search.
    - Safety net: on a clean miss, scan the regions binary search skipped.

    Hit:  O(log n) if the array is sorted.
    Miss: O(n). Proving a miss on possibly-unsorted data cannot be done faster.
    """
    n = len(arr)
    low, high = 0, n - 1
    lo_val = hi_val = None

    while high - low >= 16:
        mid = low + (high - low) // 2
        v = arr[mid]
        if v == target:
            return mid

        if (lo_val is not None and v < lo_val) or (hi_val is not None and v > hi_val):
            return LinearSearch(arr, target)  # unsorted proven

        if v < target:
            low, lo_val = mid + 1, v
        else:
            high, hi_val = mid - 1, v

    idx = LinearSearch(arr, target, low, high)
    if idx != -1:
        return idx

    idx = LinearSearch(arr, target, 0, low - 1)
    if idx != -1:
        return idx
    return LinearSearch(arr, target, high + 1, n - 1)
```

### Caveats

- The invariant check does **not** fix Case 3. It only makes failure faster when corruption lies on the probe path. The safety net does the real correctness work.
- The net skips almost nothing (only the final window under 16 elements), so it is effectively a full scan. You could drop the skipping to simplify.
- The "CPU cache" justification for the 16 threshold does not hold in Python (interpreter overhead dominates). It is a real effect in C++, so benchmark it there.

---

## 3. Fix list for the current Python file

1. **Separate timing from printing.** Verbose timers currently measure `print`, not the search. Rename the core to `_hybrid_core` (no I/O), and make `HybridSearch` a thin wrapper that times it once and prints once.
2. **Remove the five copy-pasted `t_overall_elapsed` blocks.** Step 1 fixes this.
3. **Relabel Case 3.** It exercises the safety net, not the path invariant. Trace: the only probe is `arr[8]=10`, then the window drops below 16, and the net on `[0..8]` finds 999.
4. **Add a real invariant-violation case.** Corrupt a probe position, e.g. `[1,2,3,4,5,6,7,8,2,12,14,...]`, so `arr[8]` falls below an earlier `lo_val`.
5. **Restore Case 4.** The sorted-array miss is the case that demonstrates the O(n) cost.
6. **Add a `timeit` benchmark with `verbose=False`.** Single-run microsecond readings are noise.
7. **Handle empty array input** in custom mode with a clear message.

### Minimal benchmark

```python
import timeit

def bench(n=1_000_000, reps=50):
    arr = list(range(0, 2 * n, 2))   # sorted, even numbers
    hit = arr[n // 3]                # present
    miss = 1                         # absent (odd)
    t_hit = timeit.timeit(lambda: HybridSearch(arr, hit), number=reps) / reps
    t_miss = timeit.timeit(lambda: HybridSearch(arr, miss), number=reps) / reps
    print(f"n={n:,} | hit: {t_hit*1e6:.1f} µs | miss: {t_miss*1e3:.2f} ms")
```

Expect hits in microseconds and misses in tens of milliseconds, a gap of several thousand times.

---

## 4. C / C++ port: blockers and plan

### Blockers to handle first

1. **Decide the contract before writing code.** Return `-1` on a miss. Hits are O(log n) on sorted data, misses are O(n). Write it at the top of the header.
2. **`size_t` underflow.** `low - 1` and `high - 1` underflow at 0. Use `ptrdiff_t` / `long long`, or restructure with half-open ranges `[low, high)`.
3. **Overflow-safe midpoint:** `low + (high - low) / 2`.
4. **Invariant tracking without `None`.** C++: `std::optional<T>` or a bool flag. C: two `bool`s.
5. **Benchmark pitfalls.** Compile with `-O2`, prevent the compiler from deleting the search (volatile sink or `benchmark::DoNotOptimize`), time with `std::chrono::steady_clock`, many reps, random targets.

### Project structure

```
ibesearching/
├── README.md                  # contract, complexity (hit O(log n), miss O(n)), how to build and run
├── python/
│   ├── ibesearching.py        # the interactive log/trace version (your current file, with the fix list applied)
│   └── bench.py               # timeit hit vs. miss benchmark, verbose=False
├── cpp/
│   ├── include/hybrid_search.hpp   # templated hybrid_search(const T* a, size_t n, T target)
│   ├── tests.cpp              # the four cases + randomized tests vs. a plain linear scan as the oracle
│   ├── bench.cpp              # hit vs. miss across sizes + threshold sweep (4, 8, 16, 32, 64)
│   └── CMakeLists.txt         # or a Makefile; build with -O2
├── c/                         # the challenge version, built after the C++ tests pass
│   ├── hybrid_search.h
│   ├── hybrid_search.c
│   ├── tests.c
│   └── bench.c
├── tests/
│   └── cases.txt              # shared test vectors (array, target, expected result) used by Python, C++ and C
├── results/
│   ├── threshold_sweep.csv    # output of cpp/bench.cpp
│   └── plot.py                # graphs the sweep; this is where the "CPU cache" claim gets tested for real
└── docs/
    └── IBESEARCHING_notes.md  # this file
```

Roles:

1. **`python/ibesearching.py` is the readable spec.** It prints every step (window, probed value, invariants, fallback), so you can trace a case by eye. Keep it for explanation and debugging, not speed.
2. **`cpp/` and `c/` are the fast implementations.** They have no logging in the hot path. If you want traces there, put them behind a compile-time flag such as `-DTRACE`.
3. **`tests/cases.txt` keeps all three languages honest.** Each implementation must pass the same vectors, including the sorted-array miss and the invariant-violation case.
4. **`results/` holds the evidence.** The benchmark writes the CSV, the plot reads it.

### Order

C++ first (templates, `std::optional`, compare against `std::binary_search`). Do the C version afterward as the challenge, once the C++ tests pass, so you have a correct reference.

---

## 5. What to take from this

1. **Lower bounds and adversary arguments.** A dead end can be a proof. Ask whether an adversary could defeat any algorithm.
2. **Contracts (preconditions) are part of the algorithm.** Dropping "sorted" costs Ω(n) to verify.
3. **Asymmetric guarantees.** A hit is self-certifying, a miss is not.
4. **Invariants.** The path-invariant check is a loop invariant used at runtime. Practice stating invariants for your loops.
5. **Amortization.** Pay O(n) once to verify and cache the result.
6. **Hybrids are real.** Introsort and Timsort combine algorithms with fallbacks and thresholds, as this project does.

---

## 6. Reading list (in order of payoff)

1. **Jon Bentley, *Programming Pearls*, Column 4.** Writing a correct binary search and proving it with invariants.
2. **Joshua Bloch, "Nearly All Binary Searches and Mergesorts are Broken" (2006).** The overflow bug that `low + (high - low) // 2` already avoids.
3. **CLRS.** Chapter 2 (loop invariants), the comparison-sort lower bound in Chapter 8, and the randomized algorithms chapter.
4. **Sergey Slotin, *Algorithms for Modern Hardware* (algorithmica.org/en), binary search chapters.** Free, C++, covers branchless search and cache behavior.
5. **Estivill-Castro & Wood, "A Survey of Adaptive Sorting Algorithms."** The sorting analogue of this project. Then read how Timsort exploits existing order.
6. **Property testing (advanced).** Lecture notes on "testing sortedness" (Ronitt Rubinfeld's work), the formal version of option 4 above.

Start with Bentley Column 4 and the Bloch post, then do the C++ port. The reading sticks better after you have benchmarked your own threshold.
