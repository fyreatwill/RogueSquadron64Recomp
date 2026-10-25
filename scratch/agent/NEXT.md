# NEXT: name the game-side producer of the extra wide central draws
HYPOTHESIS-ID: g1d-widescreen

Session 6189 selected H-rdp-producer: the wide phase-4 stream has 2,165
central-overlapping TEXRECTs versus 1,868 in control, while source target
dimensions and readback extents match the requested width. Competing
hypotheses for the remaining writer attribution:

- H-menu-display-list: the widened menu/title display-list builder emits the
  extra central rectangles intentionally from a width-dependent path.
- H-rsp-geometry: the LLE RSP output differs before the RDP submission range,
  creating extra geometry/rect commands from a bad viewport or scissor input.
- H-secondary-pass: a hidden secondary CI/scissor pass, not the last CI, paints
  the central rectangle and is only exposed by the wide route.

Discriminator: join each phase-4 `[g1d-cmd]` record to its RDP submission
range and guest RSP task/DL source, then compare the first matched frame
ordinal in both arms. A command present only in the wide arm with a guest
display-list/RSP source selects H-menu-display-list or H-rsp-geometry by its
source PC; identical source commands with a distinct secondary CI/scissor
range selects H-secondary-pass. No clamp, cull, skip, or other mitigation is
allowed until the writer and legitimacy of the wide pixels are named.

Exact next work unit: add the source task/DL identity to the existing
phase-4 command records in one build, export submodule patches if needed, build
Debug, and run the same `zsh scratch/agent/s6179_g1d_rdp_words.sh` route with
the route controls (>=160 joins and >=400 copies per arm).
