# Next work unit: consume s5377_census_mission_retry soak result ([a5370] rows) from SOAK-RESULTS.md
HYPOTHESIS-ID: patcheslib-shadowed
s5377: title-boot SIGSEGV si_addr=0x58 = plume MetalFramebuffer ctor null texture (renderer-side, 1/7 launches, single-source). No guard landed (writer unnamed).
Next: (1) tail SOAK-RESULTS.md for s5377; if mission reached, read [a5370] rows in scratch/agent/soak_results/s5377_census_mission_retry/run1.log and fold into ledger. (2) If a title SIGSEGV recurs with the same pc-symbol, add a caller-naming null-check log in plume_metal.cpp ctor (export.sh + commit).
Outcomes: mission reached -> census data; allattempts-failed -> host/route flake, go BLOCKED with a question.
