# Next work unit: exercise the heap-guard fire control, then close the census
HYPOTHESIS-ID: heap-guard-need-census
Regen (make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake; DEVELOPER_DIR as in CLAUDE.md), then run the s5033 recipe with ROGUESQ_FORCE_ALLOC_TAIL_GUARD2=1 added (copy scratch/agent/soak_queue/done/s5033*.sh to a new soak_queue name).
Outcomes: [alloc-tail-guard2] lines appear -> the s5033 zero is a valid null (promote to two-source, close census). No lines -> the instrument/site is dead or not on route; fix before trusting the null.
