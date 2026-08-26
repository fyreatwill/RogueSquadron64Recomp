# NEXT work unit (s2375) — M5 A1 retail internal `$a0` join

HYPOTHESIS-ID: m5-a1-rs-free-internal-a0

## Work unit

Run one ground-truth-first capture with the oracle watch range widened to
`0x80001C98..0x80001FA0`, while retaining whole-RDRAM, both target origins,
predecessor range, live `rs_free` entry, early-640, and both same-build port
arms. Reuse the positive port internal trace from s2374. Do not change game
behavior, dispatch, VI selection, task data, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-RsFreeInternalWriteDiverges: retail and port differ in the first matched
  internal `$a0` assignment or branch before `0x80001F84`.
- H-RsFreeInternalMatches: the matched retail and port internal sequence is
  equivalent through the bounded body; divergence is after it.
- H-RsFreeJoinInvalid: widened oracle rows still cannot be phase/entry joined.

The discriminator is one phase-4 table joining oracle rows at
`0x80001CAC`, `0x80001CB0`, `0x80001CD8`, and `0x80001F84` with the port
`[rs-free-internal]`, `[rs-free]`, `[a1-args]`, and `[a1-abort]` rows in both
arms. A null result is invalid unless all whole-RDRAM, target-origin,
predecessor, entry, early-640, and internal positive controls pass.

## Exact commands

    cmake --build build --config Debug --target RogueSquadron64Recomp
    cp scratch/agent/run_s2373_m5_a1_rs_free_boundary.sh scratch/agent/run_s2375_m5_a1_rs_free_internal_join.sh
    sed -i '' 's/0x80001F40:0x80001FA0/0x80001C98:0x80001FA0/' scratch/agent/run_s2375_m5_a1_rs_free_internal_join.sh
    env ROGUESQ_LOG_RS_FREE_INTERNAL=1 zsh scratch/agent/run_s2375_m5_a1_rs_free_internal_join.sh s2375_m5_a1_rs_free_internal_join
    grep -E '^(controls|table|verdict) ' scratch/agent/s2375_m5_a1_rs_free_internal_join/driver.log

The driver must SIGKILL each port arm after its abort marker and must report
counts for every internal PC plus all controls.
