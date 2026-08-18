# NEXT work unit (s1939) — why recv1 never unblocks

HYPOTHESIS-ID: vi1024-guest-never-requests

s1938 selected H-recv1-starved
on the `#7/#8` / `menu-entry`
siten=2 staller
`s1938_loop_recv1_20260818-000228`.
After `#8` the walk completes
(after n=2409), then loop
n=2410 and `[vi-cb-recv1]`
enter n=2410 `mq=0x80114388`
with no matching exit. Stall
is `osRecvMesg(0x80114388)`
never returning.

## Work unit — VI register vs producer

One Debug rebuild, one `#7/#8`
soak. Do **not** re-probe
recv1 enter/exit or the walk.
Do **not** force-zero.

This is a `lib/` edit:
`lib/N64ModernRuntime/ultramodern/src/events.cpp`.
Must run `./submodule-patches/export.sh`
and commit the refreshed patches
in the same iteration.

1. Always-on `[vi-set-event]`
   in `osViSetEvent` (mq, msg,
   retrace_count). Gate on
   `ROGUESQ_LOG_AUDIOTICK_TRACE`
   (already armed).
2. Always-on `[vi-enq]` at the
   existing `enqueue_external_message_src`
   in `vi_thread_func` when
   `cur_state->mq != NULLPTR`
   (log mq, msg, retrace,
   `total_vis`). Same gate.
3. Leave `[vi-cb-loop]` /
   `[vi-cb-recv1]` /
   `[vi-cb-recv2]` /
   `[vi-cb-walk]` /
   `[vi-cb-after]` as they
   are (already always-on).

Same-run positive control
(must fire **before** `#8`):

- tick-entry/jal/exit 2/2/2
  with `took_swap=1` twice
- `slot-alloc` ends
  `0x8018D4A0 count=16`
- `[vi-set-event]` fires with
  `mq=0x80114388` at least once
- `[vi-enq]` fires to
  `mq=0x80114388` from n=0
- `[vi-cb-recv1]` enter/exit
  fire from n=0
  `mq=0x80114388`
- `[vi-cb-after]` fires from
  n=0 and a post-`#8` after
  n=N fires (s1938: N=2409)
- `menu-entry` siten=2 AND
  `menu-spin` climbs
- `#7` and `#8` fire

Then, after recv1-enter n=N+1:

- later `[vi-set-event]`
  mq≠`0x80114388` (or 0)
  and `[vi-enq]` to that
  other mq → **H-vi-unhooked**
- last `[vi-set-event]` still
  `mq=0x80114388` and zero
  `[vi-enq]` after enter →
  **H-vi-stopped**
- `[vi-enq]` to `0x80114388`
  after enter and no
  recv1-exit → **H-host-stuck**
- another thread's recv on
  `0x80114388` (or guest
  `osSendMesg` drain) →
  **H-stolen**

Crash / #6-dead (no entry 2)
= UNEVALUABLE — enqueue a
second copy of the same
recipe, do not babysit.

Join key is log order:
`#8` vs after n=N / loop
n=N+1 / recv1 enter n=N+1 /
vi-set-event / vi-enq /
recv1-exit / menu-entry
siten=2.

Build from `build/` with
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.
Run from `build/` with the
ROM present. SIGKILL.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- The s1938 recv1 three-way
  (closed: H-recv1-starved
  SELECTED; H-post-recv1-stuck
  / H-loop-missed REFUTED).
- The s1937 walk-interior
  three-way (closed:
  H-synth-in-walk /
  H-later-slot /
  H-after-missed).
- Re-probing recv2 or the
  4-slot walk after `#8`.
- The s1932 three-way on
  synth-exit / vi-cb-after
  at stride 128.
- Crash / #6-dead last-
  logged completion
  (s1932–s1934) as the
  entry-2 answer.
- A slot-byte / gate
  force-zero without
  `ORIGIN:`.
- Ask (b) from s1891 —
  still human-only.
