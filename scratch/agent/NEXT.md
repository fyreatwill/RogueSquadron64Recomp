# NEXT work unit (s2119) — retail ground truth for the MusyX gate

HYPOTHESIS-ID: m5-guest-gate-ground-truth

## Work unit

Run one retail-oracle writer/consumer census before adding or changing any
port instrumentation for guest gate `0x800A0F50`. The run must first arm the
whole-RDRAM positive control, then watch physical `0xA0F50`, countdown
`0x14998A`, and worker flag `0x14974C`, and must reach hangar VI origin
`0x006AB400`. Do not change generated stores, guards, task fields, output
routing, waits, queues, or default behavior in this work unit.

## Competing hypotheses and single discriminator

- H-GateNeverLive: the retail gate remains zero through the qualified hangar
  route; the port's zero gate is expected and no writer arm is justified.
- H-GateWriterSpecific: retail writes a phase-specific `0`/`1` transition from
  one or more named init/display writers; a later port arm must isolate one
  writer and observe its downstream consumer.
- H-GateMixed: retail has multiple writer PCs or both values at the target
  address, so a blanket store flip would conflate initialization, failure, or
  shutdown state with the live audio gate.

The single discriminator is the oracle's target-watch hit/value/PC histogram,
post-store value samples, and countdown/worker-flag watch activity, evaluated
only after the independent whole-RDRAM watch fires and VI trace reaches
`512 @ 0x006AB400`. Whole-RDRAM hits plus zero target hits selects
H-GateNeverLive; a named writer/value transition with a stable downstream
state selects H-GateWriterSpecific; multiple writer PCs or mixed values
select H-GateMixed. Missing hangar coverage is a coverage failure, not a null
gate result.

## Exact command

Run from the repository root:

    ORACLE=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/build/rs64_oracle
    CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
    ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
    "$ORACLE" --core "$CORE" --rom "$ROM" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 90 --vi-trace --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x14998A:0x14998E --watch-write 0x14974C:0x149750 --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2119_oracle_gate.log 2>&1

Inspect the positive-control summary, VI trace, target hit/value/PC lines,
post-value summaries, and the countdown/worker-flag histograms. If the oracle
does not reach `512 @ 0x006AB400`, record coverage failure and do not classify
the gate.
