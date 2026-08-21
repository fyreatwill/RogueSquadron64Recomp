# NEXT work unit (s2101)

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Ask the independent retail oracle whether the exact physical destinations seen
in s2100's nonzero hangar image task are retail-owned audio output/metadata
buffers. Watch the whole RDRAM positive control first, then the exact port
destination spans:

- `0x166A50..0x167350`: the three nonzero `0x6F0` writebacks from the sampled
  task (`0x166A50`, `0x166D50`, `0x167050`);
- `0x178D80..0x178F18`: the sampled `0xCB0` writeback destination.

Keep the run phase-gated by the retail title/hangar VI transitions, collect
writer-PC histograms and post-store values for both exact watches, and do not
change the port or add a runtime instrument before this ground-truth result.

## Competing hypotheses and discriminator

- **H-RetailExactSame** — retail writes the exact physical destination spans
  in title or hangar, with named PCs and values compatible with the port's
  observed nonzero `0x6F0`/zero `0xCB0` rows.
- **H-RetailDifferentEnvelope** — retail audio activity is real, but its
  writes avoid both exact spans; the port destination contract is not yet
  qualified by retail.
- **H-RetailMetadata** — retail hits an exact span, but post-store values and
  writer ownership identify control/metadata rather than PCM output.
- **H-PortOnlyDestination** — the port-only exact hit is absent after both
  target phases, leaving an ABI/field interpretation boundary rather than a
  retail ownership match.

The discriminating table is one oracle run with rows keyed by watch index,
physical address, VI phase, writer PC, and post-store word. Whole-RDRAM hits
must be nonzero and the run must reach title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. Exact hits with matching writer/value envelopes select
`H-RetailExactSame`; exact hits whose values are control-like select
`H-RetailMetadata`; zero exact hits after both qualified phases retain
`H-RetailDifferentEnvelope`/`H-PortOnlyDestination` as the open boundary.
Do not infer from the broad windows or from a zero before a target phase.

## Exact command

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 64 --watch-write 0x0:0x800000 --watch-write 0x166A50:0x167350 --watch-write 0x178D80:0x178F18 --first-watch 0 --pc-hist-watch 1 --pc-hist-watch 2 --post-value-watch 1 --post-value-watch 2 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/oracle_s2101_exact_destinations.log 2>&1
rg -n '\[oracle\] (done|post-value snapshot|watch write)|^\[vi\].*(WIDTH|origin=0x006ab|origin=0x007904)' /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/oracle_s2101_exact_destinations.log
```

If the exact watches are empty despite the positive control and both target
VIs, retain the port-only boundary and design the next task/consumer join;
do not alter output routing, task fields, canary, gate, wait, guard, queue
policy, or default dispatch.
