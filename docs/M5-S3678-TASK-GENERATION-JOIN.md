# M5 s3678 — task-generation source/stage join

The retail ground-truth arm ran first with the existing task-PC witness. It
passed the whole-RDRAM control with 98,736 writes, reached the title and hangar
phase buckets (632 and 312 VI rows), and emitted valid type-2 task rows at
`0x80033FCC`. This established that the qualified route and task boundary were
observable before changing the port instrument.

The port then ran the qualified concurrent recipe after adding a monotonic
generation at each `M_AUDTASK` handoff in `get_rsp_microcode`. The generation
was copied into the existing source-range and image-stage records. Controls
passed: the oracle recorded 343,395 whole-RDRAM writes, 674 source-span writes,
and 909 valid retail task rows; the port reached title and hangar and emitted
1,024 source rows and 1,903 stage-2 rows. The generation witness itself was
positive: two phase controls, 512 bounded handoff rows, and generation values
in every source/stage row.

Classification of stage-2 rows against source rows in the same phase/arm:

| Class | Rows |
|---|---:|
| exact generation and route | 0 |
| same generation, different route | 230 |
| different generation, same task pointer | 1,671 |
| different generation, same route | 1 |
| no generation match | 1 |

This is a mixed result. It refutes a universal handoff-generation/route
identity. The dominant different-generation/same-pointer class supports a
cross-thread or stale-publication explanation, while the 230 same-generation/
different-route rows independently retain route-publication drift. The current
instrument cannot distinguish those explanations because it does not identify
the execution thread at each handoff/source/stage event. This is single-source
port evidence; the independent retail arm validates route/task coverage but
cannot expose a host generation.

ORIGIN: diagnostic-only generation fields and logging; no guest value was
skipped, rewritten, or guarded.
