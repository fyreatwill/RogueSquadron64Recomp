# Session 2532 symbol census

## Region table

| Placeholder | Span | Generated body | Companion evidence | Result |
|---|---:|---|---|---|
| `fake_func_80093E74` | `0x80093E74..0x80093E7F` (`0xC`) | `lw ra,0x24(sp)`; `lw fp,0x20(sp)`; `addiu sp,sp,0x28` | `main_overlay.txt` and `syms/rogue_squadron.syms.toml` retain the exact fake name; adjacent entries are `sqrtf_recomp` and `musyxComputeNotePlaybackRate` | No defensible rename |

## Discriminator

The complete generated span was inspected in `RecompiledFuncs/funcs_25.c`,
`funcs.h`, and `recomp_overlays.inl`. Exact-address searches across the
companion source and symbol files found no human name, m2c definition, or
caller attribution. The fragment is a function epilogue with no independent
semantic evidence. This selects `H-no-match`; it does not prove the fragment
is dead or permanently unnameable.

The same target was already recorded in an older ledger census (the current
NEXT pointer had not advanced past it). That historical entry is treated as
confirmation, not as evidence for a rename. No generated input, runtime code,
or symbol table was changed.
