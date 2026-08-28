# Session 3010 static symbol audit

Address: `0x80017B88`

| Source | Result |
|---|---|
| Companion map | `buildAndRegisterDefaultMaterial`; describes graphics-state writes and default-material registration; callers are `advanceVideoFrame` and `initVideoBootWrapper`. |
| Generated definition | One `RECOMP_FUNC` definition in `RecompiledFuncs/funcs_4.c`; body starts at `0x80017B88` and spans `0x604` bytes. |
| Generated callers | Two direct calls at `0x800183F8` and `0x800185DC`, both already call `buildAndRegisterDefaultMaterial`. |
| Overlay registration | `recomp_overlays.inl` registers `buildAndRegisterDefaultMaterial` at offset `0x17748`, ROM size `0x604`. |
| Project symbol TOML | Was the sole stale entry; synchronized to `buildAndRegisterDefaultMaterial`. |

Conclusion: the exact companion name is supported by a unique generated
definition, coherent callers, and matching overlay metadata. No duplicate
callable definition or ambiguity was found.
