# NEXT work unit (s2081)

HYPOTHESIS-ID: m5-port-fill-crash-origin

## Work unit

Add one regeneration-stable, phase-scoped host/guest boundary witness at the
existing RT64 copy/readback boundary. The witness must report the host
operation, the current `g_rs64_last_guest_pc`, and the active VI phase in one
joinable row. It is diagnostic-only: do not change task fields, output routing,
canary handling, waits, guards, gate stores, or host behavior.

## Competing hypotheses and discriminator

- **H-StaleLastGuestPC** — the witness shows a host copy/readback event with
  `g_rs64_last_guest_pc=0x8000B650`, but no guest execution row for
  `fillSampleStreamRange` in the same phase/join. This keeps the marker as
  shared stale state.
- **H-HostCopyReadback** — the witness shows the host operation immediately
  follows a phase-valid fill-range call and carries the same joined guest
  source/operation identity into the fault. This would make the host boundary
  causal, without authorizing a behavior change.
- **H-WitnessGap** — the positive control fires but the boundary witness never
  produces a joinable row, so the instrument cannot distinguish the two. This
  requires fixing the witness scope, not changing runtime behavior.

The discriminator is one same-run table with a whole-RDRAM or existing
copy/readback positive control, phase-keyed fill-range source rows, and
phase-keyed host-boundary rows joined by guest address and operation ordinal.
If the host row carries `0x8000B650` without a same-phase fill source, select
H-StaleLastGuestPC. If it carries a same-phase source/operation join through
the host boundary, select H-HostCopyReadback. If the positive control fires
but either side is absent, select H-WitnessGap and redesign before any
interpretation.

## Ground truth and exact commands

Run the retail oracle first, with its whole-RDRAM positive control and the
already-qualified title/hangar route. Use the existing PC set as a control;
do not treat a new null as evidence unless the positive control and VI phases
are present:

```sh
mkdir -p scratch/agent/s2081_oracle
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --configdir scratch/agent/s2081_oracle \
  --secs 65 \
  --watch-write 0x0:0x800000 --hit-cap 10000 \
  --watch-pc 0x8000B650,0x800668B0,0x8008DA00,0x8009B62C,0x8009B654,0x8009B3EC,0x8009B44C,0x8008EC88,0x80095D54 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace --vi-poll --pif-trace \
  > scratch/agent/s2081_oracle/run.log 2>&1
```

Before editing, locate the existing host boundary and phase helpers:

```sh
rg -n -C 6 'copyToRAM|g_rs64_last_guest_pc|PROBE_PHASE|vi_width|vi_origin' lib/rt64 src
```

Add the single witness in that existing host path, build once through the
normal host-only build, and run one phase-gated capture from `build/` with the
positive control and witness enabled in the same binary:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_KEYS='8:start' \
  zsh tools/probe.sh scratch/agent/s2081_port 120 0.5
```

Expected outcomes are the three rows above; no wait, guard, task, canary,
gate, or output treatment is permitted.
