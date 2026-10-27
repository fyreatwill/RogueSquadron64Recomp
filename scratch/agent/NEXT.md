# NEXT: isolate the aspect-only route mismatch
HYPOTHESIS-ID: g3c-edge-fade-phase-c6390

The concurrent four-arm table did not satisfy its route gate: aspect-only
settled at origin 0x0058B038 rather than the required 0x00639238. Run only the
aspect arm from a clean process and capture all origin/width transitions. Do not
score edge pixels unless the expected mission origin is continuously observed.

Competing hypotheses:

- H-route-concurrency: the aspect-only origin changes only when four game
  instances run together; a clean solo run reaches 0x00639238.
- H-route-recipe: the aspect-only recipe or gate is stale; a clean solo run
  still reaches 0x0058B038, requiring a corrected route marker.
- H-route-legitimate: 0x0058B038 is the real aspect-only mission route and the
  prior 0x00639238 result was an incidental branch; solo runs reproduce it.

DISCRIMINATING MEASUREMENT: in the solo aspect run, compare the complete
`origin=...` transition stream with the expected 0x00639238 marker. Positive
controls are `fbrun-control OK`, width=796, nonzero terrain score, and zero VI
stalls/crash markers. 0x00639238 selects a concurrency artifact; repeated
0x0058B038 selects a route/gate correction; neither selects an edge hypothesis.

Exact command:

    env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 LEVEL=1 TITLE_ORIGIN=0x00639238 MISSION_RE=639238 TAG_SUFFIX=_s6391_edge_aspect_solo HOLD_S=180 XENV_EXTRA='ROGUESQ_ASPECT=16:9' zsh scratch/agent/g1_level_coverage_common.zsh > scratch/agent/s6391_edge_aspect_solo.out 2>&1

Inspect only the summary, `[phase] vi_width=` rows, and origin transitions. If
the solo gate passes, repeat the four-arm table next; if it fails, correct the
route marker before scoring any framebuffer edge.
