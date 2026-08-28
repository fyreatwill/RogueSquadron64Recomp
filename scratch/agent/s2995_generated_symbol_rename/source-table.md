# Session 2995 — `0x80002E10` source table

The bounded audit agrees on one callable identity:

| Source | Evidence |
| --- | --- |
| Companion map | `../rogue_squadron64/symbol_files/main_overlay.txt` names `0x80002E10` `siServiceThread` and describes it as the controller polling thread. |
| Generated definition | `../N64Recomp/RecompiledFuncs/funcs_0.c:8186` has one `RECOMP_FUNC` definition named `siServiceThread`; its first instruction comment is `0x80002E10`. |
| Generated registration | `../N64Recomp/RecompiledFuncs/recomp_overlays.inl:45` registers `siServiceThread` at offset `0x29D0`, size `0x13C`. |
| Duplicate check | `rg` found no second generated definition or placeholder definition for `0x80002E10`. |
| Project TOML before this iteration | `syms/rogue_squadron.syms.toml:55` alone used `func_80002E10`. |

The project TOML now uses `siServiceThread`. The generated-functions target
built successfully. The helper `sweep_scan_candidates.py siServiceThread`
cannot resume from a human name because its parser accepts only placeholder
names; this does not affect the source audit. The next placeholder in TOML
order is `func_80007D74`.
