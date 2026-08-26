# NEXT work unit (s2438) — join retail caller to callee context

HYPOTHESIS-ID: m5-retail-callee-context

## Work unit

Run one bounded retail-oracle capture with the validated eleven-Start route.
Keep the whole-RDRAM, exact image-range, title, and hangar controls. Watch both
the actual `jal` callsite `0x8008F2CC` and its callee/store-helper entry
`0x800078EC`; phase-gate all six observed 640 intro origins plus title and
hangar. Add `--pc-field-dump 0x800078EC` alongside the existing caller dump
and exact `--store-field-dump 2:0x800078EC`. Observation-only; no port change.

## Competing hypotheses and discriminator

- H-RetailCalleeSameInvocation: the intro caller and callee rows share a
  phase-local `$s0/$s1` and source-field tuple, showing one semantic path.
- H-RetailCallerToOtherPath: the intro caller reaches `0x8008F2CC`, but the
  callee context differs or no callee row joins it in that phase.
- H-RetailCalleeUnreached: controls pass but no phase-gated callee row exists.

The discriminator is one same-run table keyed by phase/origin and the
callsite-to-callee return relation. A matching intro caller/callee tuple
selects H-RetailCalleeSameInvocation; a caller with a nonmatching callee
selects H-RetailCallerToOtherPath; zero callee rows with valid controls select
H-RetailCalleeUnreached.

## Exact validation

Use the existing oracle binary and recipe shape:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x167650:0x167C50 --watch-write 0x1798B0:0x179A48 --watch-pc 0x8008F2CC,0x800078EC --pc-phase-log 0x0066A500,0x005D4500,0x00696600,0x00696100,0x0062C200,0x0062BD00 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --pc-field-dump 0x8008F2CC,0x800078EC --store-field-dump 2:0x800078EC --hit-cap 200 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150

Require whole-RDRAM positive control, title `0x00790400:1024`, hangar
`0x006AB400:512`, and exact-range totals before interpreting nulls.
