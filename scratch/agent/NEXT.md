# NEXT (s7427)
HYPOTHESIS-ID: env-policy-order

First fold any new scratch/agent/SOAK-RESULTS.md lines.

Class CJ (CURRENT-TRUTH Next steps item 1): s7426 (class CI) found the documented defaults match the code (one presence-test
bug, DD_UNSAFE, fixed). Its ORDER check only covers FILE-SCOPE static latches. Open: main() applies env policy in a sequence
(QOS_ALL loop, rs64_s7358_sanitize_env, rs64_g1d_apply_aspect_policy, rs64_g1c_apply_dd_policy, the ASPECT/FB_WIDTH/OSMEM
setenvs at main.cpp ~12470-12710), but code runs BEFORE that sequence: s7354_race_ctl_start, s7382_qos_start, s6979se::init
(threads), and C++ static constructors in librecomp/ultramodern/rt64. Offline:
1. List every policy target (tools/s7426_env_defaults.py policy_vars(), 36 vars: literal setenv + the QOS_ALL name loop) and every
   setenv(...,1) overwrite in main.cpp. For each overwrite: is it sanitising (s7358) or guarded by "no explicit user value"? An
   unguarded overwrite of a user-set value = drift.
2. Build a call graph slice: functions reachable from the pre-policy calls in main() and from global constructors (any
   `static T x = f()` / `[]{...}()` at file scope, or __attribute__((constructor))). Any function-local static latch of a policy
   var reachable from there latches before the policy = drift (the s7030 kind, but not at file scope).
3. Policy order inside main: a policy step that reads a var another step sets LATER (e.g. dd policy reading ASPECT/FB_WIDTH
   before aspect policy sets them) = drift. The s7258 rs64_s7258_merge_reinit() exists because of such a latch: find its siblings.
4. Positive control: planted function-local static latch of ROGUESQ_OSMEM_MB called from a planted pre-policy call, and a planted
   unguarded setenv("ROGUESQ_ASPECT", x, 1) must both be flagged.
Hypotheses: H-ordered (every policy var is read only after its setenv, every overwrite guarded) vs H-race (>=1 reader latches
before the policy or one policy step reads a value set by a later step; then name who: owner recipe or test-only, and fix).
Write tools/s7427_env_policy_order.py. Exit 0 = ordered, 1 = drift, 3 = control failed.
