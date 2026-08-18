# NEXT work unit (s1963) — leftover rename `func_800FA250` and neighbors

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1962 batch-renamed nine leftovers in one TOML edit
(`func_800F99C8` through `func_800F9D68`; see PORTING-STATE.md
s1962). The scan technique that made this fast: grep the
generated tree at
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/`
for the `RECOMP_FUNC void` line covering each TOML `func_800*`
address — if the generated `.c` already carries a real name
(not `func_0x...`), the TOML is just stale metadata and the
rename is zero-risk. Do this per-entry check for every entry in
a contiguous run before batching the TOML edit; don't assume
the whole run is safe from checking one or two.

M5 closed. M3 only as idiom-class. Hangar/512 Y=0x8000 is not
live on the first hangar window. Sweep leftover is the next
bounded unit (strategic priority 4).

## Work unit — TOML metadata-only rename, batch scan

`syms/rogue_squadron.syms.toml:2039` currently reads
`func_800FA250` (`vram = 0x800FA250, size = 0x454`). The
generated body at `funcs_42.c:7916` is already
`RECOMP_FUNC void initMission(...)` — confirmed this session,
not yet verified for collision/caller-leftover.

Before renaming, for `func_800FA250` and every subsequent
`func_800FA*`/`func_800FB*` entry in the same contiguous run
(`syms/rogue_squadron.syms.toml:2039` onward — next lines are
`func_800FA6A4`, `func_800FADEC`, `func_800FAF0C`, `func_800FB05C`,
`func_800FB190`, `func_800FB2F8`, `func_800FB4B0`, `func_800FB6C0`,
`func_800FB9E4`, `func_800FBAE8`, `func_800FBB44`, …):
1. Find the `RECOMP_FUNC void <name>(` line covering that address
   in `funcs_42.c` (or wherever it lives) via the `// 0x<addr>:`
   comment inside the function body, same technique as s1962.
2. If the generated name is still `func_0x...`, stop the run there
   — that entry needs the harder path (real reverse-engineering,
   not a metadata sync) and is out of scope for this rename sweep.
3. For every already-named entry: confirm exactly one
   `RECOMP_FUNC void <name>(` definition tree-wide (no collision)
   and zero remaining `func_800F<addr>` string references
   tree-wide after the (mental) edit.
4. Batch all confirmed renames into one edit to
   `syms/rogue_squadron.syms.toml`, same as s1962.

`fake_func_800FA248` (line 2038) is a different naming
convention (`fake_func_`, not `func_`) — leave it alone unless
you specifically understand why it's prefixed `fake_`.

Do **not** rebuild the game for a metadata-only rename unless
the rename touches a generated `.c` that the Debug target
compiles (it won't, if the generated name already exists). Do
**not** default `ROGUESQ_SPIN_YIELD` on. Do **not** chase the
hangar `filterVoiceSampleBlock` SIGBUS.

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
