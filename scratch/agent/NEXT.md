# NEXT: G3c(a) fold s6448 edge soak, compute stair-step metric
HYPOTHESIS-ID: g3c-visual-defects
Queued scratch/agent/soak_queue/s6448_g3ca_edge.sh (arms: retail, dd2, dd3, asp169, fps60; pinned pose; FB dumps in scratch/agent/m6/g1_lvl1s6448_*/fbd).
Hypotheses: H-optin (dd/auto-far exposes grid boundary; haze not scaled) vs H-aspect (frustum x-widening) vs H-retail.
Next: read SOAK-RESULTS tail; write scratch/agent/edge_metric.py (per-row terrain-vs-sky boundary x-run lengths, using retail as positive control: dd3 should have longer/blockier runs if H-optin); contact sheet for owner; then fix (scale fog/haze by dd or fade outer cells).
