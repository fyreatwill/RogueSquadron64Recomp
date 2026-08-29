# NEXT work unit — retail boundary for the next VI publication handoff family

HYPOTHESIS-ID: m5-retail-video-publication-boundary

## Single work unit

Use `scratch/agent/s3119_m5_vi_request_callers.md` to move the independent
retail oracle to the next unenumerated handoff family: attribute the first
write/call after the pending request-mask store and before the VI descriptor
changes from 640 to 1024. Build one watch set containing the whole-RDRAM
positive control, title/hangar phase controls, and the complete candidate PC
range. Do not repeat `0x800C2984`, `0x8001A098:0x8001BB6C`, or the closed
selector/helper range. Do not modify the port in this unit.

## Competing hypotheses

- H-NextHandoff: a retail-attributed store/call in the interval identifies the
  missing VI publication boundary.
- H-OutsideInterval: the descriptor changes through a writer outside the
  interval, so the next probe must widen to the descriptor consumer or VI
  register handoff.
- H-NoTransition: title is reached without a directly attributable descriptor
  write in either family, indicating deferred/frame-boundary publication.

## Discriminating measurement

The PC-attributed write/call sequence across the 640-to-1024 transition splits
the hypotheses. A candidate in the interval with a matching descriptor write
selects H-NextHandoff; a widened-handoff write selects H-OutsideInterval; no
descriptor write with passed phase controls selects H-NoTransition.

## Exact commands

Run the existing retail-oracle recipe from `tools/oracle/README.md`, retaining
the whole-RDRAM positive control and title/hangar phase controls. Record the
watch configuration and result in a new `scratch/agent/s3121_*` artifact.
