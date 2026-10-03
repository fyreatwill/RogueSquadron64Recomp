# Next work unit: target-phase retail/port source-route parity

HYPOTHESIS-ID: m5-audio-retail-port-route-parity

s3820 qualified retail hangar source parity: the exact 408-byte phase snapshot
at VI `0x006AB400`/512 was zero with `FNV=0x762B22A5`, matching the qualified
port input-DMA payload. The next unit must join that retail target snapshot to
the native image-stage/source-DMA route; do not repeat the retail nonzero-writer
census or rely on a shutdown snapshot.

Competing hypotheses and discriminator:

- H1: retail and port consume the same zero source payload and the remaining
  M5 difference is downstream route/consumer behavior.
- H2: retail reaches the zero source span through a different route or timing
  edge, so equal bytes do not establish route parity.
- H3: the paired capture is coverage-invalid (missing target phase or a control
  failure), so no route conclusion is allowed.

The discriminator is one paired, phase-gated capture with independent whole-
RDRAM/target/source-DMA/task/audio-return controls: retail must emit a
hangar-phase `phase-snapshot` row for watch 1, and the port image arm must emit
the existing source-DMA FNV/zero row and route/image-stage controls in the same
target phase. H1 requires both target payloads to be zero with
`FNV=0x762B22A5` and the route controls to agree; H2 requires valid controls
but a route/source-stage mismatch; H3 is any missing positive control or target
phase in either arm.

Commands:

    env PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
      PROBE_KEYS_FROM_PHASE=1 PROBE_KEYS='12:start' \
      zsh tools/probe.sh scratch/agent/s3821_m5_retail_port_route/port 75

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --watch-write 0x0:0x800000 --watch-write 0x1798B0:0x179A48 --hit-cap 20 --detail-watch 1 --pc-hist-phase 0x6AB400:512 --phase-snapshot-watch 1 --vi-trace > scratch/agent/s3821_m5_retail_port_route/retail.log 2>&1

Inspect only bounded `[phase]`, `phase-snapshot`, source-DMA, route, task,
audio-return, and positive-control lines. Kill the native process with SIGKILL
if the wrapper does not exit; do not infer parity from a shutdown-only summary.
