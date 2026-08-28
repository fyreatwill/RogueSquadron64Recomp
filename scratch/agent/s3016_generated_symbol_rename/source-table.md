# `0x8001B7D8` generated-symbol audit

The companion `main_overlay.txt` names `0x8001B7D8`
`clearPendingViChanges`, with the adjacent `0x8001B7F0` entry named
`applyPendingViChanges`. The generated tree has one `RECOMP_FUNC` definition
in `RecompiledFuncs/funcs_5.c`, already named `clearPendingViChanges`; its
0x18-byte body clears the two pending VI words at `0x80128E90` and
`0x80128E94` and returns.

Generated callers occur at `0x800182D8` and `0x800184B4`; both dispatch to the
same generated name. `funcs.h` and `recomp_overlays.inl` also register
`clearPendingViChanges`. The candidate scan reported one tree-wide overlay
reuse match, but no second local callable definition or conflicting
registration for this address. The companion `redefs.txt` already maps the
placeholder spelling to the semantic name.

The project symbol TOML was the only stale artifact and was synchronized to
`clearPendingViChanges`. This selects the exact-companion-name hypothesis and
rules out an unnamed data gap and a local duplicate callable for this address.
