# NEXT (s7383)
HYPOTHESIS-ID: host-atomic-ordering

s7382 closed class AX (thread QoS): hot threads [Game]/Gfx at DEFAULT QoS by default, raised by QOS_ALL=1; default is the
owner's call (CURRENT-TRUTH item 4). Census tools/s7382_thread_qos_census.py --check rc 0.

Work unit: class AY, every host std::atomic (and volatile used as a flag) in src/main, src/rsp, lib/rt64/src/{hle,render,common},
lib/N64ModernRuntime/{ultramodern,librecomp}/src whose load/store/RMW uses an explicit memory_order weaker than seq_cst, plus every
plain `volatile` cross-thread flag. Per site: the atomic, its order, and whether it PUBLISHES non-atomic data to another thread
(store-release / load-acquire needed) or is a pure counter/stat (relaxed fine).
Hypotheses: H-ordered (every publishing pair already uses release/acquire or seq_cst, or a mutex covers the data),
H-relaxed-publish (a relaxed store/load pair hands off non-atomic data: benign on x86, a real reorder on arm64 = this Mac),
H-volatile (a volatile flag used for cross-thread handoff: no ordering at all on arm64).
Discriminator: census tool tools/s7383_atomic_order_census.py (--check exits 1 on an unreviewed publishing row; --controls:
a planted relaxed store followed by a plain-data read on another function must classify PUBLISH-RELAXED; a planted fetch_add stat
counter must classify COUNTER). For every PUBLISH-RELAXED / volatile-handoff row: fix to release/acquire (env gate not needed for
ordering-only changes if TSan stays clean), then a TSan arm (tools/build_tsan.sh, ROGUESQ_S7354_RACE_CTL=1 control must report)
over the s7326 route, plus a smoke run of `env SECS=200 zsh scratch/s7326/run.zsh s7383_smoke ''` (crash=0).
Expected: H-ordered -> close with the table; H-relaxed-publish / H-volatile -> fix list with TSan before/after.
