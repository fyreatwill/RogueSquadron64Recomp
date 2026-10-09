# Next work unit (s4333): retail oracle C88C descriptor comparison

HYPOTHESIS-ID: m5-step9-retail-descriptor-compare

The s4332 qualified port matrix closed the join-boundary issue: both arms
joined C88C tuples to D740 rows. The initial descriptor prefix matched, but
later descriptor pointers/words and type/class distributions diverged. The
next bounded unit is an independent retail execution witness at C88C.

Competing hypotheses:

- H-retail-silent: retail C88C arguments/descriptor sequence matches the
  silent/MusyX-stub port arm; the image arm's route/stream selection diverges.
- H-retail-image: retail matches the real-image/Factor5 arm; the silent arm's
  route/stream selection diverges.
- H-shared-production: retail matches neither port sequence; descriptor
  production or its earlier input stream diverges in both port arms.
- H-oracle-invalid: the retail watch/control fails to reach the hangar phase,
  so no descriptor comparison is admissible.

Discriminator: run the retail ROM with a whole-RDRAM positive control, VI
trace, and an execution watch at `0x8009C88C`; compare the phase-gated `$a0`,
`$a1`, `$a2`, `$a3` rows and descriptor words with the two s4332 port logs.
Retail matching one arm selects that arm's route/stream ownership; matching
neither selects shared descriptor-production divergence; missing whole-RDRAM,
title, or hangar controls selects H-oracle-invalid and proves nothing about
the descriptor boundary.

Before building any new port instrument, verify the oracle controls with:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 180 --watch-write 0x0:0x800000 --watch-pc 0x8009C88C --pc-field-dump 0x8009C88C --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`

Do not change decoder, RSP, AI, or game-path behavior. Keep all comparison
rows phase-gated on VI origin `0x006AB400` and width 512.
