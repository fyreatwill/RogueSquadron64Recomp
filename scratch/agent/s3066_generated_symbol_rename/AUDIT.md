# Session 3066 — `0x800B58B4`

## Discriminator

The six-surface comparison distinguishes an exact semantic preamble from a
boundary-only fragment or metadata drift. A callable body would need its own
return/control-flow shape and callers; a fragment may be named only when
adjacent companion evidence and independent tooling identify its role.

## Surface comparison

| Surface | Evidence | Result |
|---|---|---|
| Companion symbol map | `mission_overlay.txt` retains `fake_func_800B58B4 = 0x800B58B4`; comment on next line reads "// real function is playerAwingInit"; `playerAwingInit` is at `0x800B58C0` | Companion identifies this as a fake preamble preceding the real body |
| Companion redefs.txt | `fake_func_800B58B4 playerAwingInitPreamble` at line 10116 — independent from the symbol map | Second independent source supplies the exact name |
| Generated body | Per s2962 audit: 3 instructions `addiu $a3, $zero, 0x7F`, `jal 0x800E9B10`, `nop` delay slot; size 0xC matches TOML; no prologue or return sequence | Confirms non-callable preamble |
| Generated callers | s2962 search found no generated caller targeting `0x800B58B4`; adjacent caller targets `0x800B58C0` (`playerAwingInit`) | No independent call site for this fragment |
| Header / overlay registration | Generated files absent (no regen in current workspace); s2962 documented body matches TOML size=0xC and pattern is structurally identical to `menuControllerInputPreamble` (s3065) | Not separately verified this session; consistent with fragment record |
| Project metadata / tooling | TOML had stale `fake_func_800B58B4`; `rename_generated_symbols.py` line 113 and `build_redefs.py` line 70 both map it to `playerAwingInitPreamble`; companion `fake_func_800B75C4` (before `playerYwingInit`) and `fake_func_800B89F4` (before `playerVwingInit`) use the identical pattern | Two independent rename tools agree; pattern repeats for every shiptype Init preamble |

## Pattern context

The companion shows a recurring pattern: each shiptype init (`playerAwingInit`,
`playerYwingInit`, `playerVwingInit`) is immediately preceded by a `fake_func`
record of size 0xC. All three are noted "real function is X" in the companion.
`menuControllerInputPreamble` (s3065) established the precedent for naming
these fragment records as `XPreamble` when the adjacent body and rename maps
provide the exact name independently.

## Decision

Selected `H-ExactIdentity` for the bounded preamble name
`playerAwingInitPreamble`. The companion (two surfaces: mission_overlay.txt +
redefs.txt) and the rename tools (two surfaces: rename_generated_symbols.py +
build_redefs.py) all agree. Session 2962 preserved the placeholder because the
rename maps had not yet supplied the exact preamble name; that obstacle is now
resolved. The project TOML was synchronized. No runtime build or run was needed.
