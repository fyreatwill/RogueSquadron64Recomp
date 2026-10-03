# Next work unit: qualify retail family reachability

HYPOTHESIS-ID: m5-retail-family-ground-truth

The s3781 port witness read zero at all three candidate guest route-state
bytes, but the independent retail run stayed in attract and never reached
S/I/L. Do one new retail-oracle input/phase qualification; do not add port
instrumentation or change game behavior.

Competing hypotheses and discriminator:

- H1: the recipe reaches a retail target VI and at least one family PC; route
  byte writes then provide an independent route-state boundary.
- H2: the recipe reaches target VI but no family PC; the family entry is on a
  different retail route or address and the current discriminator is
  unevaluable.
- H3: the recipe remains in attract/pre-target; the oracle driving recipe is
  not qualified, so no route conclusion is allowed.

The discriminating measurement is one run with the whole-RDRAM positive
control, candidate route-byte watches, all three family execution watches, VI
trace, and controlled input. H1 requires a family hit plus target VI; H2 is
target VI with zero family hits; H3 is no target VI. A missing whole-RDRAM
control invalidates the run.

Exact command:

    mkdir -p scratch/agent/s3782_oracle_family_reach
    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --secs 120 --press 8:return,20:return,35:z,50:return \
      --watch-write 0x0:0x800000 \
      --watch-write 0x141AD0:0x141AD2 \
      --watch-write 0x13B038:0x13B039 \
      --watch-write 0x141AD1:0x141AD2 \
      --watch-pc 0x80007640,0x8001E230,0x8001F954 \
      --pc-phase-log-width 0x00790400:1024 \
      --pc-phase-log-width 0x006AB400:512 \
      --hit-cap 12 --vi-trace \
      > scratch/agent/s3782_oracle_family_reach/oracle.log 2>&1

Use SIGKILL only if a watchdog is needed. Record whether the positive control,
target VI, and each family PC fired. Do not infer route identity from route
byte writes alone.
