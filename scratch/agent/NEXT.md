# Next work unit: do the free-list head/walk guard sites ever execute on the mission route?
HYPOTHESIS-ID: patcheslib-shadowed
s5368: on hangar 512, allocateDisplayListBuffer entry >=4096 but head (guard2) and walk (guard3) a100 sites = 0 incl. forced control. H1: sites dead on whole route (retire, document). H2: sites reached only in mission/other phase (then census 0x100 there).
Unit: no rebuild. Copy scratch/patchq/ab/run_a100.sh, lengthen sleep to ~300 and use the validated mission autopilot schedule (CURRENT-TRUTH/M5 plan keyed mission runs); grep `[a100-head]`, `[a100]`, `[a100-ent]` for allocDLBlockToFillRectList too. Outcomes: any head/walk line -> read mis count, name writer if mis>0; all 0 with mission reached -> H1, close thread.
