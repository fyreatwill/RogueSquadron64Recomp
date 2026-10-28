# NEXT: read the s6537 cap-arm soak results and pick a cap
HYPOTHESIS-ID: g1c-span-reject-predicate
s6537 built ROGUESQ_BYPASS_MAXCELLS (per-swap cap on force-accepted span-reject cells). Four soaks queued: scratch/agent/soak_queue/s6537_cap_{0,40,120,inf}.sh (logs in scratch/agent/m6/s6537_cap_*/ and soak_results/).
Work unit: after the loop runs them, extract per arm the [g1b] sd_wall ms/task and tasks/s, VI rate, crashes, and the fixed-camera terrain fraction (same scorer as s6528/s6536) from the fb dumps.
Outcomes: inf must reproduce ~127 ms / ~10.5 tasks/s (positive control; if not, the cap wrapper changed behaviour). cap=0 near opt-out (~55-65 ms) with terrain fraction ~0.047. If cost scales with cap while fraction gains saturate early -> choose that cap as dd>1 default (ROGUESQ_BYPASS_MAXCELLS default); if fraction is linear in cost, expose the knob and report the tradeoff to the owner with a contact sheet.
