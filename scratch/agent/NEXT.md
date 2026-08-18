# NEXT work unit (s1938) — loop-top / recv1 after completed walk

HYPOTHESIS-ID: vi1024-guest-never-requests

s1937 refuted H-synth-in-walk /
H-later-slot / H-after-missed
on the `#7/#8` / `menu-entry`
siten=2 staller
`s1937_walk_interior_20260817-234929`.
After `#8` the walk completes:
recv2/walk n=2310, slot 9240
`ptr=0x80003250`, slot 9241
`ptr=0x8009123C`, synth-entry=
exit n=2425, slot 9242/9243
null, `[vi-cb-after]` n=2310,
then `.ovl.menu` + `menu-entry`
siten=2. Stall is the next
`L_800198E8` / recv1 iteration.

## Work unit — always-on loop + recv1

One Debug rebuild, one `#7/#8`
soak. Do **not** re-probe the
walk interior. Do **not**
force-zero.

In `N64Recomp/fixup_game_funcs.py`
and the live generated files:

1. Make `[vi-cb-loop]` at
   `L_800198E8` (`funcs_4.c`)
   **always-on** (drop the
   `n<40 || n%128==0` stride).
2. Add always-on `[vi-cb-recv1]`
   enter immediately before
   `osRecvMesg_recomp` at
   `0x800198F4` (mq already in
   `$a0` = `0x80114388`) and
   exit at `after_3`.

Leave `[vi-cb-slot]` /
`[synth-entry]` / `[synth-exit]` /
`[vi-cb-after]` / `[vi-cb-recv2]`
/ `[vi-cb-walk]` as they are
(already always-on).

Same-run positive control
(must fire **before** `#8`):

- tick-entry/jal/exit 2/2/2
  with `took_swap=1` twice
- `slot-alloc` ends
  `0x8018D4A0 count=16`
- `[vi-cb-loop]` fires from n=0
- `[vi-cb-recv1]` enter/exit
  fire from n=0 with
  `mq=0x80114388`
- `[vi-cb-after]` fires from n=0
  and a post-`#8` after n=N
  fires (s1937: N=2310)
- `menu-entry` siten=2 AND
  `menu-spin` climbs
- `#7` and `#8` fire

Then, after that post-`#8`
`[vi-cb-after]` n=N:

- `[vi-cb-loop]` n=N+1 AND
  `[vi-cb-recv1]` enter n=N+1
  AND no matching recv1-exit →
  **H-recv1-starved**
- recv1-exit n=N+1 AND no
  `[vi-cb-recv2]` n=N+1 →
  **H-post-recv1-stuck**
- no `[vi-cb-loop]` n=N+1 →
  **H-loop-missed**

Crash / #6-dead (no entry 2)
= UNEVALUABLE — enqueue a
second copy of the same
recipe, do not babysit.

Join key is log order:
`#8` vs last after n=N /
vi-cb-loop n=N+1 / recv1
enter/exit / recv2 / menu-entry
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
