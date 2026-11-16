# NEXT (s7448)
HYPOTHESIS-ID: quiet-harness-markers

First: fold SOAK-RESULTS line for s7447_route_levels (L4/L7/L12 120 s flight, build with include/rs64_diag_route.h). A crash
there that the s7447 150 s lvl1 runs did not show -> suspect the lib TU recompile (RS64_DIAG_ROUTE=OFF arm to split).

Class DE: since s7447 ROGUESQ_DIAG_QUIET=1 drops every non-crash diagnostic line, including markers the harnesses wait on
([initMission] from generated C makes g1_level_coverage_common.zsh MISSION_INIT=1 time out). QUIET is the cheapest owner-like
logging arm, so it should be usable in every harness.
Step 1 (offline): grep tools/*.{sh,zsh,py} + scratch/agent/*.{sh,zsh} for the stderr tags they match (grep -a '\[...', re
patterns); list them. Step 2 (one run each arm, 150 s, tools/s7431_stderr_volume.sh): default vs ROGUESQ_DIAG_QUIET=1; a
harness tag present in default but 0 in QUIET = class member.
Hypotheses: H-few (a handful of markers: [initMission], [osViSwapBuffer, VI/phase markers -> add to rs64_diag_keep or (fprintf)),
H-many (consumers depend on high-rate per-frame tags -> QUIET stays a non-harness arm, document), H-none.
Discriminator: count of harness-consumed tags dropped under QUIET. Positive control: [initMission] must show as dropped.
Close with g1_level_coverage_common.zsh running one level to flight under XENV_EXTRA=ROGUESQ_DIAG_QUIET=1.
