# NEXT work unit (s1930) — mix-alive during menu-entry 2

HYPOTHESIS-ID: vi1024-guest-never-requests

s1929 selected H-not-yet-ended +
H-tick-retrigger in the 27s mix
window: `L_80090150` `cur` is a
sane sample-end, `pos` advances,
8/8 `cross=1` match `render-end`,
and every `jal 0x8009231C` is
`tickAllAudioChannels` (0 stream).
The 180s 15/16 `0x02` freeze is
now three hypotheses on one
already-landed instrument.

Do **not** re-run a reachability-only
`s790`. Do **not** force-zero a slot
byte. Rebuild first if this binary
is older than the s1929 MEM_BU
fix (only needed for `old=`; the
mix-alive table does not use it).

## Work unit — mix during the spin

Same `[avf-gate]` sites. Same
`ROGUESQ_LOG_VI_CALLERS` gate.
One s790-shaped 180s run
(copy `s1929_cursor_attack.sh`).
A queued copy is
`scratch/agent/soak_queue/s1930_mix_during_spin.sh`
— consume `SOAK-RESULTS.md` first;
if that line is already a 180s
`#7/#8` staller, do not re-run.

Same-run positive control:
`site=tick-entry` / `tick-jal` /
`tick-exit` 2/2/2 with
`took_swap=1` twice; `slot-alloc`
ends at `0x8018D4A0 count=16`;
`site=cursor` logs (n last > 0);
`menu-entry` siten=2 AND
`menu-spin` climbs. Crash-family
(no entry 2) = UNEVALUABLE for
this axis — enqueue, do not
babysit.

Then, after `menu-entry` siten=2:

- `cursor` n keeps climbing AND
  new `render-end` / `attack-jal`
  fire → H-song-loop-forever
- `cursor` n keeps climbing AND
  `cross=1` / `render-end` freeze
  → H-pos-freeze-during-spin
- `cursor` n frozen while
  `menu-spin` siten climbs →
  H-mix-dead-during-spin

Join key is wall-clock / log
order: first `menu-entry` siten=2
line vs last `site=cursor` n.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- Cursor rarity / which jal
  re-attacks (s1929) — closed
  (H-not-yet-ended +
  H-tick-retrigger).
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
