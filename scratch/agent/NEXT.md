# Next work unit: complete the A11 terminal-transition table on a qualified route

Session 4123 was H-A11-route-invalid because the port launch omitted the
canonical AUTOPILOT/phase-gate driver: it reached title but not the required
hangar phase. Execute exactly one complete A11 terminal-transition capture
next on the canonical qualified route; do not remove the wait cap, replace the
wait, or force a slot state.

HYPOTHESIS-ID: m5-step9-wait-for-any-audio-slot-class

Competing hypotheses and discriminator:

- H-A11-terminal-slot: the pending `chCount=16` call has a valid terminal slot
  transition that was not logged by the first capture; the full writer table
  will show the return edge.
- H-A11-nonterminal-slot: a slot `01/02/00` writer or predicate input remains
  nonterminal, explaining the missing return without a cap fire.
- H-A11-route-invalid: a required positive control or title/hangar phase is
  missing, so wait and guard nulls are unevaluable. This was selected by s4123
  for the non-AUTOPILOT launch and must be rejected before interpreting nulls.

The single discriminating measurement is one same-build phase-gated port
capture with the complete writer/terminal table. A missing control or phase
selects H-A11-route-invalid; a terminal transition joined to the pending call
selects H-A11-terminal-slot; otherwise a still-pending call with both phases
selects H-A11-nonterminal-slot. Do not alter the wait or cap.

Before building, use bounded `rg` searches in the generated tree, fixup
script, and oracle watch configuration to enumerate the full idiom. Use the
canonical phase-gated driver that was missing in s4123:
`ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024
PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1
ROGUESQ_LOG_PHASE=1`, plus the qualified route parameters:
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_SPIN_YIELD=1
ROGUESQ_M5_C88_VALUE=0 ROGUESQ_AUDIO_UCODE=1`.

Required build:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Required run properties: oracle first, whole-RDRAM positive control, exact
title/hangar VI phase gates, port positive controls, all route parameters above,
`ROGUESQ_LOG_M5_WAIT_CONTRACT=1`, `ROGUESQ_LOG_M5_KEYON_CENSUS=1`, and SIGKILL
cleanup.
