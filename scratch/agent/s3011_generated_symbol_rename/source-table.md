# Session 3011 static symbol audit

Address: `0x8001818C`

| Source | Result |
|---|---|
| Companion map | `advanceVideoFrame`; describes the per-frame video advance, buffer-arbiter transitions, buffer swap, and default-material setup. |
| Generated definition | One `RECOMP_FUNC` definition in `RecompiledFuncs/funcs_4.c`; body starts at `0x8001818C` and spans `0x2DC` bytes. |
| Generated callers | One direct call at `0x800014F0`, already calling `advanceVideoFrame`; no generated call targets the placeholder name. |
| Overlay registration | `recomp_overlays.inl` registers `advanceVideoFrame` at offset `0x17D4C`, ROM size `0x2DC`. |
| Project symbol TOML | Was the sole stale entry; synchronized to `advanceVideoFrame`. |

Conclusion: the exact companion name is supported by a unique generated
definition, coherent caller and matching overlay metadata. No duplicate
callable definition or ambiguity was found.
