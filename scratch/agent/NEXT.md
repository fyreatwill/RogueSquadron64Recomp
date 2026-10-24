# NEXT: G1c phase 2 - fold the s6086 arena soaks
HYPOTHESIS-ID: g1c-phase2-drawdist

Context: s6086 built ROGUESQ_BIGARENA=1 (scaled terrain pool diverted to a bump arena at 0x80800000; tools/apply_s6086_bigarena.py). Three L1 soaks are queued: s6086_ctl_px4_dd3_noarena, s6086_arena_px4_dd3, s6086_arena_px8_dd4.

Work unit: fold them.
  tail -5 scratch/agent/SOAK-RESULTS.md
  grep -a "bigarena\|mallocnull\|heaplog.*-> 00000000\|CRASH\|SIG" scratch/agent/m6/*g1cs6086*/run.log | head -40

Competing hypotheses and what each outcome proves:
- H-heap (pool crowds the 8 MB heap): control shows [mallocnull]/crash (positive control, as s6062) AND arena arm shows [bigarena] line with 0 NULLs and rc=0 -> heap was the binding limit; move on to the next limit (ucode cap, 64-wide stride s6035, RSP cost).
- H-guard (>=0x80800000 pointer guards treat arena ptrs as null): arena arm crashes or behaves wrongly with no mallocnull -> get an lldb backtrace, find the guard, widen it in the fixup scripts (not by hand-editing generated code).
- Control does NOT fail: no positive control, so the arena result means nothing; rerun the control before concluding.

Then: score terrain fraction with tools/g1c_fixed_score.py (reference dd1 0.085, dd2 0.074) and build a dd1-vs-max contact sheet for the owner. Default stays retail.
