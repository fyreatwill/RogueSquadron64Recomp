# NEXT work unit — enumerate a new retail-grounded M5 boundary

HYPOTHESIS-ID: m5-retail-video-publication-boundary

## Single work unit

Use the independent retail oracle to watch the earlier `initVideoSubsystem`
handoff range `0x8001A098:0x8001B7B8` while retaining the whole-RDRAM positive
control and title/hangar VI phase controls. This is a new boundary; do not
repeat the three direct `osViSetMode` callsite watches or the closed selector
helper range.

## Competing hypotheses

- H-EarlyWriter: the range executes at the 640→1024 transition and supplies
  the missing writer boundary.
- H-OtherWriter: the range is live but does not write the transition mode;
  the writer is later or in a different handoff.
- H-RangeDead: the range does not execute despite positive control and title/
  hangar phases; this boundary is closed.

## Discriminating measurement

The measurement is the oracle's PC-attributed write/watch rows in the handoff
range at the 640→1024 transition, with the positive control and phase rows
visible in the same capture. A transition write in the range selects
H-EarlyWriter; execution without the mode write selects H-OtherWriter; zero
range rows with valid controls selects H-RangeDead.

## Exact command shape

Run the existing retail-oracle recipe from `tools/oracle/README.md`, adding
the range watch and retaining the whole-RDRAM control. Capture the result in
`scratch/agent/s3115_m5_retail_init_video_range/` and do not build the port.
