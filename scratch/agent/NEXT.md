# NEXT work unit (s1937) — walk interior after #8

HYPOTHESIS-ID: vi1024-guest-never-requests

s1936 selected **H-unlogged-walk-stuck**
on the `#7/#8` / `menu-entry`
siten=2 staller
`s1936_recv2_walk_20260817-233803`.
recv2 enter/exit n=2354 and
walk n=2354 fire immediately
after `#8` L405865. `[vi-cb-after]`
stays at last logged n=2304
(L404602, before `#8`). Zero
recv2/walk n=2355. 45
`musyxRenderVoiceSamples`
`slot-sb` then `.ovl.menu` then
`menu-entry` siten=2. H-recv2-starved
and H-post-recv2-stuck REFUTED.

## Work unit — always-on slot / synth / after

One Debug rebuild, one `#7/#8`
soak. Do **not** re-probe recv2.
Do **not** force-zero.

In `N64Recomp/fixup_game_funcs.py`
and the live generated files,
make these existing
`ROGUESQ_LOG_AUDIOTICK_TRACE`
sites **always-on** (drop the
`n<40 || n%128==0` /
`n<160 || n%512==0` stride),
same silent-window reason as
s1936 recv2/walk:

1. `[vi-cb-slot]` after the `lw`
   at `L_80019B68` (`funcs_4.c`)
2. `[synth-entry]` on
   `musyxSynthFrame` entry
3. `[synth-exit]` on
   `musyxSynthFrame` return
4. `[vi-cb-after]` before the
   jump back to `L_800198E8`

Leave `[vi-cb-recv2]` /
`[vi-cb-walk]` as they are
(already always-on).

Same-run positive control
(must fire **before** `#8`):

- tick-entry/jal/exit 2/2/2
  with `took_swap=1` twice
- `slot-alloc` ends
  `0x8018D4A0 count=16`
- `[vi-cb-slot]` fires from n=0
  with at least one
  `ptr=0x80003250` and one
  `ptr=0x8009123C`
- `[synth-entry]` and
  `[synth-exit]` both fire
  from n=0
- `[vi-cb-after]` fires from n=0
- `menu-entry` siten=2 AND
  `menu-spin` climbs
- `#7` and `#8` fire

Then, after `#8` / walk-start
on that staller:

- `[synth-entry]` increments
  past the last pre-`#8` n AND
  matching `[synth-exit]` does
  not → **H-synth-in-walk**
- `[synth-exit]` increments AND
  a later non-null `[vi-cb-slot]`
  `ptr` is entered AND
  `[vi-cb-after]` does not
  increment past the last
  pre-`#8` value →
  **H-later-slot**
- four `[vi-cb-slot]` lines
  for that walk (s1 0..3) AND
  still no `[vi-cb-after]` →
  **H-after-missed**

Crash / #6-dead (no entry 2)
= UNEVALUABLE — enqueue a
second copy of the same
recipe, do not babysit.

Join key is log order:
`#8` vs last recv2-exit /
vi-cb-walk / vi-cb-slot ptrs /
synth-entry / synth-exit /
vi-cb-after / menu-entry
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

- The s1936 recv2/walk
  three-way (closed:
  H-unlogged-walk-stuck).
- Treating the post-`#8`
  stall as recv2-starved or
  as stuck before
  `L_80019B68`.
- The s1932 three-way on
  synth-exit / vi-cb-after
  at stride 128 (s1935
  closed the logged split;
  s1936 moved the stall
  into the walk).
- Crash / #6-dead last-
  logged completion
  (s1932–s1934) as the
  entry-2 answer.
- A slot-byte / gate
  force-zero without
  `ORIGIN:`.
- Ask (b) from s1891 —
  still human-only.
