# NEXT work unit (s1924) — why menu entry 2 never jals

HYPOTHESIS-ID: vi1024-guest-never-requests

s1923 selected H-caller-mixed: tick 1 =
`menuOverlayInit` `0x800C5A18`, tick 2 =
`initSceneForMission` `0x800A9C70`. `mainGameLoop`
entered once and never jaled. After `#8`,
`menu-entry` siten=2 fires and `menu-jal` does not.
Do **not** re-run a reachability-only `s790`. Do
**not** rename `func_800F7130` — item 1 still has a
live discriminator. Ask (b) is still human-only.

## Work unit — menuOverlayInit entry 2 vs the audio spin

`menuOverlayInit` `0x800C5A18` is after:

```
L_800C5928:  tickMusyXIfActive
L_800C5930:  anyAudioSlotActive
             beq $v0, $zero, L_800C5930   # spin
             ... setup ...
L_800C5A14:  jal 0x80001354
```

Keep every existing `[avf-gate]` site. Add, same
tag, same `ROGUESQ_LOG_VI_CALLERS` gate, in
`N64Recomp/fixup_game_funcs.py`:

- `site=menu-spin` at `L_800C5930` (before
  `anyAudioSlotActive`). Print `tickn`/`jaln` plus
  `siten` (rate-limit: first 32, then every 50, and
  also every 256 after that — this loop can be hot).
- `site=menu-exit` at the function epilogue
  (the `lw $ra` / return path).

Do not add a second counter family.

One build, one s790-shaped 180s run (copy
`s1923_tick_caller.sh` to `s1924_menu_spin.sh`).

Same-run positive control: `site=tick-entry` /
`tick-jal` / `tick-exit` still 2/2/2 with
`took_swap=1` twice, and `menu-entry` siten=1
must be followed by `menu-jal` siten=1 (entry 1
proves the new sites are on the path that can
reach the jal). Then read entry 2:

- `menu-entry` siten=2, `menu-spin` keeps
  climbing, no `menu-jal` siten=2, no `menu-exit`
  siten=2 → H-menu2-audio-spin (blocked in
  `anyAudioSlotActive`; audio-stub degenerate
  path is the 1024 miss)
- `menu-entry` siten=2, `menu-spin` frozen at
  the entry-1 count, no `menu-jal` / `menu-exit`
  on entry 2 → H-menu2-stuck-pre-spin (`zmemcpy`
  / `tickMusyXIfActive` never returned)
- `menu-entry` siten=2 then `menu-exit` siten=2
  with no `menu-jal` siten=2 → H-menu2-returned
  (CFG surprise; find the unseen return)
- `menu-spin` climbs on entry 1 only, then entry 2
  reaches `menu-jal` this run → UNEVALUABLE for
  the skip; the 180s `#7/#8` subtype did not
  reproduce the s1923 skip

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect` (TOML
`0xB44` already matches generated `rom_size`; no bump).
Four-step already complete in s1906–s1917.

## Do not repeat

- Naming the two tick parents (s1923) — closed.
- AVF entry vs exit vs prologue after `#6` (s1921) — closed.
- Tick entry vs jal vs exit after AVF #2 (s1922) — closed.
- Naming the `#10` osViSetMode site (s1919) — closed.
- The `0x80128EAD` / `$s0` swap-gate table (s1920) — closed.
- The s844-HEAD full code-content audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed.
- `vi1024-early-crash-not-stall` (s1918) — closed.
- A same-recipe `s790` run with no new measurement axis.
- Ask (b) from s1891 — still human-only.
