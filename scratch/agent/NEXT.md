# NEXT work unit (s1951) — leftover rename `func_800F7C74`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1950 synchronized `renderNpcAnchoredProceduralEffect`
(`0x800F7130`). Consumed `s1950_hangar_yield_repro`: hangar
512 at 24.8s, crash at 4.3s after 1 frame — same short
window as s1949. Do not chase that SIGBUS.

M5 closed. M3 only as idiom-class. Hangar/512 Y=0x8000 is not
live on the first hangar window. Sweep leftover is the next
bounded unit (strategic priority 4).

## Work unit — TOML metadata-only rename

`func_800F7C74` → `spawnAndUpdateEffectActors`
(TOML `0x724` already matches generated `rom_size 0x724`).
Four-step already complete (s1950 preview). Rename directly.

After that, parked for a later sweep session:
`func_800F8398` → `executeActorType4Effect`
`func_800F9474` → `clearObjectField112`

Generated tree:
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/`

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
