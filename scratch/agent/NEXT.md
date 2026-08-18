# NEXT work unit (s1940) — why VI enqueues never unblock recv1

HYPOTHESIS-ID: vi1024-guest-never-requests

s1939 selected H-host-stuck
on the `#7/#8` / `menu-entry`
siten=2 staller
`s1939_vi_register_producer_b_20260818-001837`.
After `#8` the walk completes
(after n=2350), then loop
n=2351 and `[vi-cb-recv1]`
enter n=2351 `mq=0x80114388`
with no matching exit. Host
`[vi-enq]` keeps targeting
`0x80114388` (7987 after
enter). The guest queue never
unblocks.

## Work unit — dequeue vs drop vs wake

One Debug rebuild, one `#7/#8`
soak. Do **not** re-probe
`osViSetEvent` / vi-enq
identity. Do **not** pump
`dequeue_external_messages`
from the menu spin (that is a
mitigation).

This is a `lib/` edit:
`lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp`.
Must run `./submodule-patches/export.sh`
and commit the refreshed patches
in the same iteration.

1. Always-on `[vi-deq]` in
   `dequeue_external_messages`
   when `to_send.mq==0x80114388`
   (site=`ok` if `do_send`
   returns true, `full` if
   false; log n, validCount,
   msgCount). Gate on
   `ROGUESQ_LOG_AUDIOTICK_TRACE`.
2. Always-on `[vi-wait]`
   enter/exit on
   `wait_for_external_message`
   (and the timed variant).
   Same gate.
3. Leave `[vi-set-event]` /
   `[vi-enq]` / `[vi-mq]` /
   `[vi-cb-recv1]` as they
   are.

Same-run positive control
(must fire **before** `#8`):

- tick-entry/jal/exit 2/2/2
  with `took_swap=1` twice
- `slot-alloc` ends
  `0x8018D4A0 count=16`
- `[vi-set-event]` n=0
  `mq=0x80114388`
- `[vi-enq]` to
  `0x80114388` from n=0
- `[vi-deq]` site=ok fires
  from n=0 for
  `mq=0x80114388` (early
  recv1-exit proves delivery
  works)
- `[vi-cb-recv1]` enter/exit
  fire from n=0
- `menu-entry` siten=2 AND
  `menu-spin` climbs
- `#7` and `#8` fire

Then, after recv1-enter n=N+1
with continuing `[vi-enq]`
to `0x80114388`:

- zero `[vi-deq]` after enter
  (and zero `[vi-wait]`) →
  **H-never-dequeued**
- `[vi-deq]` site=full after
  enter, no site=ok →
  **H-deq-dropped**
- `[vi-deq]` site=ok after
  enter and no recv1-exit →
  **H-deq-not-woken**
- `[vi-wait]` enter after
  enter (no matching deq ok)
  → still H-never-dequeued,
  but the idle-wait path
  ran and did not deliver

Crash / #6-dead (no entry 2)
= UNEVALUABLE — enqueue a
second copy of the same
recipe, do not babysit.

Join key is log order:
`#8` vs after n=N / loop
n=N+1 / recv1 enter n=N+1 /
vi-enq / vi-deq / vi-wait /
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

- The s1939 four-way
  (closed: H-host-stuck
  SELECTED; H-vi-unhooked /
  H-vi-stopped / H-stolen
  REFUTED).
- The s1938 recv1 three-way.
- The s1937 walk-interior
  three-way.
- Re-probing recv2 or the
  4-slot walk after `#8`.
- A dequeue-pump / yield
  from `menu-spin` without
  `ORIGIN:`.
- Ask (b) from s1891 —
  still human-only.
