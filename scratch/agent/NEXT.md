# NEXT work unit (s1927) — who writes slot+0 = 0x02

HYPOTHESIS-ID: vi1024-guest-never-requests

s1926 selected H-all-idx + H-base-moved:
after tick 2 the voice table at
`*0x801496F8` is `0x8018D4A0` ch=16, and
15/16 `isAudioSlotActive` bytes stay
`0x02`. Idle was `0x80169460` ch=20 all
zero. Unique `sw` to `0x801496F8` is
`allocateSongChannelArray` `0x8008F0EC`.
`musyxTriggerVoiceAttack` writes `1`, not
`0x02`. Do **not** re-run a reachability-only
`s790`. Do **not** force-zero a slot byte
(that is mitigation; needs `ORIGIN:`).
Ask (b) is still human-only.

## Work unit — name the 0x02 writer

Keep every existing `[avf-gate]` site. Add,
same tag, same `ROGUESQ_LOG_VI_CALLERS`
gate, in `N64Recomp/fixup_game_funcs.py`
plus the live `.c`:

- `site=slot-alloc` in
  `allocateSongChannelArray` after the
  `sw $v0, -0x6908($at)` (`0x8008F0EC`).
  Print `tickn`/`jaln` plus `old=` (value
  before the store if you snapshot it),
  `new=` (`$v0`), `count=` (`$s0` / the
  halfword at `0x801496FF`/`-0x6900`).
  No rate-limit needed (boot-rare).
- `site=slot-sb` on every `sb` to slot+0
  that uses the `0x801496F8` table
  (start with `musyxTriggerVoiceAttack`
  `0x8009235C` `sb $v0, 0x0($v1)` and
  grep `MEM_B(0X0` after a `-0x6908`
  load in `funcs_24.c` / `funcs_23.c`).
  Print `tickn`/`jaln`/`func=`/`idx=`/
  `old=`/`new=`. Rate-limit: first 32
  then every 1000, and every `new==2`.

Do not add a second counter family. Do not
change any store.

One build, one s790-shaped 180s run (copy
`s1926_slot_byte.sh` to `s1927_slot_sb.sh`).

Same-run positive control: `site=tick-entry`
/ `tick-jal` / `tick-exit` still 2/2/2 with
`took_swap=1` twice; slot-ret n=1..3 stay
`v0=1 path=walk`; `menu-entry` siten=2 then
`menu-spin` climbs (the s1926 skip
reproduced). `site=slot-alloc` must fire
(the base actually moved). Then:

- alloc `new=0x8018D4A0 count=16` and no
  `slot-sb new=2` from alloc itself, plus
  later `slot-sb` with `new=2` from a
  named func → H-keyon (next unit asks
  why those voices never key off)
- alloc itself writes `new=2` into the
  fresh table → H-alloc-dirty (init left
  them active)
- `slot-sb new=2` never fires, but
  `slot-byte` still sees `0x02` → H-other
  (writer is a store we did not hook;
  widen the grep)
- `slot-alloc` never fires, or dest !=
  `0x8018D4A0` → UNEVALUABLE for the
  retarget; check a second `sw`
- `menu-spin` does not climb →
  UNEVALUABLE for the skip

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

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
