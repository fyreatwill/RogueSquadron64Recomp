# NEXT work unit (s993)

HYPOTHESIS-ID: m4-zero-shade-writer

## One work unit

Regenerate a clean `../N64Recomp/RecompiledFuncs/` tree, apply the new
regeneration-safe generated ordinary-store census, build, and run one
phase-gated capture. Do not hand-edit generated files or add a mitigation.

Competing hypotheses and discriminating measurement:

- H-generated-target: exact phase-4/phase-6 target overlap records with a
  matching generated guest PC.
- H-generated-unrelated: the generated probe fires its positive control and
  records only non-target shared-page stores.
- H-runtime-copy: the generated probe fires its positive control but records no
  target-range store, leaving runtime copy/state conversion as the remaining
  class.

The discriminating measurement is the phase-scoped exact-target generated-store
count and records, compared with non-target shared-page records. The run is
invalid unless `[vtx-generated-write-control] control=1`, F5/shade, and all-DMA
controls visibly fire.

## Exact commands

Use the documented delete-before-regen pipeline (`make_elf.py`, N64Recomp,
then fixup) without touching unrelated dirty files. Apply the fixup with:

`env RS64_FIXUP_S992_GENERATED_WRITES=1 python3 ../N64Recomp/fixup_game_funcs.py`

Then:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LLE_FORCE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_PHASE_TIMEOUT=180 PROBE_START=0 PROBE_KEYS='20:start' zsh tools/probe.sh scratch/agent/probe_s993 180 1`

The s992 static match count is not evidence about target-byte ownership.
