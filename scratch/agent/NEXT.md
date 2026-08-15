# NEXT work unit (s1209)

HYPOTHESIS-ID: retail-execution-path-reachability

Work unit: run one debugger-enabled retail reachability comparison using
repeated A confirmation pulses across the title window, paired with an
undriven control. The single A pulses at 6s and 18s both passed controls but
had no effect; test whether the title requires a repeated confirmation edge.
Driven presses are
`17:a,18:a,19:a,20:a,25:start,30:start,35:start,40:start,45:start,50:start,55:start`.
Preserve the whole-RDRAM watch, `--pif-trace`, and `--vi-trace` in both arms.
Do not arm an M4 target watch until a later VI phase is reached.

Competing hypotheses and discriminator:

- H1: repeated A confirmation edges change the state path and the driven arm
  reaches a later VI phase/origin than width 320 / `0x006dd280`.
- H2: both arms remain at VI 320 / `0x006dd280` while controls pass; pulse
  timing is not the missing retail entry mechanism.
- H3: either arm fails whole-RDRAM or PIF/VI controls; the comparison is
  invalid and the path hypothesis is untested.

Positive controls: each arm's whole-RDRAM watch must reach 10,000 callbacks;
the driven arm must show four PIF-confirmed A press/release pairs and the
scheduled Start press/release pairs; both arms must emit debugger-enabled VI
records. A null without all controls is invalid.

Exact commands (run from the repository root, 60 seconds each):

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --press 17:a,18:a,19:a,20:a,25:start,30:start,35:start,40:start,45:start,50:start,55:start --hold-ms 150 --vi-trace --pif-trace > scratch/agent/oracle_repeated_a_driven.log 2>&1
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace > scratch/agent/oracle_repeated_a_undriven.log 2>&1

If H1 is selected, retain the path change and arm the resulting later-phase
measurement. If H2 is selected, seek a different retail entry mechanism. If
H3 is selected, repair the control setup before drawing a conclusion.
