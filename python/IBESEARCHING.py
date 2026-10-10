#!/usr/bin/env python3
# HA ON DA CODE SO IT'S NOT RIGHT
import time


def LinearSearch(
    arr: list, target: int, low: int = 0, high: int | None = None, verbose: bool = False
) -> int:
    "Normal Linear Search with optional logging and step benchmarking :)"
    t_start = time.perf_counter()
    if high is None:
        high = len(arr) - 1

    if verbose:
        print(f"    [Linear Search] Scanning indices {low} to {high}...")

    for i in range(low, high + 1):
        if arr[i] == target:
            t_elapsed = (time.perf_counter() - t_start) * 1_000_000  # Convert to microseconds (µs)
            if verbose:
                print(f"    [Linear Search] Match found at index {i}! (Time: {t_elapsed:.2f} µs)")
            return i

    t_elapsed = (time.perf_counter() - t_start) * 1_000_000
    if verbose:
        print(f"    [Linear Search] Target {target} not found in range [{low}, {high}]. (Time: {t_elapsed:.2f} µs)")
    return -1


def HybridSearch(arr: list, target: int, verbose: bool = True) -> int:
    """
    Adaptive Hybrid Search with step-by-step performance timing.
    - Binary search while the window is large, linear scan once it is small.
    - Path invariant check to prove unsortedness.
    - Safety net for skipped binary regions.
    """
    t_overall_start = time.perf_counter()
    n = len(arr)

    if n == 0:
        if verbose:
            print("  [HybridSearch] Array is empty.")
        return -1

    low, high = 0, n - 1
    lo_val = hi_val = None
    step = 1

    if verbose:
        print(f"  [Init] Array size: {n} | Target: {target}")

    while high - low >= 16:
        t_step_start = time.perf_counter()

        mid = low + (high - low) // 2
        value = arr[mid]

        if verbose:
            print(f"\n  -- Step {step} --")
            print(f"  Window: indices [{low}..{high}] (size: {high - low + 1})")
            print(f"  Invariants -> lo_val: {lo_val}, hi_val: {hi_val}")
            print(f"  Mid index: {mid} -> Probed value: {value}")

        if value == target:
            t_step_elapsed = (time.perf_counter() - t_step_start) * 1_000_000
            t_overall_elapsed = (time.perf_counter() - t_overall_start) * 1_000_000
            if verbose:
                print(f"  🎯 Direct hit at mid index {mid}! (Step Time: {t_step_elapsed:.2f} µs)")
                print(f"\n  ⏱️ TOTAL SEARCH RUNTIME: {t_overall_elapsed:.2f} µs ({t_overall_elapsed/1000:.4f} ms)")
            return mid

        # Path invariant check: prove array is unsorted
        if (lo_val is not None and value < lo_val) or (
            hi_val is not None and value > hi_val
        ):
            t_step_elapsed = (time.perf_counter() - t_step_start) * 1_000_000
            if verbose:
                print(f"  🚨 PATH INVARIANT VIOLATION DETECTED! (Check Time: {t_step_elapsed:.2f} µs)")
                if lo_val is not None and value < lo_val:
                    print(f"     Reason: Probed value {value} < lower bound {lo_val}")
                else:
                    print(f"     Reason: Probed value {value} > upper bound {hi_val}")
                print("     Array is proven unsorted. Triggering immediate full linear search fallback...\n")

            idx = LinearSearch(arr, target, 0, n - 1, verbose=verbose)
            t_overall_elapsed = (time.perf_counter() - t_overall_start) * 1_000_000
            if verbose:
                print(
                    f"\n  ⏱️ TOTAL SEARCH RUNTIME: {t_overall_elapsed:.2f} µs ({t_overall_elapsed/1000:.4f} ms)"
                )
            return idx

        # Update bounds
        if value < target:
            t_step_elapsed = (time.perf_counter() - t_step_start) * 1_000_000
            if verbose:
                print(f"  Value {value} < Target {target} -> Narrowing right. Updating lo_val = {value} (Step Time: {t_step_elapsed:.2f} µs)")
            low, lo_val = mid + 1, value
        else:
            t_step_elapsed = (time.perf_counter() - t_step_start) * 1_000_000
            if verbose:
                print(
                    f"  Value {value} > Target {target} -> Narrowing left. Updating hi_val = {value} (Step Time: {t_step_elapsed:.2f} µs)"
                )
            high, hi_val = mid - 1, value

        step += 1

    # Window smaller than 16 elements
    if verbose:
        print(f"\n  -- Window shrunk below 16 elements (size: {high - low + 1}) --")
        print(f"  Switching to Linear Search for active range [{low}..{high}]...")

    idx = LinearSearch(arr, target, low, high, verbose=verbose)
    if idx != -1:
        t_overall_elapsed = (time.perf_counter() - t_overall_start) * 1_000_000
        if verbose:
            print(f"\n  ⏱️ TOTAL SEARCH RUNTIME: {t_overall_elapsed:.2f} µs ({t_overall_elapsed/1000:.4f} ms)")
        return idx

    # Safety net fallback for skipped ranges
    if verbose:
        print("\n  -- Target not found in primary binary window --")
        print("  Running safety net on skipped regions...")

    if low > 0:
        if verbose:
            print(f"  Scanning skipped left side [0..{low - 1}]...")
        idx = LinearSearch(arr, target, 0, low - 1, verbose=verbose)
        if idx != -1:
            t_overall_elapsed = (time.perf_counter() - t_overall_start) * 1_000_000
            if verbose:
                print(f"\n  ⏱️ TOTAL SEARCH RUNTIME: {t_overall_elapsed:.2f} µs ({t_overall_elapsed/1000:.4f} ms)")
            return idx

    if high < n - 1:
        if verbose:
            print(f"  Scanning skipped right side [{high + 1}..{n - 1}]...")
        idx = LinearSearch(arr, target, high + 1, n - 1, verbose=verbose)
        if idx != -1:
            t_overall_elapsed = (time.perf_counter() - t_overall_start) * 1_000_000
            if verbose:
                print(f"\n  ⏱️ TOTAL SEARCH RUNTIME: {t_overall_elapsed:.2f} µs ({t_overall_elapsed/1000:.4f} ms)")
            return idx

    t_overall_elapsed = (time.perf_counter() - t_overall_start) * 1_000_000
    if verbose:
        print(f"\n  ⏱️ TOTAL SEARCH RUNTIME: {t_overall_elapsed:.2f} µs ({t_overall_elapsed/1000:.4f} ms)")
    return -1


