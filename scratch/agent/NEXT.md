# Next work unit
HYPOTHESIS-ID: m3-unclosed-idiom-census
Goal: finish the M3 census. s4975 closed 64-bit mul/div, s4976 closed ldc1/sdc1 alignment (tools/census_fpmem_sites.py).
Remaining: mfc1/dmfc1 width, sltiu sign-extension, jr with non-ra register. Do all three in ONE script/iteration (iron rule 14).
Method: grep-count sites in /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs, classify real vs data-as-code (neighbouring .word/INVALID), check emitted C semantics, measure host-behaviour claims.
Outcomes: unguarded reachable defect -> guard in fixup script; all benign -> close in CURRENT-TRUTH, then REVISIT retail-entry boundary with a new angle.
Do not re-run VI-640 soaks.
