# NEXT work unit (s1966) — resume sweep at `func_800B2A98`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

s1965 batch-renamed 26 leftovers in one TOML edit (`func_800ADB70` through
`func_800B2564`; see PORTING-STATE.md s1965), reusing
`tools/sweep_scan_candidates.py <start_name>` — don't re-derive the grep by
hand. The run stopped cleanly at the next entry, `func_800B2630`
(`syms/rogue_squadron.syms.toml:2435`, size `0x468`): still a literal
placeholder in the generated tree (`funcs_30.c:11406`) — genuine
reverse-engineering needed, not a metadata sync. Leave it as-is unless this
session's scope is explicitly RE work, which is out of scope for the sweep.

## Work unit — resume the scan from `func_800B2A98`

```
python3 tools/sweep_scan_candidates.py func_800B2A98
```

This was already dry-run verified in s1965: it resolves 4 entries
(`func_800B2A98` → `allocFormatTextElement`, `func_800B2D50` →
`loadNamedTextureDescriptor`, `func_800B32F4` → `allocTextRenderTarget`,
`func_800B3650` → `tickFormatMessageWorker`) before stopping cleanly at
`func_800B3824` (`funcs_30.c:15181`, still a literal placeholder — out of
scope, stop there). Confirm the same result still holds (nothing else should
have changed the generated tree or the TOML between sessions), then:

1. Before editing, verify the printed candidates the same way s1964/s1965
   did:
   - zero duplicate generated names among the candidates
     (`cut -f2 <output> | sort | uniq -d` should be empty)
   - zero collisions against the full existing TOML name list — do an EXACT
     match check (a python `set` membership test on `name = "X"` matches, not
     a raw substring grep: s1965 hit a false positive where
     `composeInterpolatedNodeMatricesAlt` contains
     `composeInterpolatedNodeMatrices` as a substring but is not a real
     collision)
   - zero remaining `func_800B2<addr>`/`func_800B3<addr>` string references
     anywhere else in the repo (`.py`/`.c`/`.h`/`.toml`) for any renamed
     address, excluding the symbol TOML itself
   - the tool already excludes any address with more than one `RECOMP_FUNC`
     match tree-wide (overlay VRAM reuse) — trust that guard, don't re-add a
     first-match shortcut.
2. Batch all confirmed renames into one edit to
   `syms/rogue_squadron.syms.toml` (an address-keyed python replace over the
   file text is faster and less error-prone than 4 manual Edit calls).
   Validate with
   `python3 -c "import tomllib; tomllib.load(open('syms/rogue_squadron.syms.toml','rb'))"`.
3. After editing, re-run `python3 tools/sweep_scan_candidates.py
   func_800B3824` (or whatever address the batch stopped just before) to
   confirm it's still unresolved, then run the scan starting from the TOML
   entry right after it to find the *next* resume point for the following
   session's NEXT.md, the same way s1964/s1965 did.

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
- Renaming `func_800FEF10`, `func_800AB658`, or `func_800B2630` without real
  RE — none has a real generated name yet (confirmed s1963, s1964, s1965
  respectively).
- Manually grepping `RecompiledFuncs/*.c` per-entry for this sweep — use
  `tools/sweep_scan_candidates.py`, which already handles the overlay VRAM
  reuse case that a naive first-match grep gets wrong.
- Treating a substring match (`grep -F` against candidate names) as a real
  TOML-name collision — verify collisions with an exact `set` membership
  check (s1965).
