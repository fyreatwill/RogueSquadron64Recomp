# NEXT (s7466)
HYPOTHESIS-ID: host-null-deref-audit

s7465 closed DS (flight H-const, control PASS) and ran class DT (tools/s7465_nullderef_census.py --controls rc 0; 1 guard in
rt64_framebuffer_renderer FillRect, 10 classified). Queued scratch/agent/soak_queue/s7465_dt_guard_flight.sh (L4 + L12 dd4 HOLD=150).

Step 1: fold s7465_dt_guard_flight from SOAK-RESULTS.md + scratch/s7465q/s7465.txt.
  - both arms alive, 0 crash/stall -> one line under CURRENT-TRUTH item 1 DT ("soak PASS"); fillrect_null>0 is a datum: the
    both-null storage IS reached, name the framebuffer key (add key logging to the guard) before calling it closed.
  - dead arm -> backtrace from log_<arm>.txt, root-cause.
  - not yet run / void -> do Step 2 meanwhile.
Step 2 (new slug host-analyzer-rest): class DV, the remaining clang static-analyzer families on the same 150 TUs that DS/DT did
  not cover (unix.Malloc / cplusplus.NewDelete use-after-free & double-free, core.DivideZero, core.UndefinedBinaryOperatorResult
  shifts, alpha.security.ArrayBound off). Copy tools/s7465_nullderef_census.py, widen the regex to those checker names, plant one
  control line per family, classify every site (FP with invariant, or fix with an ORIGIN: line).
