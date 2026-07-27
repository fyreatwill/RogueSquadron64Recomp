# NEXT work unit — M3: root-cause `do_rom_read`'s `raw_r7` corruption (corrected), or characterize the new 11th crash class

s92 corrected two things about the s91 plan before finding a new crash
class. Read both before doing anything else.

## What s92 found

1. **The planned "dump `OSIoMesg` at `mb`" instrument was based on a
   wrong premise.** `osPiStartDma_recomp`
   (`lib/N64ModernRuntime/librecomp/src/pi.cpp:347-374`) never
   dereferences `mb` (`ctx->r4`) — `devAddr = ctx->r7 | rom_base` is a
   direct register argument (`$a3`) the caller passes, matching real
   libultra's `osPiStartDma(mb, pri, direction, devAddr, dramAddr,
   size, mq)` signature where `devAddr` is explicit, not read out of
   the message struct. There is nothing to dump at `mb` for `devAddr`.
2. **`ra=0x00000000` is not corruption evidence.** A soak
   (`s92_romread2`, s91's 5 flags + `ROGUESQ_LOG_THREAD_RESUME=1`)
   showed `ra=0x00000000` on **487/487** `pi-start-dma` calls this run
   — sane ones included — plus the same universal-zero pattern in 3
   unrelated entry-log instruments (`anim-recurse` 6740/6740,
   `anim-tex-stream` 4568/4568, `hangar-entry` 2/2). This refutes s91's
   "both r31 and r7 wrong together" framing. The corruption is
   `raw_r7` alone.
3. `do_rom_read` **did not recur** this soak (0/1, first miss after
   3/3 in s85/s91). Likely confound: `ROGUESQ_LOG_THREAD_RESUME=1`
   generates ~120k `fprintf`+`fflush` calls, enough of a timing
   perturbation that a **new 11th crash class** won the race instead:
   SIGBUS in `projectModelBoundsToScreen` (confirmed real symbol,
   `0x80065E98`) via `hangarTickCameraOrbit` (`static_5_800ADB70`) ← a
   symbol_files-named-but-suspect `loadCutsceneAssetsByIndex`
   (`static_5_800A9270`) ← `runHangarSelectionFrame` →
   `runHangarMenuFromOverlay` → `menuOverlayInit`.
4. The decomp source tree
   (`~/Documents/Tools/rogue_squadron64/src/libultra/io/{pimgr,pidma}.c`)
   has no usable C source for the real PI-manager thread body —
   both are `INCLUDE_ASM` stubs in this checkout. Can't read the real
   caller's logic offline without a fuller asm extraction.

## Two paths for this iteration — pick based on what's cheap

### Path A (preferred): re-attempt `do_rom_read` without the confound

Reproduce with **only** the s91 five flags (drop
`ROGUESQ_LOG_THREAD_RESUME`) to avoid the timing perturbation s92
identified:

```
env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
    ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
    ROGUESQ_LOG_DMA=1 \
    PROBE_MODE=start_only HOLD_S=30 zsh \
    scratch/s73_post_a_scene/run_mission_keys.sh s93_romread3 0 12
```

If it recurs: this confirms the confound theory and gets a 4th
byte-identical data point (still just on `raw_r7`, since `ra=0` is now
known-routine — don't re-report `ra=0` as a new fact). Next
discriminating step from there: since we know `devAddr` is a live
register argument from a caller we can't currently read in source
form, the next real probe is finding the asm for the guest PI-manager
thread body (search `symbol_files/*.txt` for anything covering libultra
PI-manager addresses, or extract fresh MIPS disassembly from the ROM
around whatever function calls `osPiStartDma`) to see the actual
compare/branch logic that produces the corrupted `devAddr`.

If it doesn't recur again (2nd miss): stop treating this as
reliably-reproducible-on-demand; note the miss rate (now 3/5 across
all attempts) in the write-up and consider it timing/scene-dependent
rather than "fires whenever this soak shape runs."

### Path B: characterize the new 11th class if Path A also lands it

If either this run or a future one reproduces the
`projectModelBoundsToScreen` SIGBUS, read `hangarTickCameraOrbit`
(`static_5_800ADB70`) and the suspect `loadCutsceneAssetsByIndex`
(`static_5_800A9270`) call in the RecompiledFuncs `.c` (search
`build/` for the generated overlay 5 source, or grep symbol_files for
context) to see what argument reaches `projectModelBoundsToScreen` and
whether it's read from a struct that could plausibly be
uninitialized/stale — same "unchecked deref off a corrupt arg" shape
as classes 7-10.

## Do not

- Do not re-plan "dump the `OSIoMesg` at `mb`" — refuted, `mb` is
  never read in `osPiStartDma_recomp`.
- Do not cite `ra=0x00000000` as corruption evidence in any writeup —
  it's the routine value for this and 3 other unrelated call sites.
- Do not combine `ROGUESQ_LOG_THREAD_RESUME=1` with a `do_rom_read`
  repro attempt without a specific reason to re-test the confound
  theory itself.
- Do not re-run the "arm one flag, hope for TMEM-zero" soak — 0/6,
  stays opportunistic (CURRENT-TRUTH next-steps item 2).
- Do not chase `advancePlayerAnimationPhase` — parked since s89.
- Budget: this is the 2nd dedicated soak on the do_rom_read repro
  since the "refined H1/H2" experiment shape started at s92 — 1 more
  non-discriminating attempt before parking it per rule 8.
