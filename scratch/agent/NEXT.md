# NEXT work unit (s1947) — which anyAudioSlotActive caller spins after title 1024

HYPOTHESIS-ID: hangar-after-title-1024

s1946 selected H-si-loop-recv:
`siServiceThread` finishes
send n=1419 then the next
`L_80002EA0` Recv on mq
`0x8010FF50` never returns.
Unique producer is
`wakeSerialThreadOnSi`
`0x80003250`. Last fire of
that VI slot is the walk
that produced SI 1419;
recv1 n=1420 then starves
(9369 `[vi-enq]`, 0 deq).
`menu-spin` / `[spin-yield]`
after 1024 = 0. `[slot-ret]`
still climbs to n=821e6
`v0=0 path=walk`.

## Competing hypotheses

- **H-wait-slot** —
  `waitForAnyAudioSlot`
  `0x800668C0` is the
  post-1024 spinner.
- **H-menu-input** —
  `menuControllerInput`
  `0x800B8050` (title/attract
  presenter) is the spinner.
- **H-other-jal** —
  one of the other seven
  live `jal 0x8008E57C`
  sites
  (`initCinematicSceneAssets`
  `0x800AE75C`,
  `drainAudioAndFinalizeSpeechBuffer`
  `0x800B24D4`,
  `runMenuRandomBackdropScreen`
  `0x800BFF60`,
  `runMenuShipSelectScreen`
  `0x800C1750`,
  `runMenuModelViewerScreen`
  `0x800C2DB0`,
  `menuSubtype02Handler`
  `0x800C3F64`,
  `runModelViewerLoop`
  `0x800CA580`).
- **H-menu-init-still** —
  `menuOverlayInit`
  `0x800C5930` still issues
  the post-1024 `slot-ret`
  (s1946 `menu-spin`=0
  would be a miss).

## Work unit — one rebuild

Land always-on
`[slot-ret-caller]` on every
`jal 0x8008E57C` site
(fixup, not a hand-edit).
Fields: `site=<fn-short>`,
`n`, `vi_width`, `origin`.
Rate-limit first 16 then
every 32, plus every fire
once `vi_width>=1024` is
too hot (821e6 calls) —
instead: first 16, every
1e6, and every fire in a
32-deep ring dumped once
`slot-ret` n crosses 1e6
*after* the 1024 phase
(or just first 16 / every
1e6 / first 8 after 1024).
Keep existing `[slot-ret]`
and `[si-thr]`. Do **not**
edit `lib/`. Do **not**
inject pad bits. Do **not**
default-on
`ROGUESQ_SPIN_YIELD`.

Same Debug binary
otherwise. One soak:
`ROGUESQ_SPIN_YIELD=1` +
s1943 eleven-Start from
boot + the same passive
instruments as s1946.

```
# after the rebuild:
zsh scratch/agent/soak_queue/s1947_slot_ret_caller.sh
```

Write that script this
iteration before launching.
Crash / #6-dead / 640 stall
= enqueue another copy, do
not babysit.

Same-run positive control
(must fire **before** any
caller claim):

- tick-entry/jal/exit at
  least 2/2/2 with
  `took_swap=1` twice
- `slot-alloc` third row
  `0x8018D4A0 count=16`
- `[spin-yield]` n=1
- `[phase] 1024
  origin=0x00790400`
- `[si-thr] site=start-read`
  and `site=get-read` fire
  **before** that 1024
- `[slot-ret-caller]
  site=menuOverlayInit`
  fires **before** that
  1024 (the known s1924
  spinner)

After that control, look at
`[slot-ret-caller]` rows
*after* the 1024 phase
(and after SI send last):

- only `waitForAnyAudioSlot`
  climbs → **H-wait-slot
  SELECTED**
- only `menuControllerInput`
  climbs → **H-menu-input
  SELECTED**
- exactly one of the other
  seven climbs →
  **H-other-jal SELECTED**
  (name it)
- `menuOverlayInit` still
  climbs →
  **H-menu-init-still
  SELECTED**
- `[phase] 512
  origin=0x006AB400` or
  `0x006AB800` →
  **H-hangar-reachable
  SELECTED**

Do **not** repeat
s1943–s1946 eleven-Start
as a hangar recipe without
this caller split. Do
**not** land spin-yield as
default. Ask (b) from
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
- s1943–s1946 eleven-Start-from-boot as a hangar
  recipe without the post-1024 slot-ret caller split.
- Force-zero slots.
- `requeue_vi=true` as the only arm.
- Ask (b) from s1891 — still human-only.
