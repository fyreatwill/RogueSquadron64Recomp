# NEXT (s7455)
HYPOTHESIS-ID: harness-summary-field-match

Class DK (offline + synthetic controls): summary pass checks done as prefix greps on `key=N` fields.
Datum (s7454): recipes check `grep -q 'inits=1' $D/summary`, which also passes inits=10..19; `crashlines=0` is safe only
because the field is last-but-one and digits follow. Any `key=N` check without a terminating boundary can false-pass.
Step 1: add tools/agent/summary_field.sh <summary> key op value (op = eq|le|ge), exact field parse (split on spaces, key=),
exit 1 on missing field. Controls: synthetic summary with inits=12 must FAIL `inits eq 1`, mission_restarts=0 must PASS
`mission_restarts eq 0`, missing field must FAIL.
Step 2: census every live template/launcher (scratch/agent/*.zsh|*.sh not in done/, tools/*.zsh|*.sh, tools/agent/*.sh)
for `grep -q '<key>=<digits>'` and `grep .*=0` style checks on summary files; classify each as boundary-safe or prefix-hazard;
switch hazards to summary_field.sh. Document the helper in ITERATION.md's soak-queue section so new recipes use it.
Hypotheses: H-none (0 live hazards: helper only), H-few, H-many. Discriminator: hazard count in live templates.
If H-none, close in one session and take the next ITERATION.md 3c rung or a new idiom-class audit (CURRENT-TRUTH item 20).
