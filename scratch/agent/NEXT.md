# NEXT work unit (s2373) — M5 A1 rs_free argument boundary

HYPOTHESIS-ID: m5-a1-port-predecessor-args

## Work unit

Run one ground-truth-first capture that pairs the retail `rs_free` entry and
predecessor rows with the port's existing bounded `0x80001F84` return marker
and its `ROGUESQ_LOG_RS_FREE` entry marker. Add only a bounded port-side `$ra`
capture if needed. Keep whole-RDRAM, both target origins, predecessor range,
early-640, and both control/alternate arms. Do not add a fallback or change
dispatch, VI selection, task data, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-CallerSuppliesDivergentA0: port `rs_free` entry already has
  `$a0=0x8010FEE0` while retail's corresponding entry has `$a0=1`; the
  divergence is before or at the caller's argument construction.
- H-RsFreeMutatesA0: port entry matches the retail argument, but the port
  return row changes `$a0` before `0x80001F84`; the divergence is inside
  `rs_free` or its ABI reconstruction.
- H-RsFreeJoinInvalid: positive controls pass but the entry/return rows cannot
  be phase/caller-joined, so no contract explanation is selected.

The discriminator is one phase-4 table containing retail `rs_free` entry
`$a0/$ra`, retail `0x80001F84` `$a0/$a2` and previous-PC rows, port
`[rs-free]` entry `$a0/caller_ra`, port `[a1-args]` return `$a0/$a2`, both
`[a1-abort]` rows, and all controls. Retail nulls are invalid unless the
whole-RDRAM, target-origin, and predecessor-PC controls are positive.

## Exact commands

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2373_m5_a1_rs_free_boundary.sh s2373_m5_a1_rs_free_boundary
    grep -E '^(controls|table|verdict) ' scratch/agent/s2373_m5_a1_rs_free_boundary/driver.log

The driver must run the oracle first with `--watch-write 0x0:0x800000`, both
target-origin watches, the predecessor range, and the `rs_free` entry PC;
then launch both same-build port arms and SIGKILL each after its abort marker.
