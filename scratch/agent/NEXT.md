# NEXT (s7449)
HYPOTHESIS-ID: quiet-crash-passthrough

First: fold SOAK-RESULTS line for s7448_quiet_levels (L7/L12, harness under ROGUESQ_DIAG_QUIET=1). Pass = inits=1,
alive_at_end=1, vi_stalls30s=0, crashlines=0 both -> class DE second line.

Class DF: rs64_diag_keep (src/main/main.cpp) decides on the FORMAT string. A failure report whose keyword lives in an
argument (fprintf(stderr, "%s\n", buf) with buf="... SIGSEGV ..."; 9 "%s"-leading sites in src, e.g.
upstream_compat.cpp:9009) or in an unrouted path is either dropped under QUIET or never routed at all. QUIET must never
hide a crash.
Step 1 (offline): list every failure-report path: signal handlers (grep sigaction/signal( in src + lib/N64ModernRuntime),
ultramodern error/abort handlers, recomp unhandled-op / exit paths, assert macros, fputs/puts/write(2) sites; for each,
say: raw (write/fputs/(fprintf)), routed+keyword-in-fmt (kept), routed+keyword-in-arg (DROPPED = class member).
Step 2 (one run, positive control): a planted crash under QUIET. Find an existing fault-injection env (grep ROGUESQ_.*FAULT|
PLANT|FORCE_CRASH in src); if none, add ROGUESQ_PLANT_SEGV=<sec> (raise SIGSEGV on the guest thread at t=sec). Arms: default
vs QUIET=1, same plant; compare the crash report lines. Members: lines in default that QUIET loses.
Hypotheses: H-none (every crash path is raw or keyword-in-fmt), H-few (some "%s" crash lines dropped -> route via (fprintf) or
check the formatted text when fmt starts "%s"), H-unrouted (a handler bypasses stderr capture entirely - not a QUIET issue).
Discriminator: count of default-arm crash-report lines missing in the QUIET arm. Positive control: the plant must produce a
crash line in the default arm and crashlines>0 in m6-style grep.
