# NEXT (s7447)
HYPOTHESIS-ID: direct-stderr-bypass

Class DD (CURRENT-TRUTH Next steps item 1, new idiom-class audit after the CZ-DC default-diag campaign closed s7446).
Idiom: hand-written `fprintf(stderr` in src/main/*.cpp + src/rsp/*.cpp (1468 sites) that do NOT go through rs64_diag_fprintf
(main.cpp), so ROGUESQ_DIAG_QUIET=1 cannot drop them and the game thread pays the libc lock itself.
Step 1 (offline census, tools/s7447_stderr_sites.py): classify every site by kind: one-shot (static flag / lambda init),
crash/abort breadcrumb, env-gated (getenv/latch dominates), counter-budgeted (n++ < K), UNGATED-RECURRING (none of these).
Step 2 (runtime, one run): env S7431_ARM=DD zsh tools/s7431_stderr_volume.sh 150 - map every tag that fired in the default arm to
its site; ungated-recurring sites that fired = the class members.
Hypotheses: H-clean (every recurring direct site is already gated or rate-capped -> close the class with the census),
H-hidden (some ungated-recurring sites fire in owner flight -> route via rs64_diag_fprintf or latch, consumer control restores),
H-dead (the ungated-recurring ones never fire in owner recipe -> document, no change).
Discriminator: count of UNGATED-RECURRING sites that fire in the default arm (0 -> H-clean/H-dead; >0 -> H-hidden).
Positive control: the s7431 [fbhash planted tag (ROGUESQ_FB_HASH=1) must classify PERSISTENT in the same run.
