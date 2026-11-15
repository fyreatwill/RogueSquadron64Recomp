# NEXT (s7369): TSan arm crawl at the post-fix 1024-wide scene + 3 unclassified TSan rows
HYPOTHESIS-ID: tsan-arm-1024-crawl
Context (s7368): DL-chunk pool NULL fixed (DLPOOLX armed at the game's first pool rebuild, default on). TSan t1/t2 (scratch/s7368)
now reach the 1024-wide scene (217-254 s) and then crawl: fs +1 per 600-VI stall-dump, states alternate 5,1/1,5, vflag 0.
Hypotheses: H-slow (pure TSan cost of a heavy scene: fs rate ~0.1/s is just slow), H-cycle2 (a second guest wait cycle that only the
stall-dump's own action breaks: fs advancing exactly once per dump is suspicious), H-starve (one guest thread starved by host scheduling).
Discriminator (one run, no rebuild): `env SAMPLE_AT=330 zsh scratch/s7366/tsan_run.zsh ../s7369/c1 420 "ROGUESQ_S4259=1
ROGUESQ_G1E_TL=$PWD/scratch/s7369/tl_c1.bin"`, then tools/s7367_vi_deadlock.py on the TL ring: if frames advance between dumps at
a low steady rate -> H-slow; if every fs step coincides with a stall-dump -> H-cycle2 (name the waits like s7367); compare the
sample's guest thread stacks for H-starve. Also hand-classify the 3 `?` rows in scratch/s7368/t1_tsan_report.txt (g_s6127_rd /
g_s6127_flags / rs64_s5042_poison from rs_malloc/rs_free on guest threads) into tools/s7354_tsan_report.py's table.
Exit: PORTING-STATE s7369, CURRENT-TRUTH 27zh (it is at 59.9 KB: the next iteration may be maintenance), commit.
