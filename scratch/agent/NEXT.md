# NEXT work unit (identify the GBI owner of the B4/BF candidate stream)

HYPOTHESIS-ID: m3-drawindexed-copy-cycle

Perform one phase-gated source/runtime ownership probe. Keep the existing
triangle-dispatch breadcrumb and add one bounded record at GBI selection or
handler entry identifying the selected `GBIUCode` and map owner for raw
`0xB4/0xBF`. Batch E9 provenance, VI width, triangle dispatch, copy-cycle, and
DL-sync controls in one build and capture. Do not change command advancement,
emit geometry, or classify operand legitimacy.

Competing hypotheses and discriminator:

- H-factor5-candidates: the candidates use the Factor 5 map, but the A/B gate
  or handler ownership telemetry missed them.
- H-rdp-candidates: the candidates use the RDP GBI and cannot test the Factor 5
  map; this becomes a separate RDP-stream provenance issue.
- H-mixed-owner: both owners occur and require separate owner counts.

Discriminator: every candidate must have a matching owner record. Complete
Factor 5 ownership selects H-factor5-candidates; all-RDP ownership selects
H-rdp-candidates; both selects H-mixed-owner. A null is invalid unless the
positive triangle-dispatch control fires in the same run.

Exact execution after the bounded instrumentation change:

1. `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. `env ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_DISPATCH=1 ROGUESQ_LOG_RDP_ADVANCE=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_TRI_DISPATCH=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/agent/s790_postsec2_reachability.sh`

The run must launch from `build/`, use its watchdog, and use SIGKILL on
timeout. Do not run a cross-run animating-scene comparison.

Evidence from s847: the corrected run reached VI 1024, passed all four E9
controls, and recorded 40 candidate rows, all `ucode=1`. The RT64 enum maps 1
to RDP and 12 to F3DFACTOR5. The optional Factor 5 A/B handler recorded zero
rows, including when gated at the observed VI-640 candidate width.
