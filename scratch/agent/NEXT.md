# Next work unit

HYPOTHESIS-ID: m3-idiom-class-audit

s4813 closed the integer-divide class (docs/M3-S4813-DIV-CENSUS.md). All M3 idiom classes are now closed.
Next: pick one of (a) float-to-int conversion class (TRUNC_W_S 1171, TRUNC_W_D 28, CVT_W_S 13, CVT_W_D 2 sites in recomp.h macros): check NaN/overflow semantics vs MIPS (0x7FFFFFFF) and whether any site feeds an address/index; classify, guard or prove benign. (b) otherwise M5 passive items.
Must commit a tool/doc/guard with an ORIGIN line.
