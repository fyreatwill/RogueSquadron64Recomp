# Next work unit: identify the static cycle in the flown hold
HYPOTHESIS-ID: m6-mission-endurance

s5419: flown hold clean but fbhash from ~sample 23479 (~730 s) cycles 656a759fda9783b9 (~2217 samples) / ef16afe604546361 (~570) x4.
Hypotheses: (H1) player died / mission ended -> results/retry screens loop; (H2) game hung but VI keeps scanning a stale buffer; (H3) pause/menu opened by autopilot 'r'/'a' mash.
Discriminator: rerun scratch/agent/m6_flown_hold.sh (tag s5419_b, 1200 s, run_in_background, one game at a time) with a screenshot or fb dump (look for an existing ROGUESQ_FB dump flag) when fbhash first shows 656a759f; also log whether game-thread frame counters advance (H2 vs H1/H3). Positive control: a dump of a known-animating frame in the same run.
Also check whether the cycle onset time repeats in run B (determinism); the unflown s5418 holds never entered it (maxrun 317).
Outcomes: H2 -> lldb backtrace of hung threads, root-cause fix; H1/H3 -> change pattern to avoid death/'r', re-run.
