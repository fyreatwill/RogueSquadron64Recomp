# NEXT (s7451)
HYPOTHESIS-ID: harness-death-exit-status

First: fold SOAK-RESULTS line for s7450_fatal_harness (arm P L1 ROGUESQ_PLANT_EXIT=110 KIND=quick; arm C L4 clean).
Pass = VERDICT rc=0: P alive_at_end=0 crashlines>=1 exitrc=1; C alive_at_end=1 crashlines=0 exitrc=held vi_stalls30s=0.
If P shows exitrc=held or crashlines=0, the m6_god_common.sh wait/exitrc wiring is wrong (fix, re-queue).

Class DH (silent fatal exits): s7450 showed a `_Exit(1)` with no text scores 0 in every grep; only alive/exitrc see it,
and only the m6 harness records exitrc. Step 1 (offline, one pass): enumerate every exit( / _Exit( / quick_exit( / abort(
call in src/ and lib/N64ModernRuntime/{librecomp,ultramodern}/src (21 raw matches at s7450, grep -rnE '\b(exit|_Exit|quick_exit|abort)\(').
Classify each: (a) prints a tools/agent/fatal_patterns.txt line on stderr/stdout before exiting, (b) prints a line that
no pattern matches, (c) silent, (d) normal shutdown (SDL quit, EXIT_SUCCESS) - not a fatal.
Step 2: members = (b)+(c). Fix: either add their text to fatal_patterns.txt (b) or a one-line "[FATAL] <site>" stderr print
before the exit (c) (no lib/ edits without export.sh + commit). Positive control: ROGUESQ_PLANT_EXIT KIND=silent must score
fatal=0 before and the new [FATAL] line must not apply to it (it is a plant, not a site) - so add KIND=site that calls one
real (c) site's wrapper if one exists, else report the counts only.
Hypotheses: H-none (every fatal site already prints a matched line), H-few (a handful of (b)/(c) sites), H-many.
Discriminator: the (b)+(c) count from the classification table.
