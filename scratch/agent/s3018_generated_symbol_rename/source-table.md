# `0x8001BB6C` generated-symbol audit

The companion `main_overlay.txt` names `0x8001BB6C`
`selectAndApplyViMode`, between `swapBufferWithViMode` at `0x8001BA9C` and
`computeFramebufferByteSize` at `0x8001BC48`.

The generated tree has one `RECOMP_FUNC` definition in
`RecompiledFuncs/funcs_5.c`, already named `selectAndApplyViMode`; its body
matches the TOML size of 0xDC and selects/copies a VI mode before calling
`osViSetMode_recomp` and `waitOnVideoQueue`. The generated caller at
`0x800186C0`, `funcs.h`, and `recomp_overlays.inl` all use/register the same
name and matching entry.

A tree-wide search found no second callable definition or conflicting
registration for this address. The project symbol TOML was the only stale
artifact and was synchronized to `selectAndApplyViMode`. The generated
functions target built successfully.

This selects the exact-companion-name hypothesis and rules out an unnamed
data gap and a local duplicate callable for this address. No runtime, audio,
or route behavior changed. The scanner's next unresolved placeholder is
`0x8001C260`, which has no standalone generated prologue match.
