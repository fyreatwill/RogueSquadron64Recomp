# Next work unit
HYPOTHESIS-ID: m3-unclosed-idiom-census
Goal: finish the census of M3 idiom classes not yet in CURRENT-TRUTH's closed list. s4975 closed 64-bit mul/div (tools/census_d64_sites.py).
Remaining: COP1 ldc1/sdc1 alignment (grep generated code for ldc1/sdc1 emitters + MEM_D helper), CVT_W_S/CVT_L_S rounding-mode use vs FCSR, mfc1/dmfc1 width, sltiu sign-extension, jr with non-ra register.
Method: grep-count sites per class in /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs, classify real vs data-as-code (use the s4975 script pattern), measure any host-behavior claim rather than assuming.
Outcomes: unguarded reachable site -> guard in fixup script; all benign -> close in CURRENT-TRUTH, then resume backlog (renaming is exhausted; consider REVISIT of retail-entry with a new angle).
Do not re-run VI-640 soaks.
