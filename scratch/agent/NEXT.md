# NEXT: which insert writer populates grid-cell link chains, and does it carry a player-distance radius?
HYPOTHESIS-ID: g1c-dd8-limit
Known (s6481): row+2 links in the pool at *0x80136FCC are written at runtime in flight by 16 PCs; dominant non-FFFF writers 0x800487F8, 0x8004B56C, 0x8004805C, 0x80047668, 0x80047EA0/47F50; unlink-like 0x80048EB8, 0x8004B594, 0x80047064.
H-radius: an insert writer's caller gates on a distance from the player cell (constant or table) -> scale it by DRAW_DISTANCE and far cells get chains.
H-object-bound: chains are the objects (enemies/props) placed in each cell; far cells are empty because no objects exist there -> terrain strips come from another source; close this lever, pivot to L-lod/fog.
Work: read generated code of the funcs containing 0x800487F8 and 0x8004B56C and their callers (grep RecompiledFuncs); extend apply_s6481_poolwatch to log the caller RA/a0..a3 for those PCs at dd1; then a one-site lever probe (widen radius x3 at that site, ROGUESQ env) and check [exitlog] pass count + terrain fraction at dd1 vs lever.
Outcomes: radius found and widening raises passes -> H-radius, bundle under DRAW_DISTANCE; no distance gate -> H-object-bound.
Build note: vendored fixup refuses a 2nd run on the live tree; apply new apply_*.py helpers to live files with a one-off driver (see s6481) and also wire them in fixup_game_funcs_vendored.py.
