# NEXT work unit (s2374) — M5 A1 first internal `$a0` divergence

HYPOTHESIS-ID: m5-a1-rs-free-internal-a0

## Work unit

Run one ground-truth-first capture of the first internal writes/branches to
`ctx->r4` in port `rs_free` (`0x80001C98..0x80001F84`), paired with retail's
existing watch rows for `rs_free` entry and predecessor return. Keep
whole-RDRAM, both target origins, predecessor range, live `rs_free` entry,
early-640, and both control/alternate arms. Do not add a fallback or change
dispatch, VI selection, task data, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-RsFreeInternalWriteDiverges: the first port write/branch to `ctx->r4`
  differs from the retail predecessor path before `0x80001F84`.
- H-RsFreeInternalMatches: the port internal sequence matches the retained
  retail shape and the divergence is after this bounded `rs_free` body.
- H-RsFreeJoinInvalid: positive controls pass but the internal rows cannot be
  joined to the target entry/return, so no explanation is selected.

The discriminator is one phase-4 table containing the first internal port
`$a0` write/branch, retail `rs_free` entry `$a0/prev_pc`, retail
`0x80001F84` `$a0/$a2/prev_pc`, port `[rs-free]` entry `$a0/$ra`, port
`[a1-args]` return `$a0/$a2`, both `[a1-abort]` rows, and all controls.
Retail nulls are invalid unless the whole-RDRAM, target-origin,
`rs_free`-entry, and predecessor-PC controls are positive.

## Exact commands

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2374_m5_a1_internal_a0.sh s2374_m5_a1_internal_a0
    grep -E '^(controls|table|verdict) ' scratch/agent/s2374_m5_a1_internal_a0/driver.log

The driver must run the oracle first with `--watch-write 0x0:0x800000`, both
target-origin watches, the predecessor range, and the `rs_free` entry PC;
then launch both same-build port arms and SIGKILL each after its abort marker.
