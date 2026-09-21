# M5 Session 3664 — route task join is title-buffer specific

The new oracle join instrument was built and run against retail with a
whole-RDRAM positive control, four descriptor-range watches, phase-gated task
rows, and the dominant writer field at `0x80090DE4`. The first capture exposed
an instrument bug: retaining only the globally latest task row missed the
alternating VI buffer. The fixed capture retains the latest task within the
current `(width, origin)` bucket and emitted 120 joined rows.

Controls were valid: the whole-RDRAM watch reached its 10,000-hit threshold,
the title reached both 1024 origins, and the writer/task instruments fired.
The run did not reach the 512 hangar origin `0x006AB400`; it remained in the
title task loop through approximately 37.5 seconds and was SIGKILLed by the
watchdog. Therefore this is not a full route discriminator.

The title join split by VI buffer origin:

| VI origin | task `data_ptr` | joined writer `$s1` family |
|---|---|---|
| `0x00790400` | `0x80171CE0` | `0x80171CF0..0x80172B60` |
| `0x00790800` | `0x80173B20` | `0x80173B30..0x801749A0` |

Every observed writer row retained `prev_pc=0x80090DE0` and `$ra=0x80090ABC`.
This supports `H-RouteTaskSelection` for the title buffer pair and does not
select `H-SharedLogicalProducerAllPhases`, because the hangar bucket was not
observed. The result is single-source retail evidence; the paired port arm was
not run in this work unit.

ORIGIN: diagnostic-only task/writer joins; no guest or host value was skipped,
rewritten, or guarded.
