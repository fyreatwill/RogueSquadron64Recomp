# NEXT work unit (attribute the RDP-owned B4/BF candidate writer)

HYPOTHESIS-ID: m3-rdp-triangle-candidate-writer

Perform one phase-gated source/runtime writer-attribution probe for the
RDP-owned `0xB4/0xBF` candidate stream. Keep `[tri-dispatch]`, `[tri-owner]`,
and `[tri-boundary]`; add one bounded source-tagged record at the accepted RDP
submit/LLE emission boundary carrying candidate address, task, submit serial,
and source range. Batch the E9, VI-width, triangle-owner, triangle-boundary,
copy-cycle, and DL-sync controls in one build and capture. Do not change
command advancement, emit geometry, or classify operand legitimacy.

Competing hypotheses and discriminator:

- H-game-writer: the game/LLE emission path writes the candidate bytes into a
  submitted range, making them legitimate game output despite the non-triangle
  RDP table entry.
- H-lle-writer: the LLE/RDP bridge or range bookkeeping associates an unrelated
  byte slot with the candidate; the candidate is not game-authored.
- H-unattributed: no accepted source range contains the candidate, leaving
  H-rdp-garbage open without a writer claim.

Discriminator: every boundary row must be compared with the source-tagged
accepted submit range and LLE emission address. A same-task source-range hit
selects H-game-writer; only bridge/range-origin evidence selects H-lle-writer;
no hit with positive owner/boundary controls selects H-unattributed. A null is
invalid unless owner and boundary controls fire in the same run.

Ground truth prerequisite already satisfied this iteration: the retail oracle's
whole-RDRAM positive control reported 1,596,610 writes in 8 emulated seconds
and 479 VI.

Exact execution after the bounded instrumentation change:

1. `./submodule-patches/export.sh`
2. `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. `env ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_DISPATCH=1 ROGUESQ_LOG_RDP_ADVANCE=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_TRI_DISPATCH=1 ROGUESQ_LOG_TRI_BOUNDARY=1 ROGUESQ_LOG_TRI_WRITER=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/agent/s790_postsec2_reachability.sh`

Run from the repository root; the recipe launches from `build/`, uses its
watchdog, and SIGKILLs the game on timeout. Do not run a cross-run animating
scene comparison.
