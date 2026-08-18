# NEXT work unit (s1962) — leftover rename `func_800F99C8`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1961 renamed `func_800F9918` → `initActorAsType3`
(`0x800F9918`, metadata-only TOML edit, no build/regen). No
new soak since s1950; already folded into CURRENT-TRUTH.

M5 closed. M3 only as idiom-class. Hangar/512 Y=0x8000 is not
live on the first hangar window. Sweep leftover is the next
bounded unit (strategic priority 4).

## Work unit — TOML metadata-only rename

`func_800F99C8` → `setType3ActorParams`
(TOML `0x4C` already matches generated `rom_size 0x4C`).
Four-step already complete (s1961 preview):
1. `funcs_42.c:6169` (`setType3ActorParams`) is the next
   `RECOMP_FUNC` after `initActorAsType3`.
2. `funcs.h:2181-2182` declares them in that order.
3. `recomp_overlays.inl:1909`: offset `0x00054898` =
   `0x000547E8 + 0xB0`; `rom_size = 0x0000004C` matches TOML.
4. Companion `rogue_squadron64/symbol_files/mission_overlay.txt:760`
   already names `setType3ActorParams = 0x800F99C8` with a
   full field-layout comment.

Before renaming: re-run the non-collision grep
(`RECOMP_FUNC void func_800F99C8` across
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/`)
and a caller check, same as every prior sweep session, then
edit `syms/rogue_squadron.syms.toml:2022` directly.

Do **not** rebuild the game for a metadata-only rename unless
the rename touches a generated `.c` that the Debug target
compiles. Do **not** default `ROGUESQ_SPIN_YIELD` on. Do
**not** chase the hangar `filterVoiceSampleBlock` SIGBUS.

## Do not repeat

- s1942 yield off/on A/B (closed).
- s1942 from-phase-1024 Start/A as a hangar recipe.
- s1943–s1947 eleven-Start-from-boot as a hangar recipe
  without yielding `L_800B8050`.
- Re-walking VMADH/VGE / `0xD60` / ovl20 for Y=0x8000.
- Force-zero slots.
- `requeue_vi=true` as the only arm.
- Ask (b) from s1891 — still human-only.
- Treating 640, attract 512, or title `0x00790400` as hangar.
- Re-running `s1950_hangar_yield_repro` as a work unit.
