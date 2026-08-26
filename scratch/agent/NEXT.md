# NEXT work unit (s2458) — trace the retail-selected M5 writer into the port

HYPOTHESIS-ID: m5-image-consumer-provenance

## Work unit

Build one phase-gated retail/port provenance table for the exact retail
second-range writer relation established at `0x800078EC` and the port image
arm's corresponding task/DMEM identity. Keep the first-null resolver capture
and indirect resolver control passive. Do not remap output, alter task data,
change gates, or add guards.

## Competing hypotheses and discriminator

- H-PortSecondRangeEquivalent: the port image/task row joins a legitimate
  second-range consumer equivalent to retail's `0x8002BEEC` → `0x800078EC`.
- H-PortGeneratedAlternate: the port row joins the generated audio-overlay
  alternate at `0x8008F2CC` or another direct `rs_memset` caller.
- H-PortNoConsumer: the port image/task identity has no corresponding
  second-range consumer before the hangar boundary.

The discriminator is one complete same-run table joining retail writer PC,
range offset/value, phase/origin, and caller predecessor against port image
ordinal/task identity and any bounded second-range consumer row. The retail
whole-RDRAM and target-PC controls must fire; the port image arm and resolver
positive control must fire. A retail-equivalent join selects
H-PortSecondRangeEquivalent; a generated-alternate join selects
H-PortGeneratedAlternate; an active image/task row with no consumer selects
H-PortNoConsumer. Missing any control is a non-result.

## Exact commands

1. Before instrumenting, run the retail oracle with whole-RDRAM positive
   control, explicit hangar origin `0x006AB400`, and the selected writer PCs
   from the prior audit; inspect `tools/oracle/README.md` first.

2. Before building, inspect the existing M5 image/task rows and the retail
   writer audit:

   `rg -n "0x800078EC|m5.*image|audtask-image|pcm-boundary|image-stage|rs_memset" src lib scratch/agent/s2456_m5_null_dispatch`

3. Batch all fields in one build and one qualified port run from `build/`,
   with `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LOG_M5_SECOND_EXEC=1`, and the
   existing passive M5 breadcrumb variables. Capture to a non-dot-prefixed
   path and SIGKILL on timeout.

4. Expected selection: a complete table with both independent controls and a
   single join classification. Do not treat a zero-valued port row as proof of
   no consumer without a phase-gated positive control.
