# NEXT work unit (s1944) — Start consumption after title 1024

HYPOTHESIS-ID: hangar-after-title-1024

s1943 selected H-wrong-recipe.
Yield + classified eleven-Start
from boot reached title-like
`[phase] 1024 origin=0x00790400`
at 14.2s (Rice-driven 17.3s)
then stayed through 180s /
`#10816`. Early Starts skipped
the cinematic; later Starts did
not leave that 1024. No guest
pad log existed, so host
delivery vs title-ignore is
still open.

## Work unit — one rebuild

Land `[pad-host]` in
`src/main/main.cpp` keyboard
fallback (`SDL_SCANCODE_RETURN`
→ `N64_START_BUTTON`, `Z` → A)
when those bits are newly set
on the outgoing pad word.
Rate-limit first 16 then every
32. Include `vi_width` from
the last committed phase (or
`rs64` VI width already used
by hangar gate). Do **not**
edit `lib/` (osContGetReadData
already calls this callback).

Same Debug binary otherwise.
One soak: `ROGUESQ_SPIN_YIELD=1`
+ s1943 eleven-Start from boot
+ the same passive instruments
as `s1943_hangar_spin_yield`.

```
# after the rebuild:
zsh scratch/agent/soak_queue/s1944_pad_host_after_title.sh
```

Write that script this iteration
before launching. Crash / #6-dead
/ 640 stall = enqueue another
copy, do not babysit.

ORIGIN: Start presses after
title 1024 are the question;
do not default-on
`ROGUESQ_SPIN_YIELD`. Do not
force-zero slots. Do not treat
title `0x00790400` as hangar.

Same-run positive control
(must fire **before** any
post-1024 pad claim):

- tick-entry/jal/exit at least
  2/2/2 with `took_swap=1` twice
- `slot-alloc` third row
  `0x8018D4A0 count=16`
- `[spin-yield]` n=1
- `[phase] 1024 origin=0x00790400`
- at least one `[pad-host]`
  Start **before** that 1024
  (early Starts skipped the
  cinematic — this is the
  "mark everything" control)

After that control, count
`[pad-host]` Start (and A)
**after** the 1024 `[phase]`:

- after=0 → **H-late-keys-dropped
  SELECTED** (winctl/focus;
  later Starts never reach SDL)
- after>0 and zero hangar origin
  / zero hangar handler →
  **H-title-ignores-start
  SELECTED** (pad word has
  Start; this 1024 is not the
  Rice title-to-hangar screen)
- after>0 and
  `[phase] 512 origin=0x006AB400`
  or `0x006AB800` →
  **H-hangar-reachable SELECTED**
  (reopen M4 Y=0x8000 on that
  log; s1943 was a short window
  or a missed edge)

Do **not** repeat s1942
from-phase-1024 Start/A or
s1943 eleven-Start as a
"maybe hangar this time"
recipe without this pad split.
Do **not** land spin-yield as
default. Ask (b) from s1891 —
still human-only.

Run from `build/` with the ROM
present. SIGKILL.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- s1942 yield off/on A/B (closed).
- s1942 from-phase-1024 Start/A
  as a hangar recipe.
- s1943 eleven-Start-from-boot
  as a hangar recipe without a
  pad-consumption split.
- Force-zero slots.
- `requeue_vi=true` as the only
  arm.
- Ask (b) from s1891 — still
  human-only.
