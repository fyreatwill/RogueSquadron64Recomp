# NEXT work unit (s2585) — identify the missing port-side writer contract for M5

HYPOTHESIS-ID: m5-audio-contract-gap

## Single work unit

Run one bounded static/runtime census of the port-side writers for the two
retail-attributed boundaries (`0xA0F50` writer PC `0x8008ED48` and `0x141AD0`
writer PC `0x80094648`). First enumerate every generated/patch function that
writes those guest addresses or the PCM candidate spans, then instrument the
complete writer class in one build so the qualified image run records
callsite, destination, post-store value, and phase. Do not change behavior or
promote any task/output field.

## Competing hypotheses and discriminator

- `H-PortWriterReachable`: a named port writer reaches one of the retail
  boundaries with a matching phase and value; the join is later.
- `H-PortWriterUninstrumented`: static enumeration finds a writer class, but
  the run shows no corresponding callsite/value row.
- `H-PortContractElsewhere`: the complete enumerated writer class fires, but
  writes another destination or polarity than retail.

The discriminator is one phase-keyed table covering every statically
enumerated writer callsite, destination, post-store value polarity, PCM
source/consumer join, and route phase, with `audtask-dispatch`, image
completion, and title/hangar VI as positive controls. A matching row selects
`H-PortWriterReachable`; a complete census with no row selects
`H-PortWriterUninstrumented`; only off-range/nonmatching writes select
`H-PortContractElsewhere`. If a phase control or census control is absent,
the capture is unevaluable.

## Exact command

```sh
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ROGUESQ_LOG_M5_PCM_WRITER=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_AUDTASK=1 \
  ./build/RogueSquadron64Recomp > scratch/agent/s2585_m5_port_writer_census.log 2>&1
```

Use the existing phase controls and kill the process group with SIGKILL after
the target phases are present. Record whether every positive control fired
before interpreting the port table.
