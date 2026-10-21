# NEXT: [mtm] hook v2 - host backtrace on a0==2
Edit tools/apply_s5748_mtm_log.py BLOCK: when U32(ctx->r4)==2 also call backtrace()+backtrace_symbols_fd(STDERR) (include <execinfo.h>); regen path via fixup (apply is idempotent on TAG - bump TAG to s5749). Build, rerun s5748 recipes as s5749_mtma/b.
Control: a0=1 lines still print. Discriminator: backtrace frames name the a0=2 caller (checkComplexObjectives/setHudEnableBit4 => bool arms; other => H2). If still no a0=2, the fail needs another route: find which route produced the original arg-2 observation (grep s5470 in PORTING-STATE).
HYPOTHESIS-ID: g1-nonhealth-fail
