# NEXT (s7545)
HYPOTHESIS-ID: class-ge-thread-state-fidelity

Fold first: SOAK-RESULTS lines for s7540_rwait_cost (voided 4/5 on battery as of s7544). If it voids out (5/5), rerun in-session with
ALLOW_SLOW=1 ALLOW_BATT=1 and score in-run only (tools/g1e_level_fps.py).

Work unit: class GE runtime witness. s7544's static census (tools/s7544_ge_census.py) found 0 guest accesses to OSThread fields, but
it only resolves constant addresses (+ the service-worker fns) and direct calls. Close that limit at runtime, one build:
- Track live OSThread guest addresses: osCreateThread adds [t_, t_+0x30), osDestroyThread removes (host side, a small array under a
  mutex or an atomic bitmap; ~20 threads).
- Hook guest loads (RS64_S7484_LD in tools/apply_s7484_loadwatch.py / rs64_s7484_load in src/main/upstream_compat.cpp; it is gated by
  g_rs64_s7484_on, check how to arm it without the UAF machinery, or add a sibling gate ROGUESQ_S7545_THRWATCH=1) and guest stores
  (RS64_S5798_ST) for addresses inside a live thread range. Log `[s7545] thr-access pc=.. addr=.. thr=.. off=.. kind=L|S w=..`, first
  64 per pc, counts per (pc, off) at exit.
- Positive control ROGUESQ_S7545_PLANT=1: once in mission, a guest-path read via the same hook function of thread 0x8010FF70+0x10
  (call the hook exactly as a generated load would) -> must log.
Hypotheses: H-none (0 hits with the plant caught: GE fully closed), H-reader (a guest pc reads state/queue/flags/id: classify vs the
port's enum values; if it branches on them, fix the port's stored value with an =0 knob), H-ctx (a guest store lands in 0x20..0x2F,
the host context pointer the port keeps in guest RAM: that is a crash risk, name the writer).
Arms: L1 dd1, L4 dd4, L12 dd4, 220 s holds each (tools/s7484_uafload_recipe.zsh shape), all in one run sequence.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
