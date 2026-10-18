# Generated-symbol audit — Session 5399

The bounded candidate was `fake_func_800B58B4` in the live sibling tree
`../N64Recomp/RecompiledFuncs`.

The generated record starts at `0x800B58B4` and ends at `0x800B58C0`, exactly
`0xC` bytes. Its two instructions are the preamble before the generated
`playerAwingInit` entry at `0x800B58C0`. The companion map labels the address
as a fake function and says the real function is `playerAwingInit`; the
checked-in syms mapping independently assigns the exact `0xC`-byte span the
semantic name `playerAwingInitPreamble`. The exact generated span, following
function boundary, and syms size agree, so the preamble name is justified.

The sibling repository's committed `HEAD` already contains
`playerAwingInitPreamble` in `funcs_31.c`, `funcs.h`, and
`recomp_overlays.inl`; the stale placeholder was present only in its
pre-existing dirty worktree. The bounded check therefore selected H3 and made
no committed generated-code change. No runtime build or soak was needed.
