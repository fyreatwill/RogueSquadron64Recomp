# NEXT work unit (s2077)

HYPOTHESIS-ID: m5-retail-fill-sample-boundary

## Work unit

Ask the independent retail oracle for one phase-qualified PC witness of the
new boundary exposed by s2076. Do not build the port or change guest/host
behavior. Use the corrected Rice oracle with a whole-RDRAM write positive
control, PIF Start tracing, title/hangar VI anchors, status polling, and one
batched `--watch-pc` set covering the port treatment's later crash PC
`0x8000B650` (`fillSampleStreamRange`), the wait/tick/status readers, the
retail wait candidate, and the named status writers.

## Competing hypotheses and discriminator

- **H-RetailFillBoundary** — qualified retail execution reaches
  `0x8000B650` and joins one or more wait/tick/status PCs, with a retail slot
  transition; the port's no-slot treatment result is a scheduler/ABI
  divergence at a shared audio boundary.
- **H-PortOnlyFillBoundary** — whole-RDRAM, PIF, title, and hangar controls
  fire, but retail has no `0x8000B650` hit; the later fill-sample crash is
  port-only and must not be treated as a retail contract.
- **H-RetailDistinctVoiceStage** — retail reaches `0x8000B650` but none of
  the wait/tick/status PCs or slot-table writers join it; the fill routine is
  a distinct voice-stage contract.

The discriminator is the same-run PC intersection and phase/slot control
table. A zero target-PC result without whole-RDRAM, PIF, title, and hangar
controls is UNEVALUABLE. A retail hit on `0x8000B650` alone is not enough to
select a shared boundary.

## Exact command

Run from the repository root and capture to an absolute path:

```sh
tools/oracle/build/rs64_oracle \
  --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom ../rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --input /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-input-sdl.dylib \
  --secs 65 --hit-cap 10000 \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x8000B650,0x800668B0,0x8008DA00,0x8009B62C,0x8009B654,0x8009B3EC,0x8009B44C,0x8008EC88,0x80095D54 \
  --status-poll --pif-trace --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/oracle_s2077_fill_boundary.log 2>&1
```

Report the whole-RDRAM hit count, PIF/title/hangar controls, each requested
PC hit count and any phase/slot-cycle join. Do not infer from a null without
the positive controls. No mitigation or treatment rerun is authorized until
this oracle boundary is classified.
