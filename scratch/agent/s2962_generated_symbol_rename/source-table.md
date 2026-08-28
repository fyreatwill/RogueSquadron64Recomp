# Source table: `0x800B58B4`

## Candidate

| Field | Evidence |
|---|---|
| Project symbol | `fake_func_800B58B4`, VRAM `0x800B58B4`, size `0xC`, mission overlay |
| Generated definition | `RecompiledFuncs/funcs_31.c` defines `fake_func_800B58B4`; the body is `addiu $a3, $zero, 0x7F` at `0x800B58B4`, `jal 0x800E9B10` at `0x800B58B8`, and its `nop` delay slot at `0x800B58BC` |
| Predecessor | `isWeaponSlotReady` starts at `0x800B585C`, has size `0x58`, and ends at `0x800B58B0` with its return delay-slot instruction |
| Successor | `playerAwingInit` starts at `0x800B58C0`, size `0x28C`, with its own stack-frame prologue |
| Companion semantic map | `playerAwingInit = 0x800B58C0`; the companion retains `fake_func_800B58B4` and comments “real function is playerAwingInit” |
| Companion source/m2c | No exact source routine is keyed to `0x800B58B4`; the available evidence is the larger `playerAwingInit` entry |
| Generated callers | No call or independent lookup of `fake_func_800B58B4` found in the current generated tree; the only matches are its definition, overlay registration, and address comments |
| Callable evidence | No standalone prologue, return, independent caller, or lookup. The `jal 0x800E9B10` target is an overlay/symbol-split artifact, not a verified callable boundary for this record |

## Decision

Selected **H-Fragment**. The three words are valid executable-looking output,
so this is not a mechanically proven data gap. The adjacent named
`playerAwingInit` body and companion comment do not prove that this fragment is
itself a callable preamble or provide an exact semantic name for it. Preserve
`fake_func_800B58B4` in the project map, companion map, generated header/body,
and overlay table. The next census lead is `0x800B75C4`.

ORIGIN: naming-only classification. No runtime, generated instruction,
submodule, or mitigation-shaped behavior changed.
