# NEXT work unit (s1996) — shutdownMusyXVoices inner sites

HYPOTHESIS-ID: hangar-frame-freeze

## What s1995 settled

`finalizeCurrentSpeechBuffer` hangs in
`shutdownMusyXVoices` on call 3 (post
`[drain-exit]`): nenter=3 nexit=2. Calls 1–2
both-edge then take teardown (`a0=0`). 0
`site=free`. H-rs-free / H-teardown-dma /
H-finalize-body REFUTED. Wrap control: those
two earlier shutdown calls both edges printed.
`[fin-slot]` dumped only nenter==1 (pre-title
zeros) — stale for the hanging call. Recipe
keeps `ROGUESQ_DRAIN_INLOOP_TICK=0`.

`shutdownMusyXVoices` (`0x8009BCC4`) is:
one `stopVoiceSlotSynced(s0=0)` (blez loop
runs once), then `L_8009BCEC` spin on
`lbu 0x80154620` until that byte is 0
(`a0` counts zeros, `a1=1`), then
`findAndZeroTableSlotMatching`, optional
`rs_free(*(0x8015467C))`, unconditional
`rs_free(*(0x80154674))`.

## Competing hypotheses

- **H-stop-synced:** `stopVoiceSlotSynced`
  nenter=1 nexit=0 on call 3. Spin never
  reached.
- **H-slot-spin:** stop-synced exits;
  `[shut-spin]` n grows with `v0!=0` /
  `a0!=a1`; `findAndZero` nenter=0.
- **H-find-zero:** spin exits (`a0==a1`);
  `findAndZeroTableSlotMatching` nenter=1
  nexit=0.
- **H-tail-free:** find-zero exits; one of
  the two tail `rs_free` jals nenter=1
  nexit=0.

## Discriminating measurement (one instrument, one build, one 60s probe)

Named enter/exit counters on:
`stopVoiceSlotSynced` (jal `0x8009BCD4`),
`findAndZeroTableSlotMatching` (jal
`0x8009BD28`), `rs_free` at `0x8009BD50`
(site=free-opt), `rs_free` at `0x8009BD60`
(site=free-tail). Log `[shut-post] site=...
nenter= nexit=` on each edge (first 8).

At `L_8009BD10` (`bne $a0,$a1`):
`[shut-spin] n= v0= a0= a1=` first 8 and
every 100000, with `D_80154620` b0 via
`MEM_BU(0, S32(0x80154620u))`.

On every `shutdownMusyXVoices` enter
(n<=8): `[shut-enter] n= b0=` (same S32
load) — fixes s1995's nenter==1-only dump.

Keep `[drain-exit]` / `[drain-post]` /
`[drain-inloop-gate]` / `[fin-post]` /
`[craft-select-s0]`. `S32`. No store
changed. Do not default the in-loop tick
off.

Positive control: `[drain-inloop-gate] en=0`;
`[drain-exit] v0=1`; `[fin-post] site=shutdown
nenter=3 nexit=2`; `[shut-enter] n=1` and n=2
both followed by `[shut-post]` both-edge on
the sites those calls take; call 3
`[shut-enter] n=3` (function entered).

Outcomes:
- stop-synced nenter++ without nexit on
  call 3 → H-stop-synced
- stop-synced exits; shut-spin n grows
  with v0!=0; find-zero nenter=0 →
  H-slot-spin (`b0` is the extra key)
- spin exits; find-zero nenter=1 nexit=0 →
  H-find-zero
- find-zero exits; free-opt or free-tail
  nenter=1 nexit=0 → H-tail-free

SENTINEL is applied — incremental edit, do
not rerun full fixup.

## Exact patch sites

- Incremental wrap in `shutdownMusyXVoices`
  (`funcs_26.c`) via
  `apply_s1996_shutdown_inner` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- `[shut-enter]` at function entry;
  `[shut-spin]` at `0x8009BD10`.

## Exact test

```sh
mkdir -p scratch/agent/s1996_shutdown_inner
env ROGUESQ_DRAIN_INLOOP_TICK=0 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1996_shutdown_inner 60 2
```
