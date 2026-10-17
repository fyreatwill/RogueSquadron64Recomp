# Session 5325 — M4 shared-boundary sampler design

## Purpose

The current retail capture records cxd4 instruction-PC/step samples and the
qualified port capture records four synthetic M4 stages. Both show transient
`0x8000` VACC state followed by task-end clearing, but those are not the same
boundary. This design makes the comparison falsifiable without changing game
state or adding a mitigation.

## Ground-truth preflight

The retail oracle was run for 8 seconds with the debugger-enabled cxd4-capable
core and a whole-RDRAM write watch:

```text
--watch-write 0x0:0x800000 --hit-cap 3 --vi-trace
```

The positive control reached 10,000 callbacks, the oracle reported 480 VI,
and VI width/origin callbacks were live. This validates the watch and phase
instrument before any target null can be interpreted. The oracle README also
establishes that the watch addresses are physical and that cxd4's `RSM1`
records carry task serial, task type, guest RSP PC, step, and all 24 VACC
lanes.

## Competing hypotheses

| ID | Prediction at an aligned task/PC boundary |
| --- | --- |
| H1 | Retail and port have the same first/last writer and VACC lane value; the stage-only difference was a boundary artifact. |
| H2 | Both sides align, but the first/last writer or lane value differs; the port's accumulator origin/operation is divergent. |
| H3 | Task identity or PC/step cannot be aligned with positive controls; the question remains unevaluable and no mitigation is justified. |

The discriminator is one table keyed by `(VI phase origin,width,task serial,
RSP PC,step bucket)`. For each key retain first writer, last writer, the
first and last `0x8000` lane, and task-end VACC. H1 is selected only if all
retained keys agree; H2 requires a repeated mismatch in the same key class;
H3 is selected if either side lacks a live positive control or the join cannot
be made without a synthetic stage guess.

## Instrument plan

1. Retail: rebuild the cxd4 plugin with an env-gated stride control for the
   existing `RSM1` mid-task sampler. Use stride 1 for one phase-gated run,
   retaining task serial, guest PC, step, VACC, and task-end `RSD1` records.
2. Port: extend the regeneration-surviving M4 probe record with the actual
   Factor 5 guest instruction PC corresponding to each stage hook. The PC
   constants must come from the generated labels/ucode listing, not from
   stage ordinal arithmetic. Retain the existing task and phase keys and add
   the same first/last/`0x8000` summary fields.
3. Run both arms with a whole-RDRAM positive control, VI phase controls, and
   the same keyed hangar input schedule. Do not compare wall-clock timestamps.
4. Join only exact task/PC/step keys. If the port cannot expose an actual PC,
   stop at H3; do not treat stage 10/11 as an instruction-PC proxy.

No code or mitigation is authorized by this design alone. The named writer
for any future mitigation must be the exact VACC-producing instruction and
its value must first be shown legitimate or corrupt by this table.
