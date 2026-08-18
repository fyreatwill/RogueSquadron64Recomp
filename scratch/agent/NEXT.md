# NEXT work unit (s1926) — which isAudioSlotActive index stays nonzero

HYPOTHESIS-ID: vi1024-guest-never-requests

s1925 selected H-slot-stuck: `anyAudioSlotActive`
entry-2 return is `path=walk`, `gate=0x65`,
`s1=0x01`, `v0=0` (n=4 through n=961000000).
`audioStubReturnZero` never set s1. The same
gate was already `0x65` on the idle positive
control (n=1..3, `s1=0x00`, `v0=1`). Do **not**
re-run a reachability-only `s790`. Do **not**
force-zero the gate or a slot byte (that is
mitigation; needs `ORIGIN:`). Ask (b) is still
human-only.

## Work unit — name the stuck slot

`isAudioSlotActive` `0x800920FC` (`funcs_24.c`):

```
lw   $v0, 0x801496F8          # slot table base
addu $v1, $v0, $a0*136
lbu  $v0, 0x0($v1)
sltu $v0, $zero, $v0          # return (byte != 0)
```

Walked from `anyAudioSlotActive` as
`i=0..MEM_BU(0x80141AD0)-1`, OR into s1.

Keep every existing `[avf-gate]` site. Add,
same tag, same `ROGUESQ_LOG_VI_CALLERS` gate,
in `N64Recomp/fixup_game_funcs.py` plus live
`funcs_24.c`:

- `site=slot-byte` after the `lbu` (before
  `sltu` / the s166 guard return). Print
  `tickn`/`jaln` plus `idx=` (`$a0`),
  `byte=` (the loaded byte), `base=`
  (`0x801496F8`), `ch=` (`MEM_BU` of
  `0x80141AD0`).
- Rate-limit HARD: first 8, then every
  1000000, and also the first 8
  `byte!=0` hits (so an idle walk of
  many zero slots cannot hide the first
  stuck index).
- Same build: tighten `site=menu-spin`
  to first 8 then every 1000000 (s1924
  every-50 wrote another 1.3 GB log).

Do not add a second counter family. Do not
change any store to `0x800A0F50` or to a
slot byte.

One build, one s790-shaped 180s run (copy
`s1925_slot_ret.sh` to `s1926_slot_byte.sh`).

Same-run positive control: `site=tick-entry`
/ `tick-jal` / `tick-exit` still 2/2/2 with
`took_swap=1` twice; slot-ret n=1..3 stay
`v0=1 path=walk`; `menu-entry` siten=2 then
`menu-spin` must climb (the s1924 skip
reproduced). Then read `slot-byte` after
slot-ret n>=4 (`v0=0`):

- one `idx` with `byte!=0`, `ch` small
  (≤16), `base` in RDRAM → H-one-idx
  (next unit names that slot's writer)
- many/all walked `idx` have `byte!=0`
  → H-all-idx (table/base wrong)
- `ch` huge (>64) → H-chcount-wild
  (walk is reading past the table)
- `base` differs between n=1..3 (idle)
  and n>=4 (stuck) → H-base-moved
- `menu-spin` does not climb, or
  slot-ret `v0=1` on entry 2 →
  UNEVALUABLE for the skip

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

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
