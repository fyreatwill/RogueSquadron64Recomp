# Next work unit: find why the hangar route no longer reaches VI 512 (s4276)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4275: both WRAP_FLUSH arms failed to reach VI 512 (arm0 died at VI 640, arm1 reached 1024 at 50.7 s).
Hypotheses: R1 added env (S4271/S4272) perturbs the route; R2 build regressed (KEEP_PIPE / private-DMEM defaults); R3 VI-640 crash flakiness (~2/13 pooled).
Discriminator: run the s1949 recipe verbatim (scratch/agent/soak_queue/done/s1949_*.sh) 3 times with S4271/S4272 unset vs set; count runs reaching 512.
Only after >=2/3 reach 512, re-run scratch/agent/s4275_ab.sh and decide the WRAP_FLUSH default.
