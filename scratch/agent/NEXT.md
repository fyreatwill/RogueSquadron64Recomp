# Next work unit: hangar entry-frame DL byte dump, retail vs port (first gfx task at VI 512)

HYPOTHESIS-ID: hangar-artifact-triage

s4507: first gfx task at VI 512 is data_ptr 0x80738F18 on both retail (oracle) and port. Later buffer rotation differs (timing-dependent, unqualified).
Hypotheses: H1/H3 port renderer/ucode (identical source bytes, bad pixels); H2 guest data bug (source bytes differ).
Discriminator: dump phys 0x738F18..+0x4000 at the first VI-512 gfx task on both sides, byte-diff. Control: first VI-1024 gfx task, expect identical.
Port: env-gated dump in the ROGUESQ_LOG_TASKSUBMIT hook (src/main/upstream_compat.cpp ~2520) for the first gfx task after vi_width=512 (and 1024 for control); rdram is byte-swapped (^3).
Retail: PC-triggered memory dump in tools/oracle/rs64_oracle.c (extend the --pc-task-dump handler ~line 1572) writing bytes at data_ptr.
Build both arms in one iteration, run one at a time. Recipes: scratch/agent/s4507_oracle_gfxtask.sh, s4507_port_hangar.sh. SIGKILL.
