# NEXT work unit (s2495) — join image-stage DMAs to the matching audio load rows

HYPOTHESIS-ID: m5-generated-image-downstream-join

## Single work unit

Use one qualified port run to join the established type-2 audio
`osSpTaskLoad` rows (`0x80149470`) to the image-arm stage rows and their
completion rows. Retain the descriptor and scheduler controls, and keep the
new port-load control active. Do not join through type-1 `gspTask`, change task
dispatch, change audio behavior, or add an output remap.

## Competing hypotheses and discriminator

- H-image-load-joined: image-stage events occur after a matching type-2 load
  row and the task's data pointer identifies the same image input/completion
  sequence.
- H-image-load-distinct: type-2 loads are real and retail-matching, but image
  stage/completion rows do not join them by task pointer, data pointer, or
  ordering; the missing edge is downstream of task load.
- H-image-load-unobservable: the route and controls are live but no image
  stage or completion rows occur in the same target phase; move to the actual
  image caller only then.

The discriminator is one phase-keyed table at `0x006AB400` / width 512 with
load task/data fields, image stage event/destination/length/completion, and
same-run ordering. The port target-phase, load, descriptor, scheduler, and
image-stage controls must all fire. A joined task/data/order row selects the
first hypothesis; populated non-joining rows select the second; zero image
rows with live controls select the third.

| Field | Port load hook | Retail oracle | Outcome |
|---|---|---|---|
| type-2 task/data fields and image association | port `osSpTaskLoad` + image-stage rows | retail `0x80033E3C` tuples | joined / distinct |
| target route | port phase 10 / `0x006AB400` | retail 512 / `0x006AB400` | invalid without either |
| positive controls | descriptor + scheduler + image-stage controls | whole-RDRAM 10,000; VI/PIF; retail load hits | invalid without controls |
| image stage/completion | image-stage event, destination, length, completion | retail task/data class only | third hypothesis if absent |

## Exact commands

Use the existing oracle artifact from s2493 and the s2494 port-load artifact;
do not rebuild or alter runtime behavior before adding the complete join
table. Run the qualified `tools/probe.sh` recipe with boot-relative Start
presses, phase gate at 1024, `PROBE_LEAVE_OK=1`, and
`ROGUESQ_LOG_AUDIO_RETURN=1`, `ROGUESQ_LOG_M5_DESCRIPTOR=1`,
`ROGUESQ_LOG_M5_SCHEDULER_ID=1`, and `ROGUESQ_LOG_M5_PORT_LOAD=1`.
Capture under `scratch/agent/s2495_m5_image_downstream_join/` and SIGKILL
through `tools/probe.sh`.
