# NEXT work unit (s1943) — hangar/512 with spin-yield on

HYPOTHESIS-ID: hangar-512-with-spin-yield

s1942 selected H-spin-starves-idle.
Same-binary A/B: yield-off reproduced
H-never-dequeued; yield-on published
`[phase] 1024 origin=0x00790400` at
50.3s after `[spin-yield]` n=1
unblocked recv1-exit n=2308.
That 1024 is attract, not hangar.
s1942's from-phase-1024 Start/A
schedule stayed there 300s with
zero `0x006AB400`/`0x006AB800`.

## Work unit — no rebuild

Same Debug binary. One soak with
`ROGUESQ_SPIN_YIELD=1` and a
**hangar** input recipe (PROJECT-OVERVIEW
§35 / s707 / s1496 classified
frontend route — not the s1942
from-phase-1024 Start/A list).
Arm the same passive instruments
as `s1942_spin_yield_on.sh`.

```
zsh scratch/agent/soak_queue/s1943_hangar_spin_yield.sh
```

Write that script this iteration
before launching. Crash / #6-dead /
stall at 640 = enqueue another
copy, do not babysit. If the run
never leaves attract 1024, that
is a result (wrong recipe), not
a crash retry.

ORIGIN: host VI retrace is
legitimate; the spin-yield is
still env-gated experiment, not
product. Do not default-on
`ROGUESQ_SPIN_YIELD`. Do not
force-zero slots. Do not set
`requeue_vi=true` as the only
arm.

Same-run positive control (must
fire **before** hangar/512):

- tick-entry/jal/exit at least
  2/2/2 with `took_swap=1` twice
- `slot-alloc` ends
  `0x8018D4A0 count=16`
- `[spin-yield]` n=1
- `[phase] 1024 origin=0x00790400`
  (or another 1024 origin) —
  proves the s1942 lever still
  works on this recipe
- `[vi-recv-path]` n=0 `blocked=1`

After that control:

- `[phase] vi_width=512
  origin=0x006AB400` (or
  `0x006AB800`) →
  **H-hangar-reachable SELECTED**
  (item 3 unblocked; reopen M4
  Y=0x8000 on that run)
- 1024 control fires, 300s+ at
  attract `0x00790400`, zero
  hangar origin →
  **H-wrong-recipe SELECTED**
  (yield is not sufficient;
  need the classified hangar
  route, not more Start/A)
- 640/`0x00696100` stall, zero
  `[spin-yield]`, `#9/#10`
  miss → **H-yield-not-armed**
  (recipe dropped the env var)
- 640 stall *with* `[spin-yield]`
  and recv1-exit after entry 2
  but no `#9/#10` →
  **H-1024-not-only-spin**
  (s1942 lever insufficient on
  this path)

Do **not** rebuild s1942 probes.
Do **not** land spin-yield as
default. Do **not** treat attract
512 or 640 as hangar. Ask (b)
from s1891 — still human-only.

Run from `build/` with the ROM
present. SIGKILL.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- The s1942 yield off/on A/B
  (closed: H-spin-starves-idle
  SELECTED).
- s1942's from-phase-1024
  Start/A key list as a hangar
  recipe (300s at attract 1024).
- Force-zero slots.
- `requeue_vi=true` as the only
  arm.
- Ask (b) from s1891 — still
  human-only.
