# Session 3009 source table — `0x80017B78`

| Source | Observation |
|---|---|
| Companion symbol map | `setRenderViewScaleFloat = 0x80017B78`; nearby comment describes a single-float setter at `0x8011A840` and deliberately avoids a speculative global-variable name. |
| Generated definition | `RecompiledFuncs/funcs_4.c` contains one `RECOMP_FUNC` definition, a 16-byte leaf storing `$f12` to `0x8011A840`. |
| Generated header/registration | `funcs.h` and `recomp_overlays.inl` already use `setRenderViewScaleFloat`; registration is one 16-byte entry at offset `0x17738`. |
| Generated callers | No direct C call sites; this is consistent with a callback/function-pointer setter and creates no competing identity. |
| Duplicate check | No second `RECOMP_FUNC` definition for `0x80017B78` or `setRenderViewScaleFloat`. |

Conclusion: the operation-level companion name is exact and safe to synchronize in
the project symbol TOML. The next placeholder requiring audit is `0x80017B88`.
