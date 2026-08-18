# NEXT work unit (s1941) — consume C: why VI enqueues never unblock recv1

HYPOTHESIS-ID: vi1024-guest-never-requests

s1940 landed `[vi-deq]` /
`[vi-wait]`. Both same-
session soaks were
catalogued
`fillSampleStreamRange`
SIGBUS before `menu-entry`
siten=2 / `#7/#8`
(UNEVALUABLE). Instruments
passed same-run control
(deq n=0 `site=ok`; wait
n=1 exit delivered
`0x80114388`). Queued
`scratch/agent/soak_queue/s1940_vi_deq_wait_c.sh`.

## Work unit — consume C, no rebuild

Do **not** rebuild. The
Debug binary already has
the probes. If the loop
has already run C, read
`scratch/agent/SOAK-RESULTS.md`
and the cited `run.log`
and apply the three-way
below. If C has not run,
run it:

```
zsh scratch/agent/soak_queue/s1940_vi_deq_wait_c.sh
```

Do **not** re-probe
`osViSetEvent` / vi-enq
identity. Do **not** pump
`dequeue_external_messages`
from the menu spin.

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
  `mq=0x80114388`
- `[vi-wait]` enter n=0
  and an early exit
  delivering `0x80114388`
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
= UNEVALUABLE — enqueue
another copy of the same
recipe, do not babysit.

Join key is log order:
`#8` vs after n=N / loop
n=N+1 / recv1 enter n=N+1 /
vi-enq / vi-deq / vi-wait /
recv1-exit / menu-entry
siten=2.

Run from `build/` with the
ROM present. SIGKILL.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- The s1940 rebuild (probes
  are live).
- The s1939 four-way
  (closed: H-host-stuck
  SELECTED).
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
