# NEXT work unit (s2560) — M4 dynamic index join

HYPOTHESIS-ID: m4-accumulator-origin-dynamic-index

## Single work unit

Run one phase-gated runtime capture joining every overlay-0x1c producer slot
(`DMEM B00/B02/B04`, including its `r7` slot/index) to every overlay-0x20
consumer index (`0xC70/0xB74` source, mask, and selected B00/B02/B04 entry) in
the qualified title-to-hangar route. Use the existing phase/route controls and
the retail oracle whole-RDRAM positive control. Do not add a guard, remap, or
value mitigation. The M5 s2559 checkpoint is complete for this iteration;
image promotion remains unauthorized.

## Competing hypotheses and discriminator

- `H-index-alias`: the live consumer index selects a producer slot and the
  selected slot values/pointers join in the same phase.
- `H-index-no-join`: producer slots and consumer indices are live, but no
  selected index-to-slot relation is observed.
- `H-producer-dead`: no phase-gated producer slot is live despite positive
  runtime consumer controls.
- `H-consumer-dead`: producer slots are live but the overlay-0x20 consumer does
  not execute in the qualified phase.

The discriminator is one complete joined table covering all producer slots,
all consumer index observations, selected entries, phase, and positive
controls. A same-phase selected-slot join proves `H-index-alias`; live
unjoined tables select `H-index-no-join`; absent producer or consumer rows
select the corresponding dead-path hypothesis.

## Exact preflight and run commands

```sh
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n 'B00|B02|B04|0xC70|0xB74|m4' src lib tools --glob '!*.log'
rg -n 'M4|producer|consumer|index' docs scratch/agent --glob '!*.log'
# Arm the retail oracle whole-RDRAM positive control before adding any probe.
# Batch all producer-slot and consumer-index fields in one build/run.
```

If the existing capture cannot emit the full joined table, stop and redesign
the capture before building. Do not repeat the prior static literal audit.
