# NEXT: who populates the material-link table rows (0x80136FCC, halfword+2)? Is it bounded to the retail radius?
HYPOTHESIS-ID: g1c-dd8-limit
Established (s6479): pass cells/window dd1 75 vs dd3 36, entries 2.5x, cell ptr extent identical -> widening adds only link==0xFFFF cells.
H-streamer-bound: link halfwords are written by a loader/streamer limited to the retail cell radius (far rows empty because never loaded) -> raise that radius.
H-truly-empty: far terrain has no material at all in level data -> lever closed, pursue LOD/fog.
Work: grep fixups/recompiled funcs for stores to table 0x80136FCC rows (ld of 0x80136FCC base, sh to row+2); write-watch (RS64_S5798_ST style) for those stores, log writer PC + row index + time at dd1 vs dd3; compare count of rows with link!=FFFF vs count reachable. One build, one run.
