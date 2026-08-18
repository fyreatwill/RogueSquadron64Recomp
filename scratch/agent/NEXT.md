# NEXT work unit (s1931) — VI-retrace mix producer after entry 2

HYPOTHESIS-ID: vi1024-guest-never-requests

s1930 selected H-mix-dead-during-spin:
`cursor` / `render-end` /
`attack-jal` all freeze at the
`.ovl.menu` DMA + `menu-entry`
siten=2; `menu-spin` climbs.
The 15/16 `0x02` freeze is a
dead mixer. Why the producer
dies is now three hypotheses
on an already-landed
instrument (`[vi-cb-loop]` /
`[vi-cb-slot]`, s310).

Do **not** re-run a
reachability-only `s790`. Do
**not** force-zero a slot byte.
No rebuild: the s310 sites are
already in the live `.c`.

## Work unit — VI-cb during the spin

Same `[avf-gate]` sites. Same
`ROGUESQ_LOG_VI_CALLERS` gate.
Add `ROGUESQ_LOG_AUDIOTICK_TRACE=1`
so `[vi-cb-loop]` / `[vi-cb-slot]`
fire. One s790-shaped 180s run
(copy `s1930_mix_during_spin.sh`).
A queued copy is
`scratch/agent/soak_queue/s1931_viretrace_during_spin.sh`
— consume `SOAK-RESULTS.md` first;
if that line is already a 180s
`#7/#8` staller with `vi-cb-loop`
rows, do not re-run.

Same-run positive control:
`site=tick-entry` / `tick-jal` /
`tick-exit` 2/2/2 with
`took_swap=1` twice; `slot-alloc`
ends at `0x8018D4A0 count=16`;
`site=cursor` n last > 0;
`menu-entry` siten=2 AND
`menu-spin` climbs; `[vi-cb-loop]`
n last > 0 **before** entry 2
(the mark-everything control —
if this is 0 the env was not
armed). Crash-family (no entry
2) = UNEVALUABLE — enqueue, do
not babysit.

Then, after `menu-entry` siten=2:

- `vi-cb-loop` n frozen while
  `update_screen` climbs →
  H-viretrace-blocked
- `vi-cb-loop` n climbing AND
  `vi-cb-slot` `ptr=` no longer
  includes `0x8009123C`
  (`musyxSynthFrame`) →
  H-cb-unhooked
- `vi-cb-loop` n climbing AND
  synth still slotted AND
  `cursor` n frozen →
  H-synth-early-return

Join key is log order: first
`menu-entry` siten=2 vs last
`[vi-cb-loop]` / `[vi-cb-slot]`
and last `site=cursor`.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

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
