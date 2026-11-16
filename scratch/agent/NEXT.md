# NEXT (s7457)
HYPOTHESIS-ID: soak-recipe-summary-coverage

Class DM (offline + fake-recipe controls). s7456 made the loop's verdict line carry per-arm fields from the recipe's `tag=`
summary lines; a recipe that prints none shows `arms=0` and is scored on rc alone (60 historical runs). Question: which LIVE
recipe generators/templates (tools/*.zsh|sh|py that write scratch/agent/soak_queue/*.sh, tools/agent/m6_mission_tmpl.sh.in,
m6_god_common.sh callers, g1e_level_fps.py / g1_objective_response_run.py launchers) emit a soak whose log carries no `tag=`
line, or a `tag=` line missing alive_at_end / crashlines / vi_stalls30s?
Step 1: census (grep the generators; run each template's summary path against a fake binary where one exists, as s7453 did
with tools/s7453_harness_death_test.zsh). Classify: full-summary / partial / none.
Step 2: for partial/none live generators, emit a standard `tag=<name> alive_at_end= crashlines= vi_stalls30s=` line
(from fatal_scan.sh + the generator's own alive check). Test with fake recipes that the loop's verdict shows arms>=1.
Hypotheses: H-none (every live generator already prints one: arms=0 runs are all retired one-shots), H-few, H-many.
Discriminator: count of live generators classified partial/none in Step 1.
