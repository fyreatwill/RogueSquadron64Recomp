# NEXT work unit (s2371) — M5 A1 caller/input boundary

HYPOTHESIS-ID: m5-a1-caller-input-boundary

## Work unit

Run one ground-truth-first capture around the predecessor path to the port's
null-function request at `0x80001F88`. Use the retail oracle to watch the
immediately preceding guest-PC window and collect `$a0/$a2`; use the port's
existing abort row and last-guest-PC marker as the corresponding arm. Retain
the whole-RDRAM and both target-origin controls plus the port early-640
transition control. Do not add a fallback, change dispatch or VI selection, or
edit task/audio data.

## Competing hypotheses and discriminating measurement

- H-RetailPredecessorAbsent: retail has positive controls but no execution in
  the predecessor window; this selects a route/input divergence before the
  port-only call site.
- H-RetailPredecessorMatches: retail executes the same predecessor window and
  its `$a0/$a2` relation matches the port context; this selects a later port
  dispatch/input divergence.
- H-RetailPredecessorArgsDiffer: retail executes the predecessor window but
  its `$a0/$a2` values differ from the port's call-site context; this selects
  an ABI/input value divergence before `get_function(0)`.

The discriminator is one arm/phase table containing retail predecessor-window
PC/GPR rows, oracle target-origin rows, port `[a1-abort]` requested address and
last guest PC, port early-640 transition rows, and crash/abort status. A null
retail result is invalid unless whole-RDRAM, both target-origin, and the
watch-PC mechanism's positive control are all positive.

## Exact commands

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2371_m5_a1_caller_input_boundary.sh s2371_m5_a1_caller_input_boundary
    grep -E '^(controls|table|verdict) ' scratch/agent/s2371_m5_a1_caller_input_boundary/driver.log

The driver must run the oracle first with `--watch-write 0x0:0x800000`, both
target-origin watches, and a bounded `--watch-pc-range` covering the
predecessor window, then launch control and
alternate port arms from the same build and SIGKILL them after the table is
complete.
