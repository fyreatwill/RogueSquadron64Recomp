# NEXT: fold the s7126 apex soaks; name the escaping sheet-fan member's class, then fix it
HYPOTHESIS-ID: wsheet-escape
State (s7126): the s7125 w6 swap-7641 dark sky band is a real escape of the W_SHEET cull (8 fan tris with apex (994.8,-112) dropped, one
member drawn dark). Fan geometry refutes H-span (the escaper spans >> 200 px). Remaining:
  H-pos  : the escaper has all W > 0 (one near-zero W at the W-plane zero crossing next to the cliff edge): class P in ROGUESQ_W_KEEPLOG.
           The P class exists (s7126 k7: 59 kept P tris >= 150 px, max 666, W ratio median 0.0048).
  H-other: not a perspective tri (no keep line at all next to the drops): name the command (fill/rect/non-persp tri) from a stream.
Step 1 (no game run needed if the soaks ran): read scratch/agent/SOAK-RESULTS.md and scratch/s7126/apex_r{1,2,3}.txt.
  - Any 'P' hit in tools/s7126_apex.py output -> H-pos. Design the rule: drop (or clamp like M) a P tri that shares a vertex with a dropped
    tri in the same frame is not implementable per-tri in RT64; instead test a per-tri rule on the logged hits vs all P lines offline:
    e.g. W ratio < 1/256 AND span > W_SHEET_PX. Count how many of the ~150 kept P tris per run the rule would also drop (each is potential
    missing geometry: near-wall tris have large W range too). Land behind ROGUESQ_W_SHEET_POS=<ratio> with a W_SHEET_ALT-style same-run toggle,
    qualify on one owner-recipe L6 stream run (tools/s7126_arm.zsh, EVERY=1 FROM=7500) with s7122_fidelity.py: no new missing terrain.
  - Only 'M' or nothing, but a dark band is reported -> H-other: one stream run with tools/s7126_arm.zsh and decode the frame's commands.
  - 0 hits in 3 x 300 s: escape rate < 1 per ~54k swaps; write that as the bound, close wsheet-escape as rare, move to the next G3/G5 item
    in CURRENT-TRUTH Next steps.
Commands: python3 tools/s7126_apex.py scratch/s7126/apex_rN_keep.txt scratch/s7126/apex_rN_drop.txt ; python3 tools/s7126_keep.py ... --minspan 200
