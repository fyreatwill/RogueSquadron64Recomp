# NEXT work unit (s1965) — decide `func_800AB658`, then resume sweep at `func_800ADB70`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1964 batch-renamed 221 leftovers in one TOML edit (`func_800FFE00` through
`func_800AB1C8`; see PORTING-STATE.md s1964) and cleared every `func_801*`
placeholder. It also promoted the scan from a scratch script to
`tools/sweep_scan_candidates.py <start_name>` — reuse it, don't re-derive the
grep by hand. The run stopped cleanly at the next entry, `func_800AB658`
(`syms/rogue_squadron.syms.toml:2402`, size `0x2518`): **no** `RECOMP_FUNC`
definition for that address exists anywhere in the generated tree (not even
under a different name) — genuine reverse-engineering needed, not a metadata
sync. Leave it as-is unless this session's scope is explicitly RE work, which
is out of scope for the sweep.

## Work unit — resume the scan from `func_800ADB70`

```
python3 tools/sweep_scan_candidates.py func_800ADB70
```

This was already dry-run verified this session: it resolves 26 entries
(`func_800ADB70` → `hangarTickCameraOrbit` ... through the entry before
`func_800B2630`, which is still a literal placeholder in the generated tree
— out of scope, stop there) before stopping. Confirm the same result still
holds (nothing else should have changed the generated tree or the TOML
between sessions), then:

1. Before editing, verify the printed candidates the same way s1964 did:
   - zero duplicate generated names among the candidates
     (`cut -f2 <output> | sort | uniq -d` should be empty)
   - zero collisions against the full existing TOML name list (none of the
     candidate names already appear as a `name = "..."` anywhere in
     `syms/rogue_squadron.syms.toml`)
   - zero remaining `func_800AD<addr>`/`func_800AE<addr>`/... string
     references anywhere else in the repo (`.py`/`.c`/`.h`/`.toml`) for any
     renamed address (`grep -rFf <old-names-file> --include='*.toml'
     --include='*.py' --include='*.c' --include='*.h' .`, excluding the
     symbol TOML itself)
   - the tool already excludes any address with more than one
     `RECOMP_FUNC` match tree-wide (overlay VRAM reuse) — trust that guard,
     don't re-add a first-match shortcut.
2. Batch all confirmed renames into one edit to
   `syms/rogue_squadron.syms.toml`. Validate with
   `python3 -c "import tomllib; tomllib.load(open('syms/rogue_squadron.syms.toml','rb'))"`.
3. After editing, re-run `python3 tools/sweep_scan_candidates.py
   func_800B2630` (or whatever address the batch stopped just before) to
   find the *next* resume point for the following session's NEXT.md, the
   same way s1964 did for this one.

`fake_func_*` entries (different naming convention) — leave alone unless you
specifically understand why they're prefixed `fake_`.

Do **not** rebuild the game for a metadata-only rename unless the rename
touches a generated `.c` that the Debug target compiles (it won't, if the
generated name already exists). Do **not** default `ROGUESQ_SPIN_YIELD` on.
Do **not** chase the hangar `filterVoiceSampleBlock` SIGBUS.

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
- Renaming `func_800FEF10` or `func_800AB658` without real RE — neither has
  a real generated name yet (confirmed s1963 and s1964 respectively).
- Manually grepping `RecompiledFuncs/*.c` per-entry for this sweep — use
  `tools/sweep_scan_candidates.py`, which already handles the overlay VRAM
  reuse case that a naive first-match grep gets wrong.
