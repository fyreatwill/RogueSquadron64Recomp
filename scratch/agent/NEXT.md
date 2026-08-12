# NEXT work unit (consume s734 reset-route soak)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Consume and score `scratch/agent/soak_queue/s734_reset_route.sh`. It runs the
already-built phase-latched source-route trace. For active depth-0 resets it
retains bounded first/last records of return address, resident-overlay id
(`DMEM[0x153]`), pre-reset depth, `r17`, and pending dispatch context. Do not
add a mitigation or rebuild unless the queue result proves an instrument bug.

## Competing hypotheses

- **H-wrong-trigen-route:** every active reset enters `L_1DB0` through the
  `0x05` TriGen overlay relay with the resident/return route that the generated
  overlay splice maps incorrectly; the reset is an accidental execution of a
  bootstrap path in an active `0x06` child.
- **H-intentional-trigen-reset:** active resets use a consistent, valid TriGen
  route and resident id, so the original microcode deliberately clears the
  local frame depth at this mesh boundary; the host's call-depth model is not
  the correct semantic ownership boundary.
- **H-route-mixed:** active resets arrive through multiple source routes, so no
  single overlay-route assumption explains the repeated depth-0 overwrite.

## Discriminating measurement

Score the queued log's `[e9-prov-reset-route]` rows. One uniform active-reset
route matching the `0x05` relay selects H-wrong-trigen-route; a uniform route
whose static semantics show an intentional reset selects H-intentional-trigen-reset;
multiple route tuples select H-route-mixed. Positive controls: the same run
must retain balanced direct-only boot rows and reproduce a section-2 cap row
with reset-active count equal to depth-0 reuse and zero unpaired reuse.

## Commands

    tail -20 scratch/agent/SOAK-RESULTS.md
    rg -n '\[e9-prov-reset-route\]|\[e9-prov-reset\]|\[e9-prov-depth-summary\]|\[e9-prov\]' scratch/agent/soak_results/s734_reset_route_*/run.log | tail -160
