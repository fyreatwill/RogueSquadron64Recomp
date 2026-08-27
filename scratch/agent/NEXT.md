# NEXT work unit (s2584) — port-side writer/value correspondence for M5

HYPOTHESIS-ID: m5-audio-contract-gap

## Single work unit

Run one bounded port capture using the existing phase-gated PCM
writer/source instrumentation, and correlate its writer callsites and values
against the retail PCs/ranges from s2583. Do not alter the port or promote any
task/output field.

## Competing hypotheses and discriminator

- `H-PortWriterMatch`: the port reaches the same phase-owned ranges with a
  matching writer callsite and nonzero value; the missing PCM join is later.
- `H-PortWriterMissing`: retail's named writer/value event has no port-side
  counterpart in the same phase.
- `H-PortAddressMismatch`: the port writes nonzero data, but outside the two
  retail candidate ranges or under a different phase key.

The discriminator is one phase-keyed table of port writer callsite,
destination range, post-store value polarity, PCM source/consumer join, and
route phase, with `audtask-dispatch`, image completion, and title/hangar VI as
positive controls. A matching writer/value selects `H-PortWriterMatch`; no
matching event selects `H-PortWriterMissing`; nonzero output only outside the
retail ranges selects `H-PortAddressMismatch`. If a phase control is absent,
the capture is unevaluable.

## Exact command

```sh
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ROGUESQ_LOG_M5_PCM_WRITER=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_AUDTASK=1 \
  ./build/Debug/RogueSquadron64Recomp > scratch/agent/s2584_m5_port_writer_value.log 2>&1
```

Use the existing phase controls and kill the process group with SIGKILL after
the target phases are present. Record whether every positive control fired
before interpreting the port table.
