# NEXT work unit (s2071)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Add one bounded post-store value witness to the retail oracle for the exact
E50 envelope `0x1931F0..0x194E70`, then run one corrected Rice route and
crosswalk its value/FNV/nonzero table against s2070's port-side
`0xE50/0x180` rows. The oracle callback currently reports writer PCs and hit
counts but not the value written by the stopped store; extend it only enough
to capture a bounded post-step value histogram and per-watch nonzero-byte/FNV
summary. Do not change the port, task fields, output routing, canary, guest
gate, waits, or guards.

ORIGIN: retail writer PCs are independently established, while the port's
generated `L_1E48` writer emits zero-only E50 payloads and returns `Broke`.
Whether the retail E50 bytes are final PCM or an intermediate work buffer is
not established by writer ownership alone.

## Competing hypotheses and discriminator

- **H-E50-RetailFinal** — retail writes to the exact E50 envelope carry
  nonzero, PCM-like final output. The port's zero-only E50 rows are then a
  live image-task destination/ABI mismatch, not evidence that E50 is scratch.
- **H-E50-RetailIntermediate** — retail writes to the exact envelope are
  zero/constant or otherwise do not match a PCM payload; the port's zero-only
  rows cannot be classified as a final-output mismatch from this span.
- **H-E50-PortPayloadMatch** — the retail post-store values match the port's
  exact E50 payload classes and the current port capture is a stale or
  phase-misaligned witness. This requires a value/FNV/nonzero match, not just
  the same address range.

The discriminator is one phase-qualified oracle table containing the whole-
RDRAM control, VI anchors, exact-E50 post-store value/FNV/nonzero summaries,
and writer-PC histogram. H-E50-RetailFinal is selected by nonzero
PCM-shaped retail values plus a port mismatch; H-E50-RetailIntermediate by
zero/constant or non-PCM values; H-E50-PortPayloadMatch only by matching
post-store payload classes. A hit counter or PC histogram alone selects
nothing.

## Exact commands

1. Before modifying the oracle, rerun the existing corrected Rice witness and
   require the whole-RDRAM control, title `1024 @ 0x00790400`, hangar
   `512 @ 0x006AB400`, and nonzero exact-E50 writes:

   ```sh
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --watch-write 0x0:0x800000 --watch-write 0x1931F0:0x194E70 --hit-cap 10000 --vi-trace
   ```

2. Add the single post-store value summary to `tools/oracle/rs64_oracle.c`
   and rebuild the oracle:

   ```sh
   tools/oracle/build.sh
   ```

3. Run the same route with the whole-RDRAM watch first and the E50 watch
   second; use the new value-summary option for watch 1. Capture to a named
   path and keep `--vi-trace` enabled:

   ```sh
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --watch-write 0x0:0x800000 --watch-write 0x1931F0:0x194E70 --hit-cap 10000 --vi-trace --pc-hist-watch 1 --post-value-watch 1 > scratch/agent/oracle_s2071_e50_values.log 2>&1
   ```

4. Compare the oracle E50 value/FNV/nonzero classes with s2070's port
   `audtask-dma-range` rows. Run `git diff --check`; no runtime behavior
   change is authorized by the result alone.
