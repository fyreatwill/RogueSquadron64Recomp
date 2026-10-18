# Next work unit: classify title-boot SIGSEGV (si_addr=0x58) from bisect run4.log, then rerun s5371 mission census with retries
HYPOTHESIS-ID: patcheslib-shadowed
s5376: interactive hangar 3/5 (5/7 with s5375); soak 0/2. Route flaky: try4 never reached title (SIGSEGV si_addr=0x58, 37 CRASH lines), try5 missed hangar.
Next: (1) read stack in scratch/agent/soak_results/bisect_RogueSquadron64Recomp/run4.log (rerun bisect n=5 if lost) - name the faulting function/idiom. (2) Modify soak_queue/s5371_path_census_mission.sh to retry up to 4 launches until hangar, then read [a5370] rows.
Outcomes: known idiom -> guard class; unknown -> only act if an idiom-class audit applies.
