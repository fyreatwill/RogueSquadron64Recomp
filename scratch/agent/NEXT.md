# NEXT work unit (s2007) — status-3 reachability boundary

HYPOTHESIS-ID: m5-status3-worker-dispatch

## Status at session start

The s2006 callback census is live: two port captures each produced 24
phase-gated `serviceVoicePoolFrame` entry/exit pairs at status `0x00`, phase
6, thread 0. Neither capture reached a status-3 row. The full recipe and the
`p1:start,p2:a` recipe hit the existing odd-ROM-address assertion in
`recomp::do_rom_read` after the indirect callback dispatch; the one-probe
`p1:start` capture was SIGKILLed before that assertion. The retail oracle has
already passed its corrected positive-control schedule and seen the real
`0x8009B7EC` writer, but the port's shutdown call-3 boundary is unevaluated.

## Competing hypotheses

- **H-call3-reached:** shutdown call 3 and the `L_8009BD10` status-3 spin are
  reached before the PI worker assertion; the existing worker-dispatch rows
  can then be interpreted against status `0x03`.
- **H-no-call3:** the current post-craft transition never reaches shutdown
  call 3; the missing status-3 rows are a state-machine/reachability issue,
  not a scheduler result.
- **H-pi-preempts:** the PI worker aborts first, before shutdown call 3; the
  missing status-3 rows are an instrumentation boundary caused by the
  unrelated odd ROM address, not evidence about audio dispatch.
- **H-status3-precedes-pi:** call 3/spin is present, but the phase-gated
  worker rows remain absent before the PI assertion; only this outcome
  permits a status-3 dispatch hypothesis to remain live.

## Discriminating measurement

One phase-gated table in one build/run must add shutdown entry/exit and
`L_8009BD10` spin rows to the existing s2006 callback table. Join each row to
the PI assertion timeline by ordinal/time. Include: shutdown call number,
`D_80154620` value, spin `a0/a1/v0`, worker thread identity, service
entry/exit, callback dispatch/return, expected `0x8009B7EC` store, and the
first odd PI ROM address. Shutdown calls 1 and 2, and the existing 24 service
entry/exit pairs, are positive controls.

- call 3/spin before PI assertion selects H-call3-reached;
- no call 3 with PI assertion first selects H-pi-preempts;
- no call 3 and no PI assertion in a clean fixed capture selects H-no-call3;
- call 3/spin before PI plus missing post-status-3 worker edges keeps only
  H-status3-precedes-pi live; do not add a mitigation from that result.

## Exact commands

### Step 1 — independent retail control first

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --watch-write 0x0:0x800000 --watch-write 0x154620:0x154624 --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2007-oracle.log 2>&1
```

Require the whole-RDRAM positive-control threshold, a nonzero target watch,
and a retail `0x8009B7EC` writer before trusting a port null.

### Step 2 — static census, batched fixup, and build

```sh
rg -n 'shutdownMusyXVoices|8009BCC4|8009BD10|serviceVoicePoolFrame|8009B7EC' syms tools patches
rg -n 'shutdownMusyXVoices|8009BCC4|8009BD10|serviceVoicePoolFrame|8009B7EC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
env RS64_S2007_STATUS3_REACH=1 python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp
```

The fixup must add only diagnostics: shutdown entry/exit and spin rows in the
same generated-tree path as s2006. Do not change the spin, PI handling, audio
dispatch, or in-loop tick. Do not regenerate over the existing sentinel
without first using the documented generated-tree workflow.

### Step 3 — one phase-gated port capture

```sh
env PROBES_OVERRIDE="p1:start:5 p2:a:3" ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_THREADS=1 ROGUESQ_LOG_RUNNER_ALL=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_SCHED=1 ROGUESQ_LOG_THREAD_RESUME=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2007-status3-reach 0 12 > scratch/agent/s2007-status3-reach.log 2>&1
```

Require VI 1024 / `0x00790400` and VI 512 / `0x006AB400` when available.
The script must SIGKILL the game; do not use SIGTERM. Preserve the default
status-3 spin and do not set `ROGUESQ_DRAIN_INLOOP_TICK=0`.

## Stop condition

If the new table still cannot place shutdown call 3 relative to the PI
assertion, record that reachability ambiguity and redesign one probe. Do not
add another callback field or infer scheduler starvation from a pre-status-3
null.