def parse_user_array(raw_input: str) -> list:
    """Parses comma or space separated numbers from user string."""
    cleaned = raw_input.replace(",", " ")
    return [int(x) for x in cleaned.split()]


def main():
    print("""  ---  🔍 IBESEARCHING
                      WITH HA 🔍 --- \n""")
    while True:
        print("Choose Mode:")
        print("  1. Run Built-in Test Cases")
        print("  2. Enter Custom Array & Target")
        print("  3. Exit")
        choice = input("\nEnter choice (1 or 2 or 3): ").strip()

        if choice == "3":
            print("I'm out. Signed off. HA.")
            break

        elif choice == "2":
            try:
                raw_arr = input(
                    "Enter array (comma or space separated, e.g., 1, 2, 999, 4, 5...): "
                )
                arr = parse_user_array(raw_arr)
                target = int(input("Enter target number: "))

                print("\n" + "=" * 50)
                print("  EXECUTING HYBRID SEARCH LOGS")
                print("=" * 50)
                idx = HybridSearch(arr, target, verbose=True)

                print("\n" + "=" * 50)
                print(f"  FINAL RESULT: Target {target} -> Index: {idx}")
                if idx != -1:
                    print(f"  Confirmed Value at arr[{idx}]: {arr[idx]}")
                print("=" * 50)

            except ValueError:
                print("\n❌ Invalid input! Please enter valid integer numbers.")

        elif choice == "1":
            # Default built-in harness
            # Case 1: Standard Sorted
            sorted_arr = [i * 2 for i in range(1, 30)]
            print("\n=== [Case 1] Pure Sorted Array ===")
            idx1 = HybridSearch(sorted_arr, 42, verbose=True)
            print(f"-> Result Index: {idx1}\n")

            # Case 2: Small Array
            small_arr = [3, 7, 12, 19, 25, 30]
            print("\n=== [Case 2] Small Array (<16 elements) ===")
            idx2 = HybridSearch(small_arr, 19, verbose=True)
            print(f"-> Result Index: {idx2}\n")

            # Case 3: Corrupted / Path Invariant Break
            corrupted_arr = [
                1,
                2,
                999,
                4,
                5,
                6,
                7,
                8,
                10,
                12,
                14,
                16,
                18,
                20,
                22,
                24,
                26,
                28,
            ]
            print(
                "\n=== [Case 3] Unsorted / Corrupted Array (Path Invariant Break) ==="
            )
            idx3 = HybridSearch(corrupted_arr, 999, verbose=True)
            print(f"-> Result Index: {idx3}\n")

        else:
            print("\n❌ Invalid choice! Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
