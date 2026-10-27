# Next: read s6325 radfade soak (4 arms) and judge far-edge frames
HYPOTHESIS-ID: g3c-owner-visual
Arms: nofade (maxr in [radfade] log), r18_26, r10_26, ctl (R=0,1 must blacken terrain = positive control). Logs under scratch/agent/soak_results/*s6325*, dumps under scratch/agent/m6.
Hypotheses: H-fade-dark (black ramp hides jagged edge) vs H-fade-fog (needs fog colour, black ring visible) vs H-edge-not-radial (corners remain).
Check ctl first; then compare far-edge rows nofade vs r18_26 vs r10_26; if edge is rectangular try haze colour via R,G,B args. Fold into ledger; make it default-on at dd>1 only if the owner approves.
