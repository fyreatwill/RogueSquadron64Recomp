# NEXT work unit — oracle-test the newly identified menu VI handoff

HYPOTHESIS-ID: m5-retail-video-publication-boundary

## Single work unit

Run the independent retail oracle with a physical execution watch for guest
PC `0x800C2984` (`runMenuModelViewerScreen`), retaining the whole-RDRAM
positive control and title/hangar VI phase controls. This is the next test of
the static candidate documented in
`scratch/agent/s3117_m5_retail_handoff_static/AUDIT.md`.

## Competing hypotheses

- H-NewHandoff: `0x800C2984` is on the 640-to-1024 publication path.
- H-ExistingConsumer: it only requests/consumes state after publication; the
  writer is elsewhere.
- H-DeadOrAliased: it is unreachable in the retail route or overlay-aliased.

## Discriminating measurement

The watch must fire with a transition-time timestamp/phase attribution. A hit
at the 640-to-1024 transition, with the pending-word write and later title
phase, selects H-NewHandoff. Hits only after title/hangar publication select
H-ExistingConsumer. No candidate hit while the positive control and phase
controls pass selects H-DeadOrAliased.

## Exact run requirements

Use the oracle recipe under `tools/oracle/README.md`; arm the whole-RDRAM
positive control first, add the `0x800C2984` physical-PC watch, and keep the
title/hangar VI phase watches. Do not modify the port or repeat the closed
`0x8001A098:0x8001BB6C` ranges.
