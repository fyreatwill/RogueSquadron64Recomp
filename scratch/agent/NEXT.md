# NEXT work unit (s2561) — M4 route reachability

HYPOTHESIS-ID: m4-accumulator-origin-dynamic-index

## Single work unit

Run one phase-gated runtime capture that marks overlay-0x1c producer entry,
overlay-0x20 consumer entry, the `0xC70/0xB74` byte, and the `r4 == 2` branch
outcome in one complete reachability table. Keep the existing qualified route
and retail oracle whole-RDRAM positive control. Do not add a guard, remap, or
value mitigation.

## Competing hypotheses and discriminator

- `H-route-live-branch-cold`: both route entries execute, but `r4 == 2` is never
  taken, explaining the absent indirect consumer.
- `H-route-live-producer-cold`: producer entry executes but the consumer route
  does not, selecting a route/dispatch split.
- `H-route-dead`: neither entry executes despite positive controls.
- `H-route-live-index`: the indirect consumer branch executes; restore the
  complete producer/index join as the next unit.

The discriminator is one phase-keyed table covering both entry marks, all
`r4` branch values, the raw index byte, and the positive controls. Entry rows
with no branch-taken rows select `H-route-live-branch-cold`; producer-only rows
select `H-route-live-producer-cold`; no entry rows select `H-route-dead`; a
branch-taken row reopens the full index join.

## Exact preflight and run commands

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n 'B00|B02|B04|0xC70|0xB74|m4' src lib tools --glob '!*.log'
rg -n 'M4|producer|consumer|index' docs scratch/agent --glob '!*.log'
# Arm the retail oracle whole-RDRAM positive control before adding any probe.
# Batch both route-entry marks and every branch/index field in one build/run.
```

If the existing capture cannot emit the full joined table, stop and redesign
the capture before building. Do not repeat the prior static literal audit.
