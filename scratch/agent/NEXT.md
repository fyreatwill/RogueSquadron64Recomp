# NEXT: exact count of populated link rows, and who writes row+2 after pool init (0x80041EF0)
HYPOTHESIS-ID: g1c-dd8-limit
Known (s6480): *0x80136FCC -> pool of n 12-byte rows (n from level data, load_level_hmp 0x80044554 passes a0 to 0x80041EF0). Gate: Y=row[cell+0x1E]+2 != FFFF && row[Y]+4==1.
H-streamer-bound: non-FFFF row+2 writes happen at runtime near the player (writer PC in a streamer/spawner) -> far rows empty only because not loaded -> raise that radius.
H-load-time: all row+2 writes happen at level load from hmp data -> data-limited, close lever, pursue LOD/fog.
Work: in a fixup patch, (1) record n and base at the 0x80041EF0 call; (2) log (PC-tag, row idx, value, VI) for every `sh ...,0x2(row)` in the functions found by grepping RecompiledFuncs for `sh .*0x2(` near lw 0x6FCC users (funcs_10.c lines ~3179-24992 list); simplest: wrap the 0x80136FCC-based stores. Run dd1 vs dd3 pinned (clone scratch/agent/s6480_pool.sh). Positive control: count of writes with value!=FFFF must be >0 at level load.
Outcomes: writes continue during flight -> H-streamer-bound; only at load -> H-load-time.
