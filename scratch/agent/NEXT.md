# NEXT work unit (s1928) — why slot+0 never returns to 0

HYPOTHESIS-ID: vi1024-guest-never-requests

s1927 selected H-keyon: after the third
`allocateSongChannelArray` (`new=0x8018D4A0
count=16` at tick 2) the sequence is alloc
init `0` → `musyxInitVoiceFromSample` `0` →
`musyxTriggerVoiceAttack` `0x01` →
`musyxRenderVoiceSamples` `0x01→0x02` at
`0x800909F4`. Two runs + the static
`addiu $v0, $zero, 0x2` agree. That write
is legitimate playing-state. `deactivateVoice`
has zero generated `jal 0x800924F0` sites.
`stopVoiceMarkRetrigger` does write `0`.
Do **not** re-run a reachability-only `s790`.
Do **not** force-zero a slot byte.

## Work unit — why playing-state never ends

Keep every existing `[avf-gate]` site. Add,
same tag, same `ROGUESQ_LOG_VI_CALLERS`
gate, in `N64Recomp/fixup_game_funcs.py`
plus the live `.c`:

- `site=render-end` on the
  `sb $zero, 0x28($sp)` at `0x80090174`
  (`musyxRenderVoiceSamples`). Print
  `tickn`/`jaln`/`n`/`idx=` (from `$s1`
  vs `0x801496F8`). No rate-limit
  (should be rare if it fires at all).
- `site=render-stage` on the
  `addiu $v0, $zero, 0x2` /
  `sb $v0, 0x28($sp)` at `0x80090080`.
  Lifetime counters `n2`/`n0` only;
  log first 8 then every 1000000.
- `site=rekey` on
  `musyxTriggerVoiceAttack` when
  `old!=0` (re-key of an already
  live slot). First 32 then every
  1000.

Do not add a second counter family.
Do not change any store.

One build, one s790-shaped 180s run
(copy `s1927_slot_sb.sh` to
`s1928_render_end.sh`).

Same-run positive control: `site=tick-entry`
/ `tick-jal` / `tick-exit` still 2/2/2 with
`took_swap=1` twice; `slot-alloc` still
ends at `0x8018D4A0 count=16`;
`slot-sb` `func=musyxRenderVoiceSamples`
`new=2` still fires (the s1927 skip
reproduced). Then:

- `render-end` never fires, `n2` climbs,
  `n0=0` → H-sample-never-ends (next
  unit asks why `0x38($s1)` / the
  sample cursor never crosses the
  end — stubbed audio / fillSample
  crash is the lead)
- `render-end` fires and writeback
  `new=0`, but `rekey` immediately
  restores `1` → H-rekey-forever
- `render-end` fires, writeback
  `new=0`, no rekey, but slot-byte
  still `0x02` → H-other-writer
  (widen)
- `slot-alloc` dest != `0x8018D4A0`
  or no render `new=2` → UNEVALUABLE
  for the playing-state claim

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- Who writes slot+0 = 0x02 (s1927) — closed
  (H-keyon: musyxRenderVoiceSamples; not
  alloc-dirty, not an unhooked store).
- Which slot index stays nonzero (s1926) — closed
  (H-all-idx 15/16 `0x02`; H-base-moved).
- Why `anyAudioSlotActive` returns 0 (s1925) — closed
  (H-slot-stuck; not stub, not gate-0).
- Naming the two tick parents (s1923) — closed.
- AVF entry vs exit vs prologue after `#6` (s1921) — closed.
- Tick entry vs jal vs exit after AVF #2 (s1922) — closed.
- Entry 2 spin vs pre-spin vs early-return (s1924) — closed.
- Naming the `#10` osViSetMode site (s1919) — closed.
- The `0x80128EAD` / `$s0` swap-gate table (s1920) — closed.
- The s844-HEAD full code-content audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed.
- `vi1024-early-crash-not-stall` (s1918) — closed.
- A same-recipe `s790` run with no new measurement axis.
- Another gate-byte / slot-byte force-zero without `ORIGIN:`.
- Ask (b) from s1891 — still human-only.
