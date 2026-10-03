# Next work unit: qualify retail family reachability with Start input

HYPOTHESIS-ID: m5-retail-family-ground-truth

The s3782 return/Z recipe stayed in the early 320-wide attract phase despite a
positive whole-RDRAM control. Do one new retail-oracle input/phase
qualification using repeated Start pulses; do not add port instrumentation or
change game behavior.

Competing hypotheses and discriminator:

- H1: repeated Start reaches a retail target VI and at least one family PC,
  enabling the independent route-state comparison.
- H2: it reaches a target VI but no family PC, proving a retail PC/route
  mismatch rather than port route parity.
- H3: it remains pre-target, proving this input recipe is still unqualified.

The discriminating measurement is one run with the whole-RDRAM positive
control, candidate route-byte watches, all three family execution watches, VI
trace, and repeated Start input. H1 requires a family hit plus target VI; H2
is target VI with zero family hits; H3 is no target VI. A missing whole-RDRAM
control invalidates the run.

Exact command:

    mkdir -p scratch/agent/s3783_oracle_family_start
    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --secs 120 --hold-ms 150 \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
      --watch-write 0x0:0x800000 \
      --watch-write 0x141AD0:0x141AD2 \
      --watch-write 0x13B038:0x13B039 \
      --watch-write 0x141AD1:0x141AD2 \
      --watch-pc 0x80007640,0x8001E230,0x8001F954 \
      --pc-phase-log-width 0x00790400:1024 \
      --pc-phase-log-width 0x006AB400:512 \
      --hit-cap 12 --vi-trace \
      > scratch/agent/s3783_oracle_family_start/oracle.log 2>&1

Use SIGKILL only if a watchdog is needed. Record whether the positive control,
target VI, and each family PC fired. Do not infer route identity from route
byte writes alone.
