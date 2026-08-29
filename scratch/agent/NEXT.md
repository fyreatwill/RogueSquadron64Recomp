# NEXT work unit — enumerate the post-init retail M5 boundary

HYPOTHESIS-ID: m5-retail-video-publication-boundary

## Single work unit

Use the independent retail oracle to watch the new code gap immediately after
the late `initVideoSubsystem` range, `0x8001B7B8:0x8001BB6C`, while retaining
the whole-RDRAM positive control and title/hangar VI phase controls. Do not
repeat the three direct `osViSetMode` callsite watches, the closed selector
helper range, or `0x8001A098:0x8001B7B8`.

## Competing hypotheses

- H-GapWriter: the gap executes at the 640→1024 transition and contains the
  missing writer boundary.
- H-OtherWriter: the gap executes but does not write the transition mode; the
  writer is elsewhere.
- H-GapDead: the gap does not execute despite positive control and title/hangar
  phases; this boundary is closed.

## Discriminating measurement

The measurement is the oracle's PC-attributed execution rows in
`0x8001B7B8:0x8001BB6C` at the 640→1024 transition, with the positive control
and phase rows visible in the same capture. Transition-time execution in the
gap selects H-GapWriter; execution without a transition-time mode write
selects H-OtherWriter; zero gap rows with valid controls selects H-GapDead.

## Exact command shape

Run the existing retail-oracle recipe from `tools/oracle/README.md`, adding
`--watch-pc-range 0x8001B7B8:0x8001BB6C` and retaining the whole-RDRAM control.
Capture the result in
`scratch/agent/s3116_m5_retail_post_init_range/` and do not build the port.
