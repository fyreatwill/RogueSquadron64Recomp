# NEXT work unit (s2372) — M5 A1 port predecessor arguments

HYPOTHESIS-ID: m5-a1-port-predecessor-args

## Work unit

Run one ground-truth-first capture around the predecessor path to the port's
null-function request at `0x80001F88`. Keep the retail range watch and its
`$a0/$a2` rows, and add a bounded port-side capture immediately before
`get_function(0)` so the `0x80001F84` predecessor arguments can be compared.
Retain whole-RDRAM, both target-origin controls, and the port early-640
transition control. Do not add a fallback, change dispatch or VI selection, or
edit task/audio data.

## Competing hypotheses and discriminating measurement

- H-RetailPredecessorMatches: retail executes the predecessor window and its
  `$a0/$a2` relation matches the port context; this selects a later port
  dispatch/input divergence.
- H-RetailPredecessorArgsDiffer: retail executes the predecessor window but
  its `$a0/$a2` values differ from the port's call-site context; this selects
  an ABI/input value divergence before `get_function(0)`.
- H-PortPredecessorCaptureInvalid: the new port marker does not fire while
  the existing abort and oracle controls do; this rejects the comparison as
  instrument-invalid and selects no contract explanation.

The discriminator is one arm/phase table containing retail predecessor-window
PC/GPR rows, oracle target-origin rows, port predecessor `$a0/$a2` rows,
port `[a1-abort]` requested address and last guest PC, port early-640
transition rows, and crash/abort status. A null retail result is invalid
unless whole-RDRAM, both target-origin, and the range-watch positive control
are all positive.

## Exact commands

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2372_m5_a1_port_predecessor_args.sh s2372_m5_a1_port_predecessor_args
    grep -E '^(controls|table|verdict) ' scratch/agent/s2372_m5_a1_port_predecessor_args/driver.log

The driver must run the oracle first with `--watch-write 0x0:0x800000`, both
target-origin watches, and the bounded predecessor range, then launch control
and alternate port arms from the same build and SIGKILL them after the table is
complete.
