# NEXT work unit (s1925) — why anyAudioSlotActive returns 0

HYPOTHESIS-ID: vi1024-guest-never-requests

s1924 selected H-menu2-audio-spin: `menuOverlayInit`
entry 2 sits in `L_800C5930` (`anyAudioSlotActive`
then `beq $v0, $zero, L_800C5930`). `menu-spin`
siten reached 907285100 with tickn/jaln frozen at
2; no `menu-jal` / `menu-exit` siten=2. Do **not**
re-run a reachability-only `s790`. Do **not** add
another gate-byte force-zero (that is mitigation;
needs `ORIGIN:`). Ask (b) is still human-only.

## Work unit — which `anyAudioSlotActive` path returns 0

`anyAudioSlotActive` `0x8008E57C`:

```
lbu  $v0, 0x800A0F50          # audio gate
beq  $v0, $zero, L_8008E5F4   # s1 stays 0
jal  audioStubReturnZero
bnel $v0, $zero, L_8008E5EC   # s1 = 1
# else walk isAudioSlotActive, OR into s1
L_8008E5F4:
andi  $v0, $s1, 0xFF
sltiu $v0, $v0, 1             # return (s1 == 0)
```

The spin continues when that return is 0, i.e.
s1!=0, which CFG requires gate != 0 plus a
stub/slot reporting active. Keep every existing
`[avf-gate]` site. Add, same tag, same
`ROGUESQ_LOG_VI_CALLERS` gate, in
`N64Recomp/fixup_game_funcs.py`:

- `site=slot-ret` at `L_8008E5F4` (after the
  `sltiu`, before `lw $ra`). Print `tickn`/`jaln`
  plus `gate=` (`MEM_BU` of `0x800A0F50`),
  `s1=` (the pre-sltiu byte), `v0=` (the return),
  `path=` (`gate0` if the early-out was taken,
  `stub` if `audioStubReturnZero` set s1,
  `walk` otherwise).
- Rate-limit HARD: first 8, then every 1000000.
  s1924's every-50 on this loop wrote a 1.2 GB log.

Do not add a second counter family. Do not change
any store to `0x800A0F50`.

One build, one s790-shaped 180s run (copy
`s1924_menu_spin.sh` to `s1925_slot_ret.sh`).

Same-run positive control: `site=tick-entry` /
`tick-jal` / `tick-exit` still 2/2/2 with
`took_swap=1` twice; entry 1 must log
`slot-ret` with `v0=1` (that is why siten=1
exited the spin); `menu-entry` siten=2 then
`menu-spin` must climb (the s1924 skip
reproduced). Then read entry 2's `slot-ret`:

- `gate=0` and `v0=0` → H-cfg-contradiction
  (s1/v0 vs the sltiu/early-out read; re-read
  the generated body)
- `gate!=0`, `path=stub`, `v0=0` → H-stub-one
  (`audioStubReturnZero` returns 1; the spin is
  wait-for-idle on a stub that never goes quiet)
- `gate!=0`, `path=walk`, `v0=0` → H-slot-stuck
  (a real `isAudioSlotActive` byte stays
  nonzero; next unit names the slot)
- `menu-spin` does not climb, or `slot-ret`
  `v0=1` on entry 2 → UNEVALUABLE for the
  skip; the 180s `#7/#8` spin did not
  reproduce

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

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
- Another gate-byte force-zero without `ORIGIN:`.
- Ask (b) from s1891 — still human-only.
