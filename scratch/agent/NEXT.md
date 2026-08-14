# NEXT work unit (s1151)

HYPOTHESIS-ID: vi-submitgfx-owner

Add one phase-scoped marker at the shared generated `submitGfxFrame` entry and
classify which caller family owns the post-640 loop. Do not add a guard or
repeat the NPC boundary test.

Competing hypotheses and discriminator:

- H1/mission-owner: post-640 slot dispatch and E9/render submission are driven
  by a mission frame caller of `submitGfxFrame`; the marker identifies that
  caller and its state edge.
- H2/cinematic-owner: the continuing path is a cinematic/menu caller of
  `submitGfxFrame`, separate from the mission selector predecessor.
- H3/host-only: generated `submitGfxFrame` is not reached in the continuing
  phase; E9 activity is produced by a host/runtime path without a game-side
  submit edge.

The discriminating measurement is one phase-gated run with the marker enabled
at the shared entry, logging the guest return address and phase ordinal, plus
the existing independent host selector positive control and task-control E9
control. H1/H2 are split by the caller address family; H3 is selected if the
positive E9 control and slot dispatch continue but the scoped `submitGfxFrame`
marker remains zero. A null is valid only if both positive controls fire.

Before building, add the marker through the regeneration/fixup path, not by
editing generated output directly. Then build and run the existing 1024
phase-gated recipe with the marker, selector positive control, slot dispatch,
and task-control E9 categories enabled. Capture output under
`scratch/agent/soak_results/s1151_vi_submitgfx_owner/` and kill with SIGKILL.
