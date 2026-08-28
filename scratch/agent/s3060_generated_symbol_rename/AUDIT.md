# Session 3060 — generated-symbol audit at `0x80017AE0`

## Competing hypotheses

- **H-ExactIdentity:** the companion name is an exact callable identity and
  the generated tree is synchronized.
- **H-BoundaryOnly:** the address is a fragment, data gap, or non-callable
  boundary despite the companion label.
- **H-MappingDrift:** one or more generated metadata surfaces disagree with
  the companion address or name.

## Discriminating measurement

Compare the companion identity, generated body, callers, header, overlay
registration, project TOML, and local definitions. Agreement on the address,
extent, callable shape, and name selects H-ExactIdentity; a fragment or data
gap selects H-BoundaryOnly; any address/name/extent disagreement selects
H-MappingDrift.

## Six-surface result

1. **Companion identity:** `../rogue_squadron64/symbol_files/main_overlay.txt`
   maps `setViewStateBytesAndFadeScale = 0x80017AE0`.
2. **Generated body:** `../N64Recomp/RecompiledFuncs/funcs_4.c` defines the
   symbol at `0x80017AE0` and returns at `0x80017B24`. It loads a stack fade
   divisor, stores input bytes at `0x8012A873`–`0x8012A875`, stores the input
   scale at `0x8012A878`, computes and stores the adjusted scale at
   `0x8012A87C`, and returns 1. This is a coherent callable setter.
3. **Callers:** generated callers are present in `funcs_9.c` and `funcs_36.c`,
   both calling the named symbol at `0x80017AE0`.
4. **Header:** `../N64Recomp/RecompiledFuncs/funcs.h:223` declares the same
   host function name and signature.
5. **Overlay registration:** `../N64Recomp/RecompiledFuncs/recomp_overlays.inl:224`
   registers the symbol at offset `0x176A0` with ROM size `0x48`, matching the
   VRAM extent `0x80017AE0`–`0x80017B27`.
6. **Project TOML:** `syms/rogue_squadron.syms.toml:235` names the same address
   and size (`0x48`).

`rg` found one generated definition and no duplicate definition or leftover
`func_80017AE0` reference in the current generated tree. The adjacent
`setViewStateTripletBytes` registration begins at `0x80017B28`, confirming the
boundary.

## Decision

**H-ExactIdentity selected.** No rename or synchronization change was needed;
the candidate was already synchronized. The next bounded sweep candidate is
`0x80017B28`.

