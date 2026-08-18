# NEXT work unit (s1932) — synth-exit vs after-slots after entry 2

HYPOTHESIS-ID: vi1024-guest-never-requests

s1931 selected H-viretrace-blocked:
`[vi-cb-loop]` n=2432 and
`[synth-entry]` n=2560 freeze
at the `.ovl.menu` DMA +
`menu-entry` siten=2;
`menu-spin` climbs; host
`update_screen` `#2880→#10816`.
H-cb-unhooked and
H-synth-early-return are
closed. Why the handler stops
after that last synth entry
is three hypotheses. The
existing s310 sites cannot
split them (no synth-exit,
no after-slots probe).

Do **not** re-run s1931's
existing-instrument recipe.
Do **not** re-run a
reachability-only `s790`.
No force-zero.

## Work unit — two new sites, one build, one 180s soak

Land both in `fixup_game_funcs.py`
(they die at the next regen
otherwise), then one cmake
Debug rebuild, then one
s1931-shaped 180s run.

1. `[synth-exit]` in
   `musyxSynthFrame`
   (`RecompiledFuncs/funcs_24.c`
   ~5649, the function's
   `return;`). Same
   `ROGUESQ_LOG_AUDIOTICK_TRACE`
   gate and `n<40||n%128==0`
   stride as `[synth-entry]`.
   Log `n=` from the same
   counter if possible, else a
   sibling `s_synthexit_n`.
2. `[vi-cb-after]` in
   `viRetraceHandlerThread`
   immediately before
   `goto L_800198E8`
   (`funcs_4.c` ~34870, after
   the 4-slot walk). Same env
   gate, `n<40||n%128==0`.

Copy
`scratch/agent/soak_queue/done/s1931_viretrace_during_spin_20260817-224233.sh`
(same env, including
`ROGUESQ_LOG_AUDIOTICK_TRACE=1`
and `ROGUESQ_LOG_VI_CALLERS=1`).
Do not enqueue until the new
tags exist in the live `.c`.
Crash-family (no entry 2) =
UNEVALUABLE — enqueue, do not
babysit.

Same-run positive control:
`site=tick-entry` / `tick-jal` /
`tick-exit` 2/2/2 with
`took_swap=1` twice;
`slot-alloc` ends at
`0x8018D4A0 count=16`;
`menu-entry` siten=2 AND
`menu-spin` climbs;
`[vi-cb-loop]` n last > 0
**and** `[synth-exit]` n last
> 0 **before** entry 2 (if
`synth-exit` is 0 the new
site missed); `[vi-cb-after]`
n last > 0 before entry 2
(same).

Then, after `menu-entry`
siten=2:

- last is `[synth-entry]`
  n=2560 (or later) with no
  matching `[synth-exit]` →
  H-synth-never-returned
- `[synth-exit]` fires for
  that n AND `[vi-cb-after]`
  does not increment past the
  last pre-spin value →
  H-stuck-later-slot
  (returned from synth, never
  finished the 4-slot walk)
- `[synth-exit]` AND
  `[vi-cb-after]` both fire
  for that iteration AND
  `[vi-cb-loop]` stays frozen
  while `update_screen`
  climbs → H-recv-starved
  (back at `osRecvMesg`
  `0x80114388`, no further
  VI message)

Join key is log order: first
`menu-entry` siten=2 vs last
`[synth-entry]` /
`[synth-exit]` /
`[vi-cb-after]` /
`[vi-cb-loop]`.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- VI-cb during the spin (s1931)
  — closed (H-viretrace-blocked).
- Mix-alive vs mix-dead vs
  song-loop after entry 2
  (s1930) — closed
  (H-mix-dead-during-spin).
- Cursor rarity / which jal
  re-attacks (s1929) — closed.
- Why playing-state never ends
  (s1928) — closed.
- Who writes slot+0 = 0x02 (s1927)
  — closed (H-keyon).
- Which slot index stays nonzero
  (s1926) — closed.
- Why `anyAudioSlotActive` returns
  0 (s1925) — closed (H-slot-stuck).
- Naming the two tick parents
  (s1923) — closed.
- AVF entry vs exit vs prologue
  after `#6` (s1921) — closed.
- Tick entry vs jal vs exit after
  AVF #2 (s1922) — closed.
- Entry 2 spin vs pre-spin vs
  early-return (s1924) — closed.
- Naming the `#10` osViSetMode
  site (s1919) — closed.
- The `0x80128EAD` / `$s0`
  swap-gate table (s1920) — closed.
- The s844-HEAD full code-content
  audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE`
  A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed.
- `vi1024-early-crash-not-stall`
  (s1918) — closed.
- A same-recipe `s790` run with no
  new measurement axis.
- Another gate-byte / slot-byte
  force-zero without `ORIGIN:`.
- Ask (b) from s1891 — still
  human-only.
