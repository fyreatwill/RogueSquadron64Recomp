# Session 2999 — `0x8000CB88`

The companion symbol file maps `0x8000CB88` exactly to
`reserveAndEmitDLEntry`. The generated tree contains one callable definition,
in `../N64Recomp/RecompiledFuncs/funcs_3.c`, with the same name; its generated
header declaration and overlay registration also use that name. Direct
generated callers are `0x800102B8`, `0x800109E4`, `0x8000CF1C`, and
`0x8000D444` (four call sites; the first two and latter two are distinct
callers in the generated tree). No duplicate callable definition was found.

The candidate scanner reports one address with multiple `RECOMP_FUNC` matches
tree-wide because of overlay reuse, but the concrete definition search found
only the single callable entry above. This is therefore an exact, coherent
rename rather than an ambiguous placeholder.

Changed only `syms/rogue_squadron.syms.toml`; no runtime behavior or audio
path was modified.
