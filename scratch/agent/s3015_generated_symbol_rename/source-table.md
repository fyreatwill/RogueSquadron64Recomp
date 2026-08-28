# `0x8001B7C8` generated-symbol audit

The companion map names `0x8001B7C8` `beginSceneRenderFrame` and describes it
as the per-scene render-frame kickoff. The generated tree has one
`RECOMP_FUNC` definition in `RecompiledFuncs/funcs_5.c`, already named
`beginSceneRenderFrame`; its body is the complete 16-byte store-and-return
routine.

Generated callers occur at `0x80044BBC`, `0x800ADB2C`, `0x800AF51C`,
`0x800B25F8`, `0x800B414C`, `0x800BFC94`, and `0x800C376C`; all dispatch to
the same generated name. `funcs.h` and `recomp_overlays.inl` also register
`beginSceneRenderFrame`, and the companion `redefs.txt` maps all placeholder
spellings to that name. No duplicate callable definition was found.

The project symbol TOML was the only stale artifact and was synchronized to
`beginSceneRenderFrame`. This selects the exact-companion-name hypothesis and
rules out an unnamed data gap, duplicate callable, or overlay collision for
this address.
