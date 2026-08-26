# NEXT work unit (s2382) — M5 gate writer/port downstream join

HYPOTHESIS-ID: m5-gate-writer-port-join

## Work unit

Run the existing same-build M5 downstream capture with the named gate,
service, task, slot, and route markers. Compare its phase-keyed port rows to
the independent s2381 retail writer/value rows. Keep behavior unchanged.

## Competing hypotheses and discriminating measurement

- H-PortGateWriterMatches: the port reaches the same named writer polarity and
  downstream branch/task/slot sequence as retail.
- H-PortGateWriterDiffers: the port writer, value, ordering, or downstream
  sequence differs from retail.
- H-PortGateJoinInvalid: build, route, or positive controls fail, or markers
  cannot be joined by phase.

The discriminator is one phase-keyed row containing retail writer PC/value,
port writer/consumer marker, gate branch result, task dispatch/exit, service
return, slot transition, and route phase. Matching writer polarity plus
downstream closure selects H-PortGateWriterMatches; a positive same-phase
writer with changed source/value/order or downstream result selects
H-PortGateWriterDiffers; missing controls select H-PortGateJoinInvalid.

## Exact commands / controls

Use the existing driver after rebuilding the current tree. It runs the
qualified route and its paired controls; do not change the gate or C88 value.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh

Expected controls are a successful build, first target 640, title 1024,
hangar 512, port phase markers, task/service/slot markers, and a retained
row that can be joined to `scratch/agent/s2381_m5_gate_writer_ground_truth.log`.
If any control is absent, classify H-PortGateJoinInvalid and do not change
gate, fallback, dispatch, VI, task, audio, guard, or mitigation behavior.
