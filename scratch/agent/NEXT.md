# Next work unit: port patch-only guard predicates into fixup-inlined allocateDisplayListBuffer
HYPOTHESIS-ID: patcheslib-shadowed
Finding (s5367): patch block_ok/bump_cursor_ok are stricter than inlined guards (0x100 alignment, end bound, bump cursor). H2 supported by source reading only.
Unit: in tools/apply_s3285_freelist_align_cycle.py add a counter-only (non-rejecting) check for (addr&0xFF)!=0 on free-list node pointers; positive control = same counter on a deliberately always-true predicate; run one autopilot hangar run (scratch/patchq/ab/run_ab.sh recipe). If count>0, make it reject and name the writer (ORIGIN). If 0, retire the patch layer as dead.
