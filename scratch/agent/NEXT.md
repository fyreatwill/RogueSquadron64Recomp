# NEXT: G3c(a) fold s6352 soak (radfade2 at A6C0 AA74)
HYPOTHESIS-ID: g3c-owner-visual

s6352 built ROGUESQ_EDGE_FADE_R2=r0,r1[,xoff,zoff[,R,G,B]] at L_8004AA74 (the site s6314 proved darkens terrain; the s6325 B910 hook was the wrong write, s6327/6328). Soak scratch/agent/soak_queue/s6352_g3c_r2.sh: arm ctl (R2=0,1 + LOG) and arm log (LOG only); outputs scratch/agent/m6/g1_lvl1s6352_*.
Read: (1) ctl frames must be dark terrain (positive control; if not, wrong site again -> stop). (2) In the [radfade2] lines find the stack-word pair (w38..64 are callee sp+0x38..0x64) that is a world x,z whose radius d from cam*0.5 stays bounded (~<=24 at dd3, per s6324) and varies per vertex; set xoff/zoff to those offsets.
Then run arms R2=18,26,xoff,zoff (haze colour sky-ish e.g. ,200,215,235) vs none at dd3, compare far-edge frames (tools/g3c_edge_score.py) and send owner contact sheet. Phase-gate on VI, no cross-run A/B on animating frames.
H-fog-unscaled / H-cell-boundary / H-retail as before (s6305: footprint trapezoid edge, no haze ramp in retail => fade ring is a new feature, opt-in).
