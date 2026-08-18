# NEXT work unit (s1929) — cursor compare + who re-attacks

HYPOTHESIS-ID: vi1024-guest-never-requests

s1928 selected H-fresh-attack-after-end:
`render-end` at `0x80090174` fired 9
times; `rekey` (`old!=0`) never fired;
after every end the next same-idx
render writeback is `old=0x01 new=0x02`.
H-sample-never-ends is REFUTED as a
universal (9/13646). H-rekey-forever
is REFUTED. Two leftover axes, batched
into one instrument: why the
`L_80090150` compare almost never
crosses, and which of the two
`jal 0x8009231C` sites issues the
post-end fresh attack.
Do **not** re-run a reachability-only
`s790`. Do **not** force-zero a slot
byte.

## Work unit — cursor vs attacker

Keep every existing `[avf-gate]` site.
Add, same tag, same `ROGUESQ_LOG_VI_CALLERS`
gate, in `N64Recomp/fixup_game_funcs.py`
plus the live `.c`:

- `site=cursor` on the
  `sltu` at `0x80090158` in
  `musyxRenderVoiceSamples`
  (`L_80090150`: `$v1 = 0x38($s1)`,
  `$v0 = $a0+$s4`, cross =
  `($a0+$s4) >= $v1`). Print
  `tickn`/`jaln`/`n`/`idx=` /
  `cur=` / `pos=` (`$a0`) /
  `step=` (`$s4`) / `cross=`.
  First 8 then every 1000000,
  plus every `cross=1`.
- `site=attack-jal` on both
  generated `jal 0x8009231C`
  sites, before the call:
  `tickAllAudioChannels`
  `0x8008CE7C` (`funcs_23.c`,
  idx=`$s6`) and
  `startStreamedSampleVoice`
  `0x80098194` (`funcs_26.c`,
  idx=`$s0`). Print
  `tickn`/`jaln`/`n`/`idx=` /
  `caller=` / `old=` (slot+0
  via `0x801496F8` + idx*136).
  First 32, every 1000, and
  every `old==0` after
  `render-end` has fired at
  least once (or simply every
  `old==0` — ~349 is cheap).

Do not add a second counter family.
Do not change any store.

One build, one s790-shaped 180s run
(copy `s1928_render_end.sh` to
`s1929_cursor_attack.sh`).

Same-run positive control:
`site=tick-entry` / `tick-jal` /
`tick-exit` still 2/2/2 with
`took_swap=1` twice; `slot-alloc`
still ends at `0x8018D4A0 count=16`;
`render-stage` still logs n2>0 n0=0;
`render-end` still fires (the s1928
skip reproduced) OR `attack-jal`
fires (new instrument live). Then:

Cursor rarity (the 15/16 bulk):

- `cur` sane and stable, `pos`
  never approaches it →
  H-cursor-stuck (stubbed
  fillSample / decoder is the
  lead)
- `cur` is 0 / non-KSEG /
  huge → H-end-wild
- `pos` advances then resets
  before `cross=1` →
  H-pos-rewinds
- `cursor` never logs →
  UNEVALUABLE

Post-end attacker (the 9):

- after `render-end` idx=X the
  next `attack-jal` for X is
  `caller=tick` → H-tick-retrigger
- next is `caller=stream` →
  H-stream-retrigger
- both appear after ends →
  H-mixed
- `render-end` fires but no
  subsequent `attack-jal` for
  that idx → H-no-join (widen)

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- Why playing-state never ends
  (s1928) — closed (H-fresh-attack-
  after-end; not never-end, not
  rekey-old!=0).
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
