# M5 Session 3498 — selector-load/writer comparison

The independent retail capture ran first with a whole-RDRAM positive control.
The control reached 10,000 callbacks, title origin `0x00790400` at width 1024
appeared, and both selector execution watches were live. Its 51 printed title
pairs showed selector index `v1=0x4` at `0x80091060` and source `v0=0x80171CE0`
at `0x80091074`.

The first port attempt was invalid for comparison: it crashed before title at
`spTaskSchedulerThread`, last guest PC `0x8000834C`, with zero phase, selector,
and audio-return rows. A corrective retry used the previously qualified
autopilot/LLE/spin-yield real-image route from the same successful build. It
reached title, fired the task-writer and both selector controls, and produced
660 selector-load and 660 selector-writer rows, 257 audio-return rows, and
1,332 image-stage rows, with no crash or abort.

The port selector-load classes were:

| source/value class | rows |
|---|---:|
| `0x8018DD30` | 1 |
| `0x80171CE0` | 330 |
| `0x80173B20` | 329 |

The writer rows preserved the loaded source/value, including the one
`0x8018DD30` row. Both port controls and the independent retail control were
positive, so the port null/control-failure hypothesis is refuted at this
scope. The source-family distributions are not an animated ordinal join, but
the retail run's observed class is restricted to `0x80171CE0` while the
qualified port run exposes additional `0x80173B20` and `0x8018DD30` classes.
This selects selector/input divergence at the non-ordinal source-class scope
and moves the unresolved edge upstream of `0x80091060`, where the selector/table
producer must be compared.

The measurement is diagnostic-only. No selector, task field, audio state, or
output was rewritten, skipped, or validated.

Evidence: `scratch/agent/s3498_m5_selector_comparison/retail.log`,
`port-retry.log`, and the two summary files.
