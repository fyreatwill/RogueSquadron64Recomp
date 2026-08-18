# NEXT work unit (s1936) — post-#8 recv2 vs walk

HYPOTHESIS-ID: vi1024-guest-never-requests

s1935 consumed the queued
`s1934_entry2_synth_exit` /
`_b` soaks. Arm B was the
`#7/#8` / `menu-entry`
siten=2 flavor. Three-way
result: **H-recv-starved
SELECTED.** H-synth-never-
returned REFUTED (`synth-exit`
n=2560). H-stuck-later-slot
REFUTED for the last logged
walk (`vi-cb-after` n=2432;
`vi-cb-slot` n=9728 = 2432×4).
`#8` (applyPending, only
caller `0x80019914`) fires
after after-2432, so the
loop-top `osRecvMesg(0x80114388)`
of the next iteration
unblocked. Stall is after
`#8`.

## Work unit — instrument the post-applyPending path

One Debug rebuild, one
`#7/#8` soak. Do **not**
re-hunt the s1932 three-way.
Do **not** force-zero.

Add three sites in
`N64Recomp/fixup_game_funcs.py`
(and the live `funcs_4.c`)
under the existing
`ROGUESQ_LOG_AUDIOTICK_TRACE`
gate, same
`n<40 || n%128==0` stride:

1. `[vi-cb-recv2]` `site=enter`
   immediately before
   `osRecvMesg_recomp` at
   `0x80019928` (queue
   `0x8013 + -0x72F0` =
   `0x80128D10`, `a2=1` BLOCK).
   Log `n=` and `mq=`.
2. `[vi-cb-recv2]` `site=exit`
   at `after_7` (first insn
   `0x80019930`).
3. `[vi-cb-walk]` at
   `L_80019B68` (start of the
   4-slot walk; existing
   `[vi-cb-slot]` is inside
   the walk after the `lw`).

Same-run positive control
(must fire **before** `#8`):

- tick-entry/jal/exit 2/2/2
  with `took_swap=1` twice
- `slot-alloc` ends
  `0x8018D4A0 count=16`
- `[vi-cb-recv2] site=enter`
  and `site=exit` both fire
  from n=0 (if enter is 0
  the site missed)
- `[vi-cb-walk]` n last > 0
  before `#8` (if 0 the
  site missed)
- `menu-entry` siten=2 AND
  `menu-spin` climbs
- `#7` and `#8` fire

Then, after `#8` on that
staller:

- recv2-enter increments
  past the last pre-`#8`
  logged n AND recv2-exit
  does not →
  **H-recv2-starved**
- recv2-exit increments
  AND `[vi-cb-walk]` does
  not increment past the
  last pre-`#8` value →
  **H-post-recv2-stuck**
- `[vi-cb-walk]` increments
  AND `[vi-cb-after]` stays
  at 2432 →
  **H-unlogged-walk-stuck**

Crash / #6-dead (no entry 2)
= UNEVALUABLE — enqueue a
second copy of the same
recipe, do not babysit, do
not re-read as the answer.

Join key is log order:
`#8` vs last recv2-enter /
recv2-exit / vi-cb-walk /
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

- The s1932 three-way on
  synth-exit / vi-cb-after
  (s1935 closed it:
  H-recv-starved).
- Treating H-recv-starved
  as the loop-top
  `osRecvMesg(0x80114388)`
  — `#8` refuted that.
- Another identical
  entry-2 flavor hunt with
  no new site.
- Crash / #6-dead last-
  logged completion
  (s1932–s1934) as the
  entry-2 answer.
- VI-cb during the spin
  (s1931) — closed
  (H-viretrace-blocked).
- Mix-alive vs mix-dead
  after entry 2 (s1930) —
  closed.
- A same-recipe `s790`
  with no new axis.
- A slot-byte / gate
  force-zero without
  `ORIGIN:`.
- Ask (b) from s1891 —
  still human-only.
