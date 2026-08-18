# NEXT work unit (s1964) — decide `func_800FEF10`, then resume sweep at `func_800FFE00`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1963 batch-renamed thirty leftovers in one TOML edit
(`func_800FA250` through `func_800FEECC`; see PORTING-STATE.md
s1963). The run stopped cleanly at the next entry,
`func_800FEF10` (`syms/rogue_squadron.syms.toml:2072`, size
`0xEF0`): its generated body at `funcs_43.c:5660` is still
literally `RECOMP_FUNC void func_800FEF10(...)` — the generated
tree has no real name for it yet, so it needs genuine
reverse-engineering, not a metadata sync. Leave it as-is (do not
invent a name) unless this session's scope is explicitly RE work,
which is out of scope for the sweep.

## Work unit — resume the contiguous-run scan from `func_800FFE00`

`syms/rogue_squadron.syms.toml:2073` is `func_800FFE00` (size
`0x3C8`), the entry right after `func_800FEF10`. Same
four-step-per-entry technique as s1962/s1963:

1. For each subsequent `func_800*`/`func_801*` entry, grep
   `RecompiledFuncs/*.c` (check `funcs_43.c` first, then
   `funcs_44.c` etc. as addresses climb) for the
   `// 0x<addr>:` comment covering that vram.
2. Confirm the `RECOMP_FUNC void <name>(` line exactly 3 lines
   above that comment (the fixed `uint64_t hi=0,lo=0,result=0;` /
   `int c1cs=0;` prologue) — this proves the address is the
   function's own start, not a mid-body instruction landing on a
   larger, already-named function (a real risk once several
   short functions get folded near each other).
3. If the generated name is still `func_0x...`, stop the run
   there — out of scope for this sweep (needs real RE).
4. For every already-named entry: confirm zero prior uses of the
   target name anywhere in `syms/rogue_squadron.syms.toml` (grep
   the whole candidate-name list against the TOML in one pass,
   expect zero hits) and zero remaining `func_800F<addr>`/
   `func_8010<addr>` string references anywhere in the repo
   (`.py`/`.c`/`.h`/`.toml`) after the (mental) edit.
5. Batch all confirmed renames into one edit to
   `syms/rogue_squadron.syms.toml`, same as s1962/s1963. Validate
   with `python3 -c "import tomllib; tomllib.load(open('syms/rogue_squadron.syms.toml','rb'))"`.

`fake_func_*` entries (different naming convention) — leave alone
unless you specifically understand why they're prefixed `fake_`.

Do **not** rebuild the game for a metadata-only rename unless the
rename touches a generated `.c` that the Debug target compiles
(it won't, if the generated name already exists). Do **not**
default `ROGUESQ_SPIN_YIELD` on. Do **not** chase the hangar
`filterVoiceSampleBlock` SIGBUS.

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
- Renaming `func_800FEF10` without real RE — its generated body
  has no real name yet (confirmed s1963).
