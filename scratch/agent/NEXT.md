# NEXT (s7341): idiom-class audit - class P, KSEG0 top-byte tests vs spill pointers (0x81xxxxxx)
HYPOTHESIS-ID: kseg-topbyte-tests
Context: s7340 closed class O (host `0x81000000` bounds, tools/s7340_kseg16_census.py, B 0). A different idiom can still reject
a spill pointer: `(x >> 24) == 0x80`, `(x & 0xFF000000) == 0x80000000`, `(x >> 28) == 8` is fine (0x81 passes), `x >> 24 != 0x80`.
Host count (s7340 grep): upstream_compat.cpp 5, src/rsp/s7324_rcp_spill.cpp 1. Generated tree / PatchesLib not counted yet:
grep the generated C (RecompiledFuncs dir from CMakeLists / fixup_game_funcs.py) for `>> 24` / `0xFF000000` compared to 0x80, and
the retail MIPS idiom `srl tX, ptr, 24` + `addiu/ori 0x80` + `beq/bne` (that one is the game's own check: retail semantics, but at
dd>1 a game-side check that sees a host spill pointer is exactly the H-reject case).
Hypotheses: H-diag (host sites are s7318/s7324 audit classifiers), H-reject (a default-on check, host or game, treats a spill
pointer as invalid), H-none-in-game (the game never tests the top byte; it relies on KSEG masks).
Method: copy tools/s7340_kseg16_census.py frame with the top-byte regex for host; separate pass over generated C with a
per-function list; any game-side site that can see a spill pointer -> name the object type (is it ever spill-allocated? spill
allocations are rs_malloc reqs routed by s6569) and either prove unreachable or convert in a fixup script behind ROGUESQ_S7341=0.
Runtime only if a B site exists: `env SECS=260 zsh scratch/s7326/run.zsh s7341_dd8 ''` with a selftest control on 0x81000100.
