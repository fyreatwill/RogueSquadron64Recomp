# NEXT: PIVOT — audit hangar artifacts with a same-phase framebuffer table
HYPOTHESIS-ID: g3-hangar-artifacts

Pivot status (s6601): the prior `g1c-dd-phase2` witness stalled for three
iterations without an advanced result. Do not rerun it under that slug.

One work unit: capture the same hangar phase at retail 4:3, ASPECT 16:9, and
ASPECT 21:9, then join each dump to VI origin/width and compare the artifact's
pixel bounds plus RDP command range.

Competing hypotheses:
- H-viewport: an incorrect scissor/viewport exposes the rim band.
- H-stride: a wide framebuffer row or flip stride leaves stale right-edge data.
- H-rdp: RT64/RDP edge treatment creates the holo spikes.
- H-game: the submitted hangar geometry itself contains the artifact.

Discriminator: width-proportional stale bands select H-stride; fixed
screen-space clipping selects H-viewport or H-rdp; identical command geometry
and artifact in the retail control selects H-game. The framebuffer/VI join and
the known hangar-origin gate are the positive controls and must fire in every
arm.

Commands:

```sh
rg -n 'hangar|ROGUESQ_ASPECT|fbdump|VI origin|scissor|viewport' \
  tools scratch/agent docs | head -120
# Then write one build/run arm table and use the existing fbdump/contact-sheet
# tooling; keep all three aspect arms in this iteration.
```

Do not add a guard or skip. Default retail behavior must remain unchanged.
