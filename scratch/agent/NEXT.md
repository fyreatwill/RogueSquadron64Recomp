# Next work unit: rerun one new retail navigation recipe with Rice attached

HYPOTHESIS-ID: m5-retail-family-ground-truth

s3787 supplied a valid whole-RDRAM positive control (10,003 writes), but the
oracle log explicitly said “No video plugin attached” and stayed at width 320.
Its zero target/family counts therefore cannot qualify retail reachability.
Use the same independently justified Start+Z input recipe, with the Rice
plugin required by tools/oracle/README.md explicitly attached; this is the
minimal fixed recipe, not a new interpretation of the null.

Competing hypotheses and discriminator:

- H1: Rice plus Start+Z reaches a target VI and at least one family PC,
  enabling the independent route-state comparison.
- H2: it reaches a target VI but no family PC, proving a retail PC/route
  mismatch rather than port route parity.
- H3: it remains pre-target even with Rice, proving this input recipe is still
  unqualified.

The discriminating measurement is one run with whole-RDRAM, route-byte, all
three family-PC watches, and VI trace. H1 requires a family hit plus target VI;
H2 is target VI with zero family hits; H3 is no target VI. A missing
whole-RDRAM control invalidates the run.

Exact command:

    mkdir -p scratch/agent/s3788_oracle_family_start_z_rice
    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 120 --hold-ms 150 \
      --press 6:start,6:z,11:start,11:z,16:start,16:z,21:start,21:z,26:start,26:z,31:start,31:z,36:start,36:z,41:start,41:z,46:start,46:z,51:start,51:z,56:start,56:z \
      --watch-write 0x0:0x800000 \
      --watch-write 0x141AD0:0x141AD2 \
      --watch-write 0x13B038:0x13B039 \
      --watch-write 0x141AD1:0x141AD2 \
      --watch-pc 0x80007640,0x8001E230,0x8001F954 \
      --pc-phase-log-width 0x00790400:1024 \
      --pc-phase-log-width 0x006AB400:512 \
      --hit-cap 12 --vi-trace \
      > scratch/agent/s3788_oracle_family_start_z_rice/oracle.log 2>&1

Record the positive control, video attachment, first target VI/origin, each
family-PC count, and route-byte counts. Do not infer route identity from
route-byte writes alone.
