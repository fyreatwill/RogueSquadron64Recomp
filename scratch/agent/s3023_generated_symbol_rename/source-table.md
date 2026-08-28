# Session 3023 — `0x8002BB34` static audit

## Discriminator

The audit separates an exact companion rename from an unnamed fragment/data
gap and from a generated overlay collision by checking the companion symbol
and source trees, generated definitions/callers/registrations, and the
surrounding symbol boundaries.

## Evidence

| Source | Result |
|---|---|
| `syms/rogue_squadron.syms.toml` | Contains only placeholder `func_8002BB34`, size `0xE8`. |
| `../rogue_squadron64/symbol_files/libultra.txt` | No entry at `0x8002BB34`; neighboring known entries are `__osException` at `0x8002B600`, `__osEnqueueAndYield` at `0x8002BC1C`, and jump-table labels in the intervening exception region. |
| Companion source/map search | No `8002BB34`, `func_8002BB34`, or semantic companion name found in `src/`, `docs/`, `symbol_files/`, or `build/redefs.txt`. |
| `../N64Recomp/RecompiledFuncs` search | No generated comment, `RECOMP_FUNC` definition, header declaration, direct caller, or overlay registration for `0x8002BB34`. |
| `python3 tools/sweep_scan_candidates.py func_8002BB34` | `STOP: func_8002BB34 has no comment/prologue match in generated tree`; resolved `0`. |
| Boundary arithmetic | Placeholder range `0x8002BB34..0x8002BC1B` overlaps the TOML `__osException` range `0x8002B600..0x8002B837` and ends exactly at `__osEnqueueAndYield` `0x8002BC1C`; it is not an independently supported generated callable boundary. |

## Classification

No exact companion identity exists, and there is no generated callable to
rename or collision to resolve. The placeholder remains unchanged. The
overlapping range is best treated as a stale/unsupported symbol-table entry,
not promoted to a semantic `data_gap_*` name because the available evidence
does not establish a data-only fragment boundary.

No build or runtime run was needed: the discriminator selected the no-rename
branch before any source change.
