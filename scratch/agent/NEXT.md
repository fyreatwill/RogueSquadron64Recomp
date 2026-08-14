# NEXT work unit (s1154)

HYPOTHESIS-ID: post640-vi-producer-gate

Build one phase-scoped census of every generated `osViSetMode` caller and its
state/input predecessor, keeping the existing host selector positive control,
slot-dispatch control, and host-input control. The target window begins at the
last committed width-640 record and ends at timeout; do not use a stopwatch.
This is the next highest-information probe after three unevaluable owner runs.

Competing hypotheses and discriminator:

- H1/state-gate-active: a generated producer or exact predecessor fires after
  the final 640 commit while slot dispatch and host input continue.
- H2/producer-absent: no generated producer or predecessor fires after the
  final 640 commit, while the independent controls continue.
- H3/early-loop-stop: slot dispatch or host input stops before the producer
  window, so the post-640 state gate is not reached.

The discriminating measurement is one run with a positive host selector,
positive slot/input controls, and phase-scoped generated producer/predecessor
markers. Producer-positive proves an unobserved state gate; producer-zero with
continuing controls proves the active-loop path and sends the next audit to the
state writer. If the controls stop first, the result is an early-loop stop and
the next probe must target that boundary.

Before building, record the competing hypotheses and discriminator above in the
durable probe path, then regenerate in the required order:

    python tools/make_elf.py
    build/Debug/N64Recomp.exe rogue_squadron.toml
    python tools/fixup_game_funcs.py
    cmake --build build --config Debug --target RogueSquadron64Recomp

Run from the repo root with the existing 1024 gate and known input schedule:

    env ROGUESQ_LOG_VI_SELECTOR=1 ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_HOST_INPUT=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_PHASE_KEYS_FROM_PHASE=1 PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:start 250:start" PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/soak_results/s1154_post640_vi_producer_gate 300 2
