# NEXT work unit — qualify port slot/status edge against retail

HYPOTHESIS-ID: m5-slot-status-contract-gap

Session 3346 observed the retail guest indirect edge
`0x800919D4 -> 0x800919EC -> 0x80007910` with matching `prev_pc`, while the
positive control and title phase were live. The pointer-source/host-dispatch
thread is closed for this observed transfer. The remaining M5 Step 1 question
is the port's missing slot/status consumer relation in reachable hangar.

Competing hypotheses:

- `H-PortSlotStatusMissing`: the reachable port hangar truly lacks the writer
  or status transition seen in retail.
- `H-PortConsumerUnreached`: the port writes the state, but the named consumer
  path is not reached on the qualified route.
- `H-PortProbeGap`: the port has both edges and the current instrumentation
  misses them.

The next discriminating measurement is one same-build port run using the
validated LLE/image hangar recipe, with whole-run host/task/PCM controls and
phase-gated rows for the slot/status ranges `0x80141AD8:0x80141AF0` and
`0x80154620:0x801546A0`, plus execution watches at
`0x80094648,0x8009B600,0x8009B85C,0x8009BDE8`. A target-phase writer with
consumer hits selects a complete port edge; writer rows without consumers
select `H-PortConsumerUnreached`; neither writer nor consumer rows with all
controls selects `H-PortSlotStatusMissing`; control-positive rows at the
known consumer PCs with no target rows select `H-PortProbeGap`. Build once,
run once, and do not change behavior or add a mitigation.

Exact command/script:

    sed -n '1,220p' scratch/agent/run_s2289_m5_retail_slot_route.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_M5_SLOT_STATUS=1 zsh scratch/agent/run_s2289_m5_retail_slot_route.sh
