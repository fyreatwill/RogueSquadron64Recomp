# Session 3002 — `0x80011C9C`

| Source | Result |
|---|---|
| Companion map | `renderUnlitMeshFaces` in `../rogue_squadron64/symbol_files/main_overlay.txt` |
| Generated definition | One `RECOMP_FUNC` definition in `../N64Recomp/RecompiledFuncs/funcs_4.c` |
| Generated header | `renderUnlitMeshFaces` in `../N64Recomp/RecompiledFuncs/funcs.h` |
| Overlay registration | One `renderUnlitMeshFaces` record in `recomp_overlays.inl` |
| Direct callers | `0x800151A8` and `0x80015390` in `processSceneNode` |
| Duplicate definition check | None at `0x80011C9C` |

The generated C tree was already synchronized to the companion name, while
`syms/rogue_squadron.syms.toml` still used `func_80011C9C`. The scanner stopped
because it only accepts placeholder generated names; this is a tooling
limitation, not an identity conflict. The project TOML was synchronized and
`cmake --build build --config Debug --target RecompiledFuncs` succeeded.
