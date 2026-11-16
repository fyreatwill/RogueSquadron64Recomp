# NEXT (s7422)
HYPOTHESIS-ID: apply-idempotence-window

Class CE (CURRENT-TRUTH Next steps item 1): windowed idempotence checks in apply/fixup scripts. s7421 found 4 scripts
(s5787/s5790/s5791/s5809) whose "already applied?" test looked for the tag only in a fixed window after the anchor, so a second
call (inline fixer + RS64_REPLAY) after another block landed at the same anchor applied them twice in a regen. Fixed + tested
(tools/s7421_idem_test.py). Enumerate the whole idiom class:
1. `grep -lE "in (text|t|s|src)\[[a-z]+ *: *[a-z]+ *\+ *[0-9]+" tools/apply_*.py tools/fixup_*.py` (13 at s7421) plus any
   `find(TAG, k, k + N)` / `TAG in x[a:b]` variants. Classify each: SAFE (called once in the chain, or window covers every
   possible interposer), DOUBLE (called twice: inline fixer + RS64_REPLAY list in fixup_game_funcs_vendored.py), AT-RISK.
2. Extend tools/s7421_idem_test.py to every DOUBLE/AT-RISK script; fix to a whole-body check.
3. Remaining regen>live tag counts after the s7421 fix: s5856 (apply_s5835_sphere_probe.py, checkTrackedNpcProximityForCue) and
   s6497 (apply_s6496_bin_inputs.py, binPolygonIntoTerrainGrid). Explain each.
4. Second line: full regen replay (cp -R /tmp/s7420/front X; tools/regen_replay.sh X; tools/regen_verify.sh X out) then
   tools/s7421_regen_drift.py ... --control rc 0 and the PATCH-tag census (s7421 PORTING-STATE entry): no regen>live tag left.
   If /tmp/s7420/front is gone, regenerate with tools/regen_front.sh.
Hypotheses: H-once (every remaining windowed script is applied once: 0 DOUBLE) vs H-double (>=1 doubles in a regen).
Control: the HEAD copy of a fixed script must double under the interposed-block test.
