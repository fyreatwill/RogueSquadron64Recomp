Single next work unit: copy scratch/agent/s5578_plume_nolldb4.sh, add
ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 to COMMON (the s5463 title8
recipe has them), and make the per-second poll cheap (grep -c on tail, logs reach 70 MB/120 s).
Run as a soak_queue recipe (N=4, run in the loop, not interactively - 600 s tool cap).

H1: LLE trio reaches title (origin 0x00790400) in most attempts -> then run under lldb to catch the plume SIGSEGV (si_addr=0x58).
H2: LLE trio also stays at 0x696100 -> a regression in the title route since s5463; bisect.
H3: title reached but plume never recurs in N -> raise N.
Discriminator: per-attempt title count with the LLE trio (control: s5463 logs had titles).

HYPOTHESIS-ID: m6-title-plume-lldb
