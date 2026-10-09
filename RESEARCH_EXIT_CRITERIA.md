# NumPy searchsorted Q-free finalization criteria (2026-10-09)

## Single objective
Submit a maintainable, Q-free NumPy searchsorted optimization that retains roughly 5x benefit on validated high-locality workloads while preventing material regressions on general, adversarial, and small workloads relative to the **original batched NumPy implementation**.

## Non-negotiable design rules
- NO query-length Q activation threshold; NO architecture-specific hardware threshold. Query length may be used for valid indexing/shape, not a performance magic gate.
- Reuse coarse positions produced by the first three batched passes; account for any loads/comparisons as *incremental* cost (not literally free).
- Reject early when the coarse positions or sampled predecessor keys provide adverse evidence.
- Escalate only ambiguous regions if justified by a measured cost bound; absence of detected inversions is NOT sufficient proof of profitable locality.
- Maintain the original batched path for non-target cases; measure whole-function overhead, including the selector and fallback.
- Prefer the smallest explainable selector; no histogram, CPU-model branch, or adaptive threshold by default.
- The ~5x figure is a *target-workload* historical observation, NOT guaranteed across all N/Q/data.
- Correctness must hold for left/right, supported dtypes, strided inputs, equal elements, and special floating-point values.

## Measurement / close gate
- Compare ORIGINAL batched, Q-free existing, and conservative candidates on paired ABBA native runs.
- Show both acceptance/rejection for each input pattern and latency relative to original batched. No sign-off based only on Q20 comparisons.
- 2 distinct CPU backends (not merely OS versions when CPU is same); repeated seeds and adverse hidden reversals. Separate run-to-run noise from reproducible slowdowns.
- PASS: relevant correctness and no reproducible material general-case regression within the tested matrix, plus meaningful retained ~5x high-locality win and a compact maintenance argument.
- FAIL or inconclusive: do not modify upstream PR. Record exact obstruction, evidence, and next smallest experiment.

## Upstream status
Upstream PR https://github.com/numpy/numpy/pull/32895 was already OPEN as of 2026-10-09; the task is to prepare a Q-free revision, not to open a duplicate.
Independent PRIVATE research repo only until sign-off.

## Current experimental note
Strict coarse-anchor equality is a *candidate*, not proof of monotonic query keys or profitability. Bounded galloping was not uniformly beneficial. Keep this distinction in future reporting.
