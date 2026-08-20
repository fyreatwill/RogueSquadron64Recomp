# NEXT work unit (s1997) — serviceVoicePoolFrame during status-3 spin

HYPOTHESIS-ID: hangar-frame-freeze

## What s1996 settled

`shutdownMusyXVoices` call 3 returns from
`stopVoiceSlotSynced` (nenter=3 nexit=3) then
spins at `L_8009BD10` with `D_80154620==0x03`
through 1.63e10 iters. Calls 1–2 exit that
spin in one iter with `b0=0x00`. find-zero
and both `rs_free` never enter on call 3.
H-stop-synced / H-find-zero / H-tail-free
REFUTED; H-slot-spin SELECTED.

Writer of `0x03`: `stopVoiceSlotSynced`
`sb 0x8009B30C` (status==2 recv/stop/send).
Legitimate stop-in-progress. Spin waits for
slot-0 idle. Named zeroers:
`serviceVoicePoolFrame` `0x8009B7A8` /
`0x8009B7EC` (no jal in the generated tree;
likely a thread entry). Recipe keeps
`ROGUESQ_DRAIN_INLOOP_TICK=0`. Do not yield
the spin yet.

## Competing hypotheses

- **H-service-starved:** `serviceVoicePoolFrame`
  n grows before `[shut-enter] n=3`, then
  narmed=0 through the spin. Cooperative
  tight loop never schedules the worker.
- **H-service-skips:** narmed grows; both
  `sb $zero` sites narmed=0.
- **H-service-rewritten:** a zero-store
  narmed>0 but `[shut-spin] b0` stays `0x03`.
- **H-gate-off:** `lbu 0x800A5121` is 0 at
  shut-enter n=3 so the worker early-outs
  even if entered (`beq` at `0x8009B5D8`).

## Discriminating measurement (one instrument, one build, one 60s probe)

Always-on (not `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN`):
`[svc-pool] n= armed= a0= gate=` on
`serviceVoicePoolFrame` entry, first 8 and
every 1000. `armed` is a flag set at
`[shut-enter] n==3`. `gate` is
`MEM_BU(0, S32(0x800A5121u))`.

On the three `serviceVoicePoolFrame` stores
to `D_80154620`:
`[svc-store] site=zero-a8|zero-ec|sb3 n=
armed= val=` first 8 and every 1000.

Keep `[shut-enter]` / `[shut-spin]` /
`[shut-post]` / `[drain-exit]` /
`[drain-inloop-gate]` / `[fin-post]`.
`S32`. No store changed. Do not default
the in-loop tick off. Do not yield the
spin.

Positive control: `[drain-inloop-gate] en=0`;
`[drain-exit] v0=1`; `[shut-enter] n=3
b0=0x02`; `[shut-post] site=stop-synced
nenter=3 nexit=3`; `[shut-spin] n=3 b0=0x03`;
`[svc-pool]` n>0 before armed (status-2
voice was live, worker ran at least once).

Outcomes:
- svc-pool n>0 then narmed=0 → H-service-starved
- narmed grows; both zero sites narmed=0 →
  H-service-skips
- a zero-store narmed>0 and b0 stays 0x03 →
  H-service-rewritten
- shut-enter n=3 gate=0 → H-gate-off
  (worker would early-out)

If svc-pool n=0 entire run, the positive
control failed: find the actual caller /
thread of `serviceVoicePoolFrame` before
concluding starved.

SENTINEL is applied — incremental edit, do
not rerun full fixup.

## Exact patch sites

- Incremental wrap via
  `apply_s1997_svc_pool` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- Flag set in existing `[shut-enter]` when
  n==3; counters in `serviceVoicePoolFrame`
  (`funcs_26.c`).

## Exact test

```sh
mkdir -p scratch/agent/s1997_svc_pool
env ROGUESQ_DRAIN_INLOOP_TICK=0 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1997_svc_pool 60 2
```
