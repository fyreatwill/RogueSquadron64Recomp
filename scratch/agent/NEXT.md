# RESUME: phase-map the runtime writer of voice 0x801724C0 +0x34
HYPOTHESIS-ID: m5-audio-destub

Checkpoint close-out for the interrupted s4598 work unit. Do not rerun
s4598 artifacts. The independent retail oracle and the qualified port run
completed; the port reached VI 640/origin 0x006A2900, the adjacent generated
store control fired, and the target generated-store witness produced zero
rows before the known odd-PI alignment abort. Artifacts:
`scratch/agent/s4598_oracle.log` and `scratch/agent/s4598_port_run/run.log`.

Competing hypotheses and discriminator:

- H-prephase-guest: a generated guest store writes physical 0x1724F4 before
  VI 640. A phase-bucketed row names its PC, value, width, and phase.
- H-host-translation: no generated store writes the target in any phase;
  the value enters through host/translation state or an uninstrumented path.
- H-other-guest: an earlier generated writer outside the statically named
  init/keyon sites writes the target. A row names that writer.

The discriminating measurement is one run with target rows bucketed from the
first VI through VI 640, while retaining the adjacent generated-store control
in every phase. Any earlier target row selects H-prephase-guest or H-other-
guest by PC. Zero lifetime target rows with the control live selects
H-host-translation at the generated-store boundary.

Resume commands from the repository root:

1. Extend `tools/apply_s4598_complete_store_census.py` (or add the next
   regeneration-preserved fixer) so `rs64_s4597_target_store` records a small
   per-phase first-row table instead of filtering to width 640/origin
   0x006A2900; retain the target and adjacent controls.
2. Run `python3 tools/apply_s4598_complete_store_census.py`.
3. Build with `cmake --build build --config Debug --target RogueSquadron64Recomp`.
4. Run the qualified route from `build/` with the existing real-LLE flags,
   phase/store logger, repeated Start input, and SIGKILL watchdog. Capture to
   `scratch/agent/s4599_port_run/`.

Do not add a mitigation. The s4598 target-phase result is already recorded in
PORTING-STATE.md and docs/CURRENT-TRUTH.md.
