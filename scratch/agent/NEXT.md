# NEXT: phase-map the runtime writer of voice 0x801724C0 +0x34
HYPOTHESIS-ID: m5-audio-destub

s4598 completed the target-phase generated-store census. The adjacent
generated-store control fired at VI 640/origin 0x006A2900, but there was no
generated store to physical 0x1724F4 before the known odd-PI alignment abort.
The independent retail oracle had a positive whole-RDRAM control and four
target writes from 0x80007670 during retail VI 512. This rules out a
target-phase generated writer, but does not distinguish a pre-640 generated
writer from a host/translation write.

Next work unit: change the census to bounded per-phase target rows covering
boot through the first target-phase edge. Keep the adjacent generated-store
control in every phase. Do not add a mitigation.

Competing hypotheses:

- H-prephase-guest: a generated guest store writes 0x1724F4 before VI 640;
  its first row will name the PC, value, width, and phase.
- H-host-translation: no generated store writes the target in any phase, so
  the field enters through host/translation state or an uninstrumented path.
- H-other-guest: a generated writer outside the two statically named
  init/keyon sites writes it in an earlier phase.

Discriminating measurement: one run with phase-bucketed target rows from the
first VI through VI 640, plus an adjacent-range generated-store control that
fires in the same run. A target row at any earlier phase selects H-prephase-
guest or H-other-guest by PC; zero lifetime target rows with the control live
leaves H-host-translation as the remaining generated-store-boundary result.

Exact sequence:

1. Extend `tools/apply_s4598_complete_store_census.py` (or add the next
   regeneration-preserved fixer) so `rs64_s4597_target_store` records a small
   per-phase first-row table rather than filtering to width 640/origin
   0x006A2900. Retain the target and adjacent control ranges.
2. Run `python3 tools/apply_s4598_complete_store_census.py` and build with
   `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Run from `build/` with
   `ROGUESQ_NODEFAULT=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
   ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1`, repeated Start input,
   and the phase/store logger. Capture to `scratch/agent/s4599_port_run/` and
   SIGKILL the game after the target route or the known PI abort.

The previous run's artifacts are `scratch/agent/s4598_oracle.log` and
`scratch/agent/s4598_port_run/run.log`; do not rerun them as the next unit.
