# NEXT work unit (s2950) — port route source-word qualification

HYPOTHESIS-ID: m5-route-qualification-repair

## Context

s2948 added a regeneration-owned full-input probe at `0x80019CD8`. The fixed
port run emitted 771 rows, and its same-run `[f5-fetch-control]` positive
control fired 8 times, but the route stopped at pre-title VI 640
(`0x0066A500`). s2949's independent retail run reached both target phases and
found three source-word families at the same PC: `0x02000612`, `0x00000400`,
and `0x02000800`; sampled `branch_state=0x0010` was constant.

## Competing hypotheses and discriminator

- H-PrepareFieldBad: the port's pre-title pointed field/source word differs
  from the retail route's accepted families.
- H-PrepareTimingBad: the values match, but phase-relative ordering differs.
- H-PrepareLogicBad: values and ordering match, but generated control flow
  still rejects the route.

Extend the existing regeneration-owned port probe at `0x80019CD8` with the
pointed source-word/branch fields represented by the oracle field table, in one
build and one fixed run. The `[f5-fetch-control]` mark must fire. A stable
pre-title mismatch selects Field; matching values with a different event order
select Timing; matching values/order with rejection selects Logic. Missing
positive control or target qualification selects nothing and requires a pivot,
not a mitigation.

## Exact work

From the repo root, update the existing fixup-owned probe, then run:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_F5_STATE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  ./build/RogueSquadron64Recomp > scratch/agent/s2950_port_route_sourceword.log 2>&1
```
