Single next work unit (s5633): make the objective RNG deterministic-reproducible. Hypothesis R (s5632): bool[1..3] = randMod(3)+1 at 0x80102158; 0x64 fail arm needs bool[1]==1 && bool[7]==1.
Offline first: find what sets bool 7 (grep setObjectiveBoolean literals 0x7 / randMod-derived ids in funcs_43.c lv functions) and randMod's (0x800C77D0) seed source.
Then: env-gated override (fixup script, not hand-edit) forcing the randMod(3) result at the 0x7F site to 0 (id 1) vs 2 (id 3) within separate runs, queue soaks, positive control = [objbool] shows forced id. Expected: forcing id 1 (+ bool 7 path) reproduces the fail; forcing id 3 never fails.
HYPOTHESIS-ID: m6-mission-endurance
