# NEXT work unit (s1949) — yield the menuControllerInput audio-slot spin

HYPOTHESIS-ID: hangar-after-title-1024

s1948 was maintenance (CURRENT-TRUTH 60,464 → 13,282 bytes).
The planned s1948 unit was not run; execute it now.

s1947 selected H-menu-input:
after title 1024 the only
live `jal 0x8008E57C` site
is `menuControllerInput`
`0x800B8050` (n=773e6,
10→`after1024=8`, all
`1024`/`0x00790400`).
`menuOverlayInit` /
`waitForAnyAudioSlot` /
the other seven are dead
after 1024. Same
`beq v0==0` tight spin as
`L_800C5930`; s1942
`ROGUESQ_SPIN_YIELD` does
not cover `L_800B8050`, so
idle-wait starves again
(SI send 1418 then recv1
n=1419 `blocked=1`).

## Competing hypotheses

- **H-same-starve** —
  extending the existing
  env-gated `yield_self_1ms`
  (every 100000 iters) to
  `menuControllerInput`
  `L_800B8050` unblocks
  recv1 (exit after a
  `[spin-yield]`) and later
  Starts reach
  `get_n64_input` after
  1024.
- **H-title-real** —
  yield unblocks SI/poll
  but title still ignores
  Start (Starts consumed,
  0 hangar origin).
- **H-yield-miss** —
  `[spin-yield]` never
  fires on this site
  (wrong loop / cadence
  never reached).
- **H-hangar-reachable** —
  `[phase] 512
  origin=0x006AB400` or
  `0x006AB800`.

## Work unit — one rebuild

Extend the existing
`ROGUESQ_SPIN_YIELD` block
(currently only on
`menuOverlayInit`
`L_800C5930`) to the
`L_800B8050` `beq v0==0`
loop in
`menuControllerInput`.
Same cadence (every
100000), same
`[spin-yield]` tag, add
`site=menuInput` so the
two yields are
distinguishable. Fixup,
not a hand-edit. Do **not**
default the env on. Do
**not** edit `lib/`. Do
**not** inject pad bits.

Keep `[slot-ret-caller]`,
`[si-thr]`, `[pad-host]`,
`[pad-sdl]`. Same Debug
binary otherwise. One
soak: `ROGUESQ_SPIN_YIELD=1`
+ s1943 eleven-Start from
boot + the same passive
instruments as s1947.

```
# after the rebuild:
zsh scratch/agent/soak_queue/s1949_menu_input_yield.sh
```

Write that script this
iteration before launching.
Crash / #6-dead / 640 stall
= enqueue another copy, do
not babysit.

Same-run positive control
(must fire **before** any
yield claim):

- tick-entry/jal/exit at
  least 2/2/2 with
  `took_swap=1` twice
- `slot-alloc` third row
  `0x8018D4A0 count=16`
- `[spin-yield] site=menuInit`
  n=1 (the existing s1942
  yield still fires)
- `[phase] 1024
  origin=0x00790400`
- `[slot-ret-caller]
  site=menuControllerInput`
  fires **after** that 1024

After that control:

- `[spin-yield] site=menuInput`
  n>=1, then recv1-exit
  after the post-1024
  enter, and `[si-thr]`
  `start-read` n>1418, and
  later `[pad-host]` Start
  after 1024
  → **H-same-starve
  SELECTED** (if still 0
  hangar, say so)
- yield + SI/poll resume
  but 0 further pad-host
  Start after the already-
  known n=3,4 and 0 hangar
  → **H-title-real
  SELECTED**
- `[slot-ret-caller]
  site=menuControllerInput`
  climbs and `[spin-yield]
  site=menuInput` never
  fires → **H-yield-miss
  SELECTED**
- `[phase] 512
  origin=0x006AB400` or
  `0x006AB800`
  → **H-hangar-reachable
  SELECTED**

Do **not** land spin-yield
as default. Ask (b) from
s1891 — still human-only.

Run from `build/` with the
ROM present. SIGKILL.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- s1942 yield off/on A/B (closed).
- s1942 from-phase-1024 Start/A as a hangar recipe.
- s1943–s1947 eleven-Start-from-boot as a hangar
  recipe without yielding `L_800B8050`.
- Force-zero slots.
- `requeue_vi=true` as the only arm.
- Ask (b) from s1891 — still human-only.
- Maintenance: CURRENT-TRUTH was compacted in s1948
  (60,464 → 13,282 bytes). Do not re-compact unless
  Step 0 triggers again.
