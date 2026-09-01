# NEXT work unit — M5 upstream selector producer comparison

HYPOTHESIS-ID: m5-upstream-selector-producer

Session 3498 selected selector/input divergence: the qualified port exposed
`0x8018DD30`, `0x80171CE0`, and `0x80173B20`, while the independent retail
title observations exposed `0x80171CE0`. The next unit is the upstream
producer comparison, not another route retry.

Competing hypotheses and discriminating outcomes:

- `H-ProducerParity`: producer index/table/source rows match across retail and
  port at the title origin.
- `H-ProducerDivergence`: both producer controls fire, but the first producer
  index/table/source/value class differs across runtimes.
- `H-ProducerObservationFailure`: a positive route control fires but a
  producer control or rows are absent, leaving the boundary unevaluable.

Discriminating measurement: build once, run the independent retail arm and
the qualified real-image/LLE/spin-yield port arm with phase-gated rows at the
producer immediately feeding `0x80091060`/`0x80091074`. Include selector index,
table address, loaded value, source family, title origin, and the existing
four-PC/task/route controls. Matching producer classes select
`H-ProducerParity`; live controls with the first differing producer class
select `H-ProducerDivergence`; a missing producer control with a live route
selects `H-ProducerObservationFailure`. No null is interpreted without the
phase and positive control.

Exact run requirements: use the qualified real-image/LLE/spin-yield route
from `build/`, enable `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_LOG_PHASE=1`, `ROGUESQ_LOG_VI_TRANSITION=1`,
`ROGUESQ_LOG_M5_TASK_WRITER=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`, and the
producer plus selector-load/writer controls. Run the independent retail
preflight first, use a direct-PID watchdog, capture under `scratch/agent/`,
and terminate survivors with SIGKILL.
