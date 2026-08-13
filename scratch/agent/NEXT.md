# NEXT work unit (classify the late E9 parser condition)

HYPOTHESIS-ID: m3-rdp-parser-condition

Perform one phase-gated source/runtime parser-condition probe for the lower
late authoritative E9 count. Keep the existing E9 provenance, parser-range,
triangle owner, triangle boundary, and DL-sync controls. Add only bounded
condition-tagged records at every authoritative parser command-start decision
that can explain an emitted E9 slot: direct command start, preceding command
span, pending completion, or no association. Carry task, submit serial, exact
range, and candidate address where applicable. Do not change parser advance,
RDP handlers, or any mitigation.

Competing hypotheses and discriminator:

- H-direct-filter: late bridge E9 slots are at parser command starts but are
  excluded by an authoritative parser filter or opcode/byte-order condition.
- H-span-accounting: late bridge E9 slots are covered by a preceding non-E9
  command span, so the lower E9 count is correct command-boundary accounting.
- H-pending: the late slots are completed through the pending-command path and
  are omitted from the direct-start count.
- H-unassociated: the slots are outside all authoritative parser ranges,
  reopening a range-association defect.

Discriminator: classify every retained late bridge E9 slot with a same-task,
same-serial parser record. Direct-start hits select H-direct-filter; span hits
select H-span-accounting; pending hits select H-pending; no association with
positive controls selects H-unassociated. A null is invalid unless the E9
provenance and parser command-start controls fire in the same run.

Exact execution:

1. `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Run from the repository root:

`env ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_DISPATCH=1 ROGUESQ_LOG_RDP_ADVANCE=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_TRI_DISPATCH=1 ROGUESQ_LOG_TRI_BOUNDARY=1 ROGUESQ_LOG_TRI_WRITER=1 ROGUESQ_LOG_RDP_CONDITION=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/agent/s790_postsec2_reachability.sh`

Do not run a cross-run animating comparison.
