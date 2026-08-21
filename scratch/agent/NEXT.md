# NEXT work unit (s2082)

HYPOTHESIS-ID: m5-port-fill-crash-origin

## Work unit

Repair the regeneration-stable source-side witness for
`fillSampleStreamRange`. The current generated definition is in
`N64Recomp/RecompiledFuncs/funcs_24.c`, while the existing fixup anchor is
file-scoped to `funcs_23.c`, so `ROGUESQ_LOG_FILL_RANGE_ARGS=1` produces no
rows. Make the fixup target the current function placement and emit one
phase-scoped `[m5-fill-range-source]` row per source call with a source ordinal,
`0x8008FAAC` identity, raw arguments, and current `g_rs64_last_guest_pc`.
Keep the existing RT64 host witness unchanged. This is diagnostic-only: do not
change task fields, output routing, canary handling, waits, guards, gate
stores, or host behavior.

## Competing hypotheses and discriminator

- **H-StaleLastGuestPC** — source rows fire in the target phase, but host rows
  continue to carry `0x8000B650` without a same-event source identity.
- **H-HostCopyReadback** — a phase-valid source row and host row share the
  source identity/ordinal at the boundary, and the host row carries that live
  identity rather than the stale marker.
- **H-WitnessGap** — the host control fires but source rows remain absent or
  cannot be joined, so the instrument still cannot distinguish the two.

The discriminator is one same-run table with the retail whole-RDRAM positive
control, the port host-boundary control, phase-keyed fill-range source rows,
and phase-keyed host rows. If source rows exist but host rows retain
`0x8000B650` without a same-event source identity, select H-StaleLastGuestPC.
If a source/host identity join is live through the boundary, select
H-HostCopyReadback. If the controls fire but the source side or join is absent,
select H-WitnessGap and redesign before interpretation.

## Ground truth and exact commands

Run the retail oracle first, with its whole-RDRAM positive control and the
already-qualified title/hangar route. Use the existing PC set as a control;
do not treat a new null as evidence unless the positive control and VI phases
are present:

```sh
mkdir -p scratch/agent/s2082_oracle
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --configdir scratch/agent/s2082_oracle \
  --secs 65 \
  --watch-write 0x0:0x800000 --hit-cap 10000 \
  --watch-pc 0x8000B650,0x800668B0,0x8008DA00,0x8009B62C,0x8009B654,0x8009B3EC,0x8009B44C,0x8008EC88,0x80095D54 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace --vi-poll --pif-trace \
  > scratch/agent/s2082_oracle/run.log 2>&1
```

Before editing, locate the current generated definition, fixup anchor, host
boundary, and phase helpers:

```sh
rg -n -C 6 'fillSampleStreamRange|ROGUESQ_LOG_FILL_RANGE_ARGS|copyToRAM|g_rs64_last_guest_pc|rs64_phase_ord|vi_width|vi_origin' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py lib/rt64 src
```

Patch the existing fixup anchor, regenerate in the required order, build once,
and run one phase-gated capture from `build/` with the retail/port positive
controls and both source/host witnesses enabled in the same binary. Use the
known stable hangar gate if the title gate stalls:

```sh
cd /Users/williambuckley/Documents/Tools/N64Recomp
./build/N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 \
  ROGUESQ_LOG_FILL_RANGE_ARGS=1 PROBE_PHASE_WIDTH=512 \
  PROBE_PHASE_TIMEOUT=300 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
  zsh tools/probe.sh scratch/agent/s2082_port 120 0.5
```

Expected outcomes are the three rows above. The source row must visibly fire in
the target phase before a null can select H-StaleLastGuestPC; no wait, guard,
task, canary, gate, output treatment, or host behavior change is permitted.
