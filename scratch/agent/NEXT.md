# NEXT work unit (s2083)

HYPOTHESIS-ID: m5-port-fill-crash-origin

## Work unit

Add one bounded, regeneration-stable source reachability table around the
current `fillSampleStreamRange` entry and its four generated callsites in
`funcs_24.c`. Keep the existing target-phase source row and RT64 host witness
unchanged. The new entry/callsite rows must be phase-scoped, rate-limited per
phase, and include edge identity, phase, VI width/origin, target-phase flag,
guest identity, and raw arguments. This is diagnostic-only: do not change
task fields, output routing, canary handling, waits, guards, gate stores, or
host behavior.

## Competing hypotheses and discriminator

- **H-NoRuntimeCall** — the host control and host rows fire, but both the four
  callsite rows and the callee-entry rows remain zero in the qualified route.
- **H-NonTargetEntry** — callsite and entry rows fire, but every entry is
  outside the title/hangar target VI pairs; the existing target-phase source
  filter is therefore correctly quiet at this scope.
- **H-CallsiteEntryMismatch** — a generated callsite row fires but no matching
  callee-entry row follows, indicating a dispatch/symbol or generated-call
  relationship problem.
- **H-TargetEntry** — a callee-entry row fires with a target VI pair. This
  reopens the source/host comparison; only then may a host row carrying
  `0x8000B650` be treated as stale-marker support rather than a witness gap.

The discriminator is one same-run table with the retail whole-RDRAM positive
control, port host-boundary control, four callsite edges, and the callee entry
edge. `host_control > 0` and `host_rows > 0` with both source edge sets at
zero selects H-NoRuntimeCall. Callsite rows without entry rows select
H-CallsiteEntryMismatch. Entry rows only outside target VI pairs select
H-NonTargetEntry. Any target-phase entry row selects H-TargetEntry and keeps
the existing source/host join as the next comparison. A null source result is
not interpreted without the host control, target VI phases, and the all-phase
reachability rows being present.

## Ground truth and exact commands

Run the retail oracle first, with its whole-RDRAM positive control and the
existing retail PC controls. Do not treat a new PC null as evidence unless the
positive control and both title/hangar VI phases are present:

```sh
mkdir -p scratch/agent/s2083_oracle
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --configdir scratch/agent/s2083_oracle \
  --secs 65 \
  --watch-write 0x0:0x800000 --hit-cap 10000 \
  --watch-pc 0x8000B650,0x800668B0,0x8008DA00,0x8009B62C,0x8009B654,0x8009B3EC,0x8009B44C,0x8008EC88,0x80095D54 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace --vi-poll --pif-trace \
  > scratch/agent/s2083_oracle/run.log 2>&1
```

Before editing or building, verify the current generated definition,
callsite addresses, source fixup, and unchanged host witness:

```sh
rg -n -C 5 'fillSampleStreamRange|m5-fill-range-source|ROGUESQ_LOG_FILL_RANGE_ARGS|m5-host-boundary|rs64_phase_ord|rs64_vi_committed' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py \
  lib/rt64/src/hle/rt64_framebuffer.cpp src/main/rt64_render_context.cpp
```

Patch the existing fixup, then regenerate in order and build once:

```sh
cd /Users/williambuckley/Documents/Tools/rogue_squadron64
python3 tools/make_elf.py
cd /Users/williambuckley/Documents/Tools/N64Recomp
./build/N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run one phase-gated capture from the repository root with all source edges and
the existing host witness in the same binary:

```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 \
  ROGUESQ_LOG_FILL_RANGE_ARGS=1 PROBE_PHASE_WIDTH=512 \
  PROBE_PHASE_TIMEOUT=300 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
  zsh tools/probe.sh scratch/agent/s2083_port 120 0.5
```

The source edge rows must be checked for their positive-control activity
before interpreting any target-phase null. Preserve the current no-mitigation
boundary: no wait, guard, task, canary, gate, output, or host change is
authorized.
