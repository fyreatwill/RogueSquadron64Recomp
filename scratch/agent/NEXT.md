# NEXT: fold g1_lvl15b..18b; root-cause stale cinematic shared by levels 10 and 15

HYPOTHESIS-ID: g1-mission-coverage-sweep

Read new SOAK-RESULTS lines (15b,16a/b,17a/b,18a/b). If another level shows nomission with
curOvl=1 cineState=F7B80040 it is a class. Then diff the level-10/15 `[phase]` rows against
level 11 (m6/g1_lvl11a/run.log) around the first cineBody transition and find who leaves
cineState=F7B80040 after section-4 DMA. H1 level-table entry for 10/15 carries a cinematic
flag; H2 our DMA/overlay copy skips a reset; H3 cinematic is legit and needs a skip key.
Discriminator: a retail-oracle/level-table read of entries 10 and 15 vs 11.
