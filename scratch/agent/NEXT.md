# NEXT work unit (s1942) — yield-from-spin A/B

HYPOTHESIS-ID: vi1024-guest-never-requests

s1941 selected H-never-dequeued:
after recv1-enter n=2343,
8038 `[vi-enq]` to
`0x80114388`, zero
`[vi-deq]`, zero
`[vi-wait]`. `osRecvMesg`
already passed dequeue and
blocked in `do_recv`; the
`anyAudioSlotActive` spin
is runnable so idle-wait
never runs.

## Work unit — one rebuild, two soaks

One Debug rebuild carrying
both:

1. Always-on `[vi-recv-path]`
   on `osRecvMesg` when
   `mq==0x80114388` (same
   `ROGUESQ_LOG_AUDIOTICK_TRACE`
   gate as `[vi-mq]`):
   `pre_vc`, `deq_any`,
   `deq_vi`, `post_vc`,
   `blocked=1` if
   `do_recv` entered the
   empty loop. Same-run
   control: n=0 must print
   and an early n must show
   `blocked=1` then a
   matching recv1-exit.
2. Env-gated
   `yield_self_1ms` every
   100000 `menu-spin`
   iterations at
   `L_800C5930` (fixup in
   `fixup_game_funcs.py`
   next to the s1924
   `menu-spin` patch). Gate:
   `ROGUESQ_SPIN_YIELD=1`.
   Log `[spin-yield] n=`
   first 4 then every 16.

ORIGIN: host VI retrace
(legitimate) enqueues to
`external_messages`.
`requeue_vi` defaults
false so deq n=50-54
`site=full` were dropped.
The spin is a runnable
game thread
(`beq v0==0`; v0 is
`sltiu(s1,1)` so 0 means
a live slot). Hardware
would preempt it with a
VI interrupt.

Then two soaks of the
**same** binary (rule 13),
same recipe as
`s1940_vi_deq_wait_c.sh`
plus the yield env on
one arm only. Run them
concurrently.

```
# arm off (control)
zsh scratch/agent/soak_queue/s1942_spin_yield_off.sh
# arm on
zsh scratch/agent/soak_queue/s1942_spin_yield_on.sh
```

Write both scripts this
iteration before the
rebuild. Crash / #6-dead
= enqueue another copy of
that arm, do not babysit.

Same-run positive control
(must fire **before** `#8`
on both arms):

- tick-entry/jal/exit 2/2/2
  with `took_swap=1` twice
- `slot-alloc` ends
  `0x8018D4A0 count=16`
- `[vi-set-event]` n=0
  `mq=0x80114388`
- `[vi-enq]` / `[vi-deq]`
  n=0 `site=ok` /
  `[vi-wait]` delivers
  `0x80114388`
- `[vi-recv-path]` n=0
- `[vi-cb-recv1]` enter/exit
  from n=0
- `menu-entry` siten=2 AND
  `menu-spin` climbs
- `#7` and `#8` fire

After recv1-enter n=N+1:

- off: zero `[vi-deq]` /
  zero `[vi-wait]` /
  `[vi-recv-path] blocked=1`
  → reproduces
  H-never-dequeued
  (control live)
- on + `[spin-yield]` fires
  + recv1-exit n=N+1 +
  later `[vi-deq]` site=ok
  + synth/cursor after
  entry 2 →
  **H-spin-starves-idle
  SELECTED**
- on + `[spin-yield]` fires
  + recv1 continues but
  `#9/#10` still miss and
  `menu-spin` still climbs
  → **H-slots-stay-live**
  (mix resumed; song still
  holds `0x02`)
- on + zero `[spin-yield]`
  or zero deq after enter
  → **H-yield-never-reached**

Do **not** force-zero
slots. Do **not** set
`requeue_vi=true` as the
only arm (that buys at
most one extra walk).
Do **not** rebuild the
s1940 probes; they stay.

If the 15-title window is
all sweep-titled, this is
still the VI thread, not
a sweep, so do not
REVISIT.

Run from `build/` with the
ROM present. SIGKILL.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- The s1941 consume (C
  already selected
  H-never-dequeued).
- The s1940 rebuild.
- The s1939 four-way
  (closed: H-host-stuck
  SELECTED).
- Re-probing recv2 or the
  4-slot walk after `#8`.
- A dequeue-pump from
  `menu-spin` that is not
  the env-gated yield
  above (ORIGIN is now
  named).
- Ask (b) from s1891 —
  still human-only.
