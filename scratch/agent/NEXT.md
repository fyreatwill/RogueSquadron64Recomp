# NEXT (s7456)
HYPOTHESIS-ID: soak-verdict-line-fields

Class DL (offline + fake-recipe controls): the loop's SOAK-RESULTS verdict line (tools/agent/loop.sh:344) records only the
recipe's rc. CURRENT-TRUTH says "read alive_at_end / crashlines, never rc", yet every fold since s7406 had to open the
soak log by hand to get them, and s7449 rc=1 (benign mission re-init) read like a failure until a session dug it out.
Step 1: census SOAK-RESULTS.md lines since s7400: for each, does rc agree with the recipe's own per-arm summaries
(m6/<tag>/summary via tools/agent/summary_field.sh: alive_at_end, crashlines, vi_stalls30s, exitrc)? Classify agree /
rc-false-fail / rc-false-pass.
Step 2 (if any disagreement or always, cheap): loop.sh appends to the verdict line `fatal=<n>` from
tools/agent/fatal_scan.sh over the soak log, plus `arms=<k> alive=<a>/<k>` from `== arm` summary lines the recipe printed
(no recipe change needed: recipes already cat $D/summary into the log). Test in tools/agent/test_soak_idle_gate.sh with fake
recipes: one with a planted fatal line + rc=0 must show fatal>=1, a clean rc=1 recipe must show fatal=0.
Hypotheses: H-agree (rc always matched the summaries: fields are convenience only), H-few (1-3 mismatches), H-many.
Discriminator: mismatch count in Step 1.
