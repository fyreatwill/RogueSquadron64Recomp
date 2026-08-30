# NEXT work unit — promote the non-interrupting SP yield lifecycle

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3303 selected `H-FalseYieldStatus` with a same-build port A/B and
independent retail ground truth. Baseline request-only status produced
`requested=1 returned=1`, E70/E80F, and the third-submit stall. The
completion-wins arm produced `requested=1 returned=0`, E60, restored
19ED0/19F1C/19FE4, matched SENT/SRET through n=10, and advanced 2D50 through
n=10. Retail s3296/s3298/s3301 has no viewer yield publication/E70 and
completes type-1 before type-2.

The current code still keeps completion-wins behind
`ROGUESQ_SP_YIELDED_COMPLETION_WINS=1`. The linked strong
`osSpTaskStartGo_recomp` also shadows the weak implementation's request clear.

## Competing hypotheses

- `H-LifecycleRepairComplete`: default not-yielded status plus request reset
  preserves E60/scheduler/submit progress long enough for viewer return and
  title 1024; the rollback arm reproduces E70/E80F and the third-submit stall.
- `H-ViewerOnly`: the default returns through the viewer but still never
  publishes title 1024, proving the false-yield defect was causal only for the
  local viewer stall and another downstream boundary remains.
- `H-LateYieldRecurrence`: the default initially reaches SRET/2D50 n=4 but a
  later unmatched submit, stale request transition, crash, or E70/E80F stops
  it before viewer return.
- `H-CoverageInvalid`: either arm misses its arm row, request-reset control,
  SP completion, `640 @ 0x0066A500`, viewer entry, or expected rollback
  discriminator.

## Discriminator

One build contains default completion-wins and an explicit request-only
rollback arm. Add a bounded task-start request-reset row so a pre=1 → post=0
transition is visible; do not infer reset from a later status read. Run both
arms concurrently and phase-gate each at the 640 viewer. Default E60 plus
matched SENT/SRET/2D50, viewer return, and title 1024 selects
`H-LifecycleRepairComplete`. Viewer return without 1024 selects
`H-ViewerOnly`. Early progress followed by a named late stop selects
`H-LateYieldRecurrence`. Rollback must reproduce request=1/returned=1,
E70/E80F, SENT n=3 without SRET n=3, or the pair is invalid.

ORIGIN: `osSpTaskYield_recomp` legitimately writes the request bit. The bit is
not a legitimate yielded-task result because the host executes tasks to
completion and has no interrupt/resume path. Resetting it at the linked strong
task-start boundary is legitimate lifecycle cleanup, not a corruption guard.
This is not M5 Step 3 audio/output work.

## Exact commands

In `lib/N64ModernRuntime/librecomp/src/sp.cpp`, make not-yielded the default
and preserve request-only behind `ROGUESQ_SP_YIELDED_REQUEST_ONLY=1`. Export a
small request-reset helper and call it from both the weak task-start path and
the linked strong override in `src/main/upstream_compat.cpp`. Keep the s3303
status rows, add the task-start pre/post control, update the env catalog, and
export the lib patch.

Update the s3303 pair driver (or create the s3304 successor) to wait on
phase predicates and the complete default/rollback discriminator, not elapsed
animation time. Both processes must start from `build/` and end with SIGKILL.

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  cmake --build build --config Debug --target RogueSquadron64Recomp
./submodule-patches/export.sh
zsh scratch/agent/s3304_yield_lifecycle_default/run_pair.sh
```

Log: `scratch/agent/s3304_yield_lifecycle_default.md`, both arm logs, and one
joined verdict.
