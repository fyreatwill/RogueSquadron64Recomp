# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e dense-second tail, offline split first (no game run needed)
HYPOTHESIS-ID: g1e-dd4-dense-tail
s6962 closed g1e-dd4-commit-leaves: locked owner figure 58.4-60.0 fps on 4 arms (lvl1 16:9 60.0, lvl1 21:9 58.4, LEVEL=4 58.5, LEVEL=10 60.0), 0 crash.
The residual is a dense-second tail (p10 52-53 tasks/s on lvl1 21:9 and LEVEL=4) while sd_wall p50 is only ~9 ms, so a few frames exceed 16.7 ms.
Hypotheses: H-traffic (texel memory traffic: rs64LoadBlockRuns + hash read the same bytes twice) vs H-encode (RT64 recordFramebuffer/submitRasterScene
per draw call, AGX encode ~20%) vs H-burst (a few frames carry most of the cost: per-task ring shows a bimodal wall, not a shifted median).
Discriminator, offline: CALLER=submitRasterScene python3 tools/g1e_xt_leaves.py scratch/s6961/xt_x.xml (H-encode share), and
python3 tools/g1e_task_ring.py on the s6962 logs if they carry the ring (AQ=2 only: if not, one run with ROGUESQ_G1E_TRING=1 AQ=3 at LEVEL=4 16:9
dd4 windowed, tools/g1e_owner_quiet_arms.zsh, ARMS="4:t4:ROGUESQ_G1B=1+ROGUESQ_G1E_TRING=1+ROGUESQ_G1E_AQ=3+ROGUESQ_FORCE_SAVE_MISSION=4").
Outcome: top share names the next fix; if slow seconds are <3% of seconds and lat p99 < 50 ms, close G1e as done and take the next ladder rung.
Owner reports override all of this. Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE stay opt-in, owner decides.
