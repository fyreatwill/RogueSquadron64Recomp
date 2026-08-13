# NEXT work unit (classify the RDP-owned B4/BF candidate stream)

HYPOTHESIS-ID: m3-rdp-triangle-candidate-origin

Perform one phase-gated source/runtime provenance probe for the RDP-owned
`0xB4/0xBF` candidate stream. Keep the owner and triangle breadcrumbs, and add
one bounded record of the RDP command-table entry/length and surrounding parser
boundary for each candidate. Batch E9, VI-width, triangle-owner, copy-cycle,
and DL-sync controls in one build and capture. Do not change command
advancement, emit geometry, or classify operand legitimacy.

Competing hypotheses and discriminator:

- H-rdp-legitimate: RDP reaches genuine B4/BF commands at valid boundaries.
- H-rdp-misframed: RDP is selected, but command length/boundary state makes a
  candidate misframed.
- H-rdp-garbage: RDP reaches a boundary-shaped slot that is not a legitimate
  game command; writer attribution remains required.

Discriminator: compare every owner row with the command-table length and
preceding parser span. Valid RDP boundaries select H-rdp-legitimate;
boundary/length disagreement selects H-rdp-misframed; a valid boundary without
writer evidence leaves H-rdp-garbage open. A null is invalid unless triangle
dispatch and owner controls fire in the same run.

Exact execution after the bounded instrumentation change:

1. `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. `env ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_DISPATCH=1 ROGUESQ_LOG_RDP_ADVANCE=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_TRI_DISPATCH=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/agent/s790_postsec2_reachability.sh`

The run must launch from `build/`, use its watchdog, and use SIGKILL on
timeout. Do not run a cross-run animating-scene comparison.

Evidence from s848: the run reached VI 1024, passed the E9 controls, and
recorded one candidate/owner pair, both `ucode=1 owner=RDP`; the source enum
maps 1 to RDP and 12 to F3DFACTOR5. The capture had zero copy-cycle rows.
