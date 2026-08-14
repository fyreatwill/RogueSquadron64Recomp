# NEXT work unit (s1018)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Audit why the corrected 1024-gated capture did not execute the landed M4 probe.
Use the saved s1018 capture and static artifact inspection; do not run another
game capture until the probe-bearing artifact and active ucode path are
identified.

Competing hypotheses and discriminating measurement:

- `H-stale-build-link`: the probe-bearing generated overlay is not present in
  the linked executable used by `build/Debug`.
- `H-active-ucode-mismatch`: the executable contains the probe, but runtime
  selects a different Factor 5 ucode artifact or overlay for the observed
  scene.
- `H-env-or-callsite`: the active artifact and symbol are present, but the
  environment gate or probe call site is not reached/recognized.

The discriminator is one artifact/runtime table: source hook presence in the
active generated overlay, symbol/string presence in the linked executable,
runtime ucode-selection records in the saved log, and env-gate parsing. A
missing linked symbol selects stale-build/link; a present symbol with a
different active ucode selects overlay mismatch; all artifact and selection
controls positive with zero rows selects env/call-site reachability.

Exact commands:

`rg -n "rs64_m4_accum_probe|ROGUESQ_LOG_M4_ACCUM" build/factor5_ucode/factor5_ucode_ovl20_recompiled.c src/rsp/dpc_bridge.cpp`

`strings build/Debug/RogueSquadron64Recomp.exe | rg "rs64_m4_accum_probe|M4_ACCUM|factor5_ucode|ovl20"`

`rg -n "loadUCode|ucode|overlay|IMEM|M4|m4" scratch/agent/probe_results/m4_accum_1024/run.log | tail -120`
