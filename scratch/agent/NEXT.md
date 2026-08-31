# NEXT work unit — retail exec-prev for 0x8002BEEC dispatch caller

HYPOTHESIS-ID: m5-image-stage3-destination

The slot-level investigation is closed for hangar-512: both retail and port have
`field348=0x801797B0` (two independent lines from s3401 + s3402). The gap is in
what dispatches `0x8002BEEC` — the JAL that calls `0x800078EC` (the PCM writer).
In retail it fires 37,635 times per 120 s; in the port, zero times.

Use `--watch-pc 0x8002BEEC` to capture the oracle's `exec-prev` histogram for
that PC. The README states: "exec-prev pc=X prev=Y n=N — for each exec hit,
mupen's PREVIOUS_PC (the jal site that transferred here; $ra is prev+8)." This
names the JAL that dispatched the containing function.

Competing hypotheses:

- `H-Dispatch-DirectCaller`: exec-prev names a single JAL site; that site either
  exists in the port (same function, not called) or is absent (the call chain is
  missing).
- `H-Dispatch-IndirectCaller`: exec-prev shows many prev-PC values (indirect
  jump); the dispatcher is a callback table or function pointer that differs.
- `H-Dispatch-BootOnly`: exec-prev fires only during boot/init phases, not during
  title or hangar — which would mean the function IS called but only pre-phase.

Discriminator: the exec-prev histogram combined with phase-gated execution count.
Phase-gated count > 0 during hangar-512 refutes `H-Dispatch-BootOnly`.
A single dominant prev-PC points to a named JAL site (then cross-check in port).
Multiple prev-PCs point at an indirect dispatcher.

Command:

    mkdir -p scratch/agent/s3403_retail_8002beec_caller
    env tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 60 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x8002BEEC \
      --watch-write 0x1935E0:0x1935F0 \
      --pc-phase-log 0x00790400,0x006AB400 \
      --pc-hist-phase 0x00790400:1024 \
      --pc-hist-phase 0x006AB400:512 \
      --vi-trace \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
      > scratch/agent/s3403_retail_8002beec_caller/oracle.log 2>&1

Notes:
- 60 seconds is enough to reach hangar-512 (~38s measured); the phase-log
  restricts logged exec rows to title/hangar to prevent boot noise.
- Retain whole-RDRAM positive control. Retain `0x1935E0` as a secondary control
  (confirming retail PCM production path is live).
- The `exec-prev` lines in the shutdown summary name the JAL dispatch site.
- After getting the caller PC, grep the port's generated recomp code for that
  PC's caller chain to determine if the port is missing the dispatch path.
- Use SIGKILL-only cleanup.
