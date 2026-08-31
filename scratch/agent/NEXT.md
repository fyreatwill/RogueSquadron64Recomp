# NEXT work unit — re-establish the retail PCM producer dispatch address

HYPOTHESIS-ID: m5-image-stage3-destination

The 120-second caller capture and its corrective adjacent-PC capture both
passed whole-RDRAM, title/hangar, and `0x1935E0` controls. `0x800078EC` ran
9,699 times, but `0x8002BEE8` and `0x8002BEEC` were zero. The earlier 2BEEC
attribution is stale or route-dependent and must be reconciled before port
instrumentation.

Competing hypotheses:

- `H-ProducerDirectCall`: `0x80033300` is the live caller seen in the earlier
  route census; it executes with a usable `exec-prev` row in this route.
- `H-ProducerAlternateCall`: the live caller is another watched adjacent PC;
  `0x80033300` remains zero while `0x800078EC` is live.
- `H-ProducerSelfLoopOnly`: the observed `0x800078EC` activity is only its
  internal loop, with no external dispatch site in this route.

Discriminator: one 120-second retail oracle run watching
`0x80033300,0x800078EC,0x800078E8,0x8002BEE8,0x8002BEEC`, with the whole-RDRAM
positive control, `0x1935E0` control, title/hangar phase gates, and phase
histograms. A nonzero `0x80033300` count and its `exec-prev` row selects the
direct caller; zero there with another adjacent hit selects an alternate
caller; only `0x800078EC` live preserves the self-loop explanation.

Command:

    mkdir -p scratch/agent/s3405_retail_pcm_dispatch
    env tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 120 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x80033300,0x800078EC,0x800078E8,0x8002BEE8,0x8002BEEC \
      --watch-write 0x1935E0:0x1935F0 \
      --pc-phase-log 0x00790400,0x006AB400 \
      --pc-hist-phase 0x00790400:1024 \
      --pc-hist-phase 0x006AB400:512 \
      --vi-trace \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
      > scratch/agent/s3405_retail_pcm_dispatch/oracle.log 2>&1

Keep the capture SIGKILL-safe and do not add port instrumentation until the
retail dispatch site is named.
