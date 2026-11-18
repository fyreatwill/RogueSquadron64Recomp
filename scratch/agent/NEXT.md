# NEXT (s7586)
HYPOTHESIS-ID: host-memory-growth-audit

s7585 found and fixed the in-flight growth (plume executeCommandLists wait-buffer autorelease leak, 1.39 -> 0.016 MB/s, same-binary
A/B). With that masking growth gone, finish class LK:
Hypotheses: H-flat (no per-load growth: footprint returns to the same level after each hangar re-entry), H-leak (each mission load /
hangar re-entry adds > ~5 MB that is never freed), H-slow (a small time-linear residual, e.g. the CFString +15k/210 s seen in both
s7585 arms, that matters only over hours).
Discriminator, one run each, build/ (fixed binary):
1. Hangar route: `env GD=build SECS=650 XE2="MallocStackLogging=lite DYLD_INSERT_LIBRARIES=$PWD/tools/s7585_leakplant.dylib" zsh
   scratch/s7585/hangar.zsh hc` with a side loop running `heap -s -q <pid>` at each hangar entry (grep [hangarmenu-a0-entry] in
   scratch/s7585/hc/cap/run.log, or fixed times ~150/330/480/600 s), then tools/s7585_heapdiff.py between consecutive entries.
2. Long hold: `env R=scratch/s7586/L HOLD=1200 ALLOW_SLOW=1 ARMS="4:l4:MallocStackLogging=lite" zsh tools/g1e_owner_quiet_arms.zsh`
   with heap -s at 120/600/1150 s (copy scratch/s7585/runC2.zsh, change the times). Plant control: leaks must report it (>= 39 MB).
Outcomes: per-entry delta > 5 MB in one class -> H-leak, name it from the heap label and fix; residual slope > 0.05 MB/s over 1200 s
-> H-slow, name the class; both small with the control firing -> class LK CLOSED.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
