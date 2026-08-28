# Source table: `0x800B75C4`

## Candidate

| Field | Evidence |
|---|---|
| Project symbol | `fake_func_800B75C4`, VRAM `0x800B75C4`, size `0xC`, mission overlay |
| Generated definition | Active `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_31.c` defines `fake_func_800B75C4`; the body is `lui $at, 0x8005` at `0x800B75C4`, `lwc1 $f2, 0xC58($at)` at `0x800B75C8`, and `mul.s $f0, $f0, $f2` at `0x800B75CC` |
| Predecessor | `findLockOnTarget` starts at `0x800B7590`, size `0x34`, and its branch at `0x800B759C` targets label `L_800B75C4`; its epilogue ends at `0x800B75C0` |
| Successor | `playerYwingInit` starts at `0x800B75D0`, size `0x200`, with its own `addiu $sp, $sp, -0x50` prologue |
| Companion semantic map | Project symbol map names `findLockOnTarget` at `0x800B7590` and `playerYwingInit` at `0x800B75D0`; no exact companion semantic name is assigned to `0x800B75C4` |
| Generated callers and lookups | The active generated tree contains the `findLockOnTarget` internal branch to `L_800B75C4`; no `jal` or independent lookup of `fake_func_800B75C4` was found. `playerYwingInit` is called directly at `0x800B85D8` and `0x800B86F0` |
| Callable evidence | No standalone prologue, return, independent caller, or independent lookup. The address is a branch target inside the preceding routine and the three-instruction body has no callable boundary |

## Decision

Selected **H-Fragment**. The three words are valid executable instructions, so
this is not a mechanically proven data gap. The internal branch from
`findLockOnTarget` proves the address is part of the preceding routine's
control flow, while `playerYwingInit` begins at the next address with its own
prologue. No exact semantic name for this fragment is justified. Preserve
`fake_func_800B75C4` in the project map, companion map, generated header/body,
and overlay table.

The stale `playerYwingInitPreamble` entries were removed from
`tools/rename_generated_symbols.py` and `tools/rename/build_redefs.py` so a
future reconciliation cannot apply an unsupported rename.

ORIGIN: naming-only classification. No runtime, generated instruction,
submodule, or mitigation-shaped behavior changed.
