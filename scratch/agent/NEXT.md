# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e dd4 16:9 sync per-task tail split (the s6944 "per-task split not taken")
HYPOTHESIS-ID: g1e-dd4-task-tail
g1e-present-drain CLOSED s6953 (34 stays; 28 overdrains). Remaining G1e item 7 cost: slow seconds (p10 ~56 tasks/s) are denser
frames on the Gfx thread (+1.1-1.6 ms/task, s6944, per-second grain only).
Hypotheses: H-ucode (slow tasks are ucode-heavy: more vertices/tris -> factor5_ucode time) vs H-submit (rsp_dpc_submit/record per
call dominates: call count +16-23%) vs H-rt64 (RT64 remainder: draw-call build / TMEM loads) — discriminator: ONE per-task ring
(task ms, ucode ms, submit ms+calls, rt64 ms, tri count) over a windowed dd4 16:9 flight; regress task ms on each term over the
slowest 10% vs median tasks. Positive control: the per-task sum must match sd_wall within 5%.
Check first what tools/g1e_tail_split.py and the existing [g1e] per-second lines already carry (boring first) before adding fields.
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
