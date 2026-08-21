# NEXT work unit (s2165) — retail oracle at cinematic SIGBUS PCs

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2164 selected `H-NoSuchSite`: neither `slotDispatcherIter` nor
`cutsceneDispatchSlotsByFlag` contains an unsigned KSEG0 `MEM_*`
constant. Crash sites (existing Debug `atos`, no rebuild):

- `slotDispatcherIter+3092` → `funcs_8.c:23678`
  `MEM_BU(ctx->r17, 0X1A)` guest `0x8003E944` `lbu $v0, 0x1A($s1)`
- `cutsceneDispatchSlotsByFlag+8960` → `funcs_27.c:115207`
  `MEM_W(ctx->r2, 0X44)` guest `0x800A87A8` `lwc1 $f2, 0x44($v0)`
  producers `0x800A879C` `lw $v0, 0x50($a2)` then `0x800A87A0`
  `lw $v0, 0x0($v0)`

Table: `scratch/s73_post_a_scene/s2164_unsigned_kseg0_census.txt`.

Ask the retail oracle whether those PCs execute at VI 640 and what
`$s1` / `$v0` they hold. Do not S32-address by guess, re-flip
default-on, or add a wait/slot guard.

`--watch-pc` currently logs pc/prev_pc only. Wire
`DebugGetCPUDataPtr(M64P_CPU_REG_REG)` so each exec hit also prints
`$v0` (gpr[2]) and `$s1` (gpr[17]). Then one Rice run.

## Competing hypotheses and discriminator

- `H-RetailNeverExec`: `--watch-pc` counts stay 0 after the
  whole-RDRAM control fires and `--vi-trace` shows a 640 row.
  Retail does not execute these loads in the cinematic window;
  the port is on a path retail does not take.
- `H-RetailExecsValidPtr`: the PCs execute at 640 and `$s1` /
  `$v0` are KSEG0 RDRAM (`0x80000000..0x807FFFFF`, not 0). The
  port loaded a different pointer; next is writer attribution
  of that slot/object field, not S32-addressing.
- `H-RetailExecsNullOrRaw`: the PCs execute and `$v0` is 0 (or
  `$s1` is non-KSEG0). Retail takes the same load; the port
  SIGBUS is host `MEM_*` on a guest-null/wild pointer. Name that
  writer before any skip/allow/guard.
- `H-CoverageFailure`: whole-RDRAM watch does not fire, or
  `--vi-trace` never prints a 640 row. Null PC counts are
  unevaluable.

Positive control: watch 0 whole-RDRAM must print ~1.6M-class hits
(or the 10000-callback removal line) in the same log as the PC
rows and at least one `[vi]` 640 line. A GPR print of `$v0`/`$s1`
on a synthetic/first exec hit (or on the whole-RDRAM-adjacent
first `--watch-pc` if a known-live PC is included) must be
visible before treating `$v0=0` / `$s1=…` as measured.

s2161 undriven Rice 45s reached 640 `origin=0x0066a500`, not
`0x00696100`. Record whichever 640 origin retail actually
prints; a missing `0x00696100` is a row, not a reason to
discard a 640-gated PC table.

## Exact commands

If `DebugGetCPUDataPtr` is not yet called from the exec-hit
path, add a bounded print of gpr[2] and gpr[17] on
`M64P_BKP_FLAG_EXEC` hits, rebuild `tools/oracle/build.sh`,
then:

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 45 --hit-cap 64 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x8003E944,0x800A87A8,0x800A87A0,0x8003E938 \
      --first-watch 0 --vi-trace \
      > scratch/agent/oracle_s2165_cinematic_pcs.log 2>&1

PCs: crash loads plus the two `lw` producers (`0x8003E938`
`lw $a0, 0($v0)` that becomes `$s1`; `0x800A87A0`
`lw $v0, 0($v0)`).

Do not rebuild the game. Do not flip `get_rsp_microcode`.
If an exec hit shows `$v0==0`, do not add a NULL skip this
iteration — that is ORIGIN work for a later unit.
