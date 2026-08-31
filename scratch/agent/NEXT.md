# NEXT work unit — port M5 consumer entry qualification

HYPOTHESIS-ID: m5-consumer-reachability-audit

Session 3351's retail oracle passed the whole-RDRAM control, reached hangar
`512 @ 0x006AB400`, and executed all five named PCs with stable previous-PC
chains. `H-ConsumerWrongNames` is refuted on retail; the remaining split is
port reachability versus a port status/slot gate.

Competing hypotheses for the next unit:

- `H-PortConsumerIndirectGap`: retail executes the five bodies, but the port
  does not reach the corresponding generated entries.
- `H-PortConsumerGate`: the port reaches the entries, but its slot/status
  predicate prevents the downstream consumer work.
- `H-PortProbeMismatch`: the existing port probe labels do not cover the
  actual generated consumer entries.

Discriminator: add regeneration-surviving entry counters for all five PCs to
the existing port probe, build once, and run the validated extended
Start/spin-yield recipe with host/task/PCM, title `1024`, and hangar
`512 @ 0x006AB400` controls. All five port entries zero with live controls
selects `H-PortConsumerIndirectGap`; entries live while existing slot/status
rows remain active selects `H-PortConsumerGate`; entries live and the current
probe remains silent selects `H-PortProbeMismatch`. Missing controls invalidate
the run, not a null.

Exact preparation and run shape:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    cd build/Debug
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ./RogueSquadron64Recomp > ../../scratch/agent/s3352_m5_port_consumer_entry.log 2>&1

The entry probe must be added to the regeneration/fixup path before this
build; do not hand-edit generated functions. Use SIGKILL if the watchdog must
stop the process.
