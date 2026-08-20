# NEXT work unit (s2006) — status-3 worker-dispatch census

HYPOTHESIS-ID: m5-status3-worker-dispatch

## Status at session start

Session 2005 closed the M5 DMA-to-`queue_samples` boundary for the two
nonzero hangar buffers: post-DMA and pre-queue FNV/nonzero counts matched at
guest addresses `0x80166450` and `0x80166750`. Do not reopen that boundary or
change default audio dispatch. The parked hangar freeze remains the next M5
lead: after `shutdownMusyXVoices` enters the status-3 spin, the retail worker
continues writing `0x80154620` from `0x8009B7EC`, while the port has no armed
`serviceVoicePoolFrame` entry.

## Competing hypotheses

- **H-status3-starves-worker:** the worker is ready, but the cooperative
  status-3 spin monopolizes execution; no post-spin `serviceVoicePoolFrame`
  entry or scheduler turn occurs until the spin is externally broken.
- **H-dispatch-unregistered:** the port never dispatches the worker callback
  after its earlier positive-control entries, independent of the shutdown
  spin; the worker has no wake/queue handoff.
- **H-worker-body-blocks:** the callback is dispatched after status 3, but its
  entry has no matching exit because the worker body blocks or faults before
  the expected service write.
- **H-service-writes-elsewhere:** entry and exit continue after status 3 and
  the missing `0x80154620` write is a store/guest-address mismatch rather than
  scheduler starvation.

## Discriminating measurement

One phase-gated table in one build/run, with a row for every
`serviceVoicePoolFrame` entry/exit and every owning worker scheduler
dispatch/ready/block transition, joined to the status-3 spin sample by
ordinal. The table must include: pre/post-status-3, guest PC, worker/thread
identity, entry/exit edge, `D_80154620` status, and whether the expected
`0x80154620` store probe fired. The pre-status-3 service entry/exit and the
`[svc-pool]` counter are positive controls; a counter that only proves the
spin ran is not a control.

- No post-status-3 service entry, with a ready worker and no scheduler turn,
  selects H-status3-starves-worker.
- No post-status-3 service entry and no ready/wake/dispatch event, while the
  pre-status-3 control is live, selects H-dispatch-unregistered.
- A post-status-3 entry without exit selects H-worker-body-blocks.
- Post-status-3 entry/exit plus scheduler turns but no expected store selects
  H-service-writes-elsewhere; do not add a store mitigation from this result.

## Exact commands

### Step 1 — independent retail control first

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 45 --watch-write 0x0:0x800000 --watch-write 0x154620:0x154624 --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start > scratch/agent/s2006-oracle.log 2>&1
```

Require nonzero whole-RDRAM hits and a `0x154620` hit from retail PC
`0x8009B7EC` before trusting a port null.

### Step 2 — static dispatch census and one batched port instrument

```sh
rg -n 'serviceVoicePoolFrame|8009B5A8|8009B7EC|8009BD10' syms tools patches
rg -n 'serviceVoicePoolFrame|8009B5A8|8009B7EC|8009BD10' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
```

Use the generated-tree/fixup path identified by that census to add all entry,
exit, scheduler-edge, status-3, and expected-store rows in one build. Preserve
the default status-3 spin and do not enable `ROGUESQ_DRAIN_INLOOP_TICK=0`.
Export any `lib/` changes with `./submodule-patches/export.sh`, then build:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

### Step 3 — one phase-gated run

```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_THREADS=1 ROGUESQ_LOG_RUNNER_ALL=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2006-status3 180 12 > scratch/agent/s2006-status3.log 2>&1
```

`ROGUESQ_SPIN_YIELD=1` is only the established boot/title/hangar-entry aid;
the status-3 shutdown spin itself must remain unyielded. Require VI 1024 /
`0x00790400` and VI 512 / `0x006AB400`, then join the complete table around
`[shut-enter]`/`[shut-spin]`/`[shut-exit]`.

## Stop condition

If the table cannot distinguish the four outcomes, do not add another field.
Record the ambiguity and redesign the next highest-information-value probe.
