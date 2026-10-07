# Next work unit: requalify the M5 status-03 event ordering

HYPOTHESIS-ID: m5-status03-worker-join

The live-tree fallback now builds and the route qualifies, but the first table
uses separate shutdown/service ordinals and places the only phase-5 store after
the phase-4 shutdown return. Before a new build, make the existing s2028 event
helper use one monotonic sequence for every edge, then rerun the same qualified
silent route. Do not replace the wait, force-clear status, or add a guard.

Competing hypotheses and discriminator:

- H-status03-before-return: the qualified port's `03 -> 00` store sequence lies
  between a service entry and the matching shutdown return.
- H-status03-after-return: the qualified port's store sequence lies after the
  matching shutdown return, so the worker contract is not the observed cause.
- H-status03-route-invalid: the silent arm misses title/hangar or crashes before
  the joined table is phase-qualified; no ordering conclusion is allowed.

The single discriminating measurement is one monotonic, phase-keyed event
sequence joining service entry, `0x8009B7EC` store, and shutdown return on a
route that passes the whole-RDRAM retail positive control plus title 1024 and
hangar 512. Store sequence between entry and return selects before-return;
store sequence after return selects after-return; either missing phase gate or
a pre-gate crash selects route-invalid. A counter that merely proves a branch
ran is not sufficient.

Before running, edit only the regeneration-safe s2028 fixup, run its apply mode,
then build once with all three event classes and run the existing
`scratch/agent/run_s4117_m5_status03_silent.sh` recipe. Use
`PROBE_PHASE_WIDTH` and `PROBE_KEYS_FROM_PHASE=1`; kill only with SIGKILL.
Retry condition: the live `funcs_26.c` contains one shared event-sequence
helper plus service/store/shutdown markers, and the rebuilt binary reaches both
target VIs.
