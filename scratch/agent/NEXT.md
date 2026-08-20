# NEXT work unit (s2072)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Repair the oracle's named-writer post-store join so one-shot samples are
guaranteed for the exact retail PCs already attributed to the E50 envelope:
`0x8008F7D4`, `0x80091374`, and `0x8008FB64/68/78`. Keep the current phase gate,
KSEG0 conversion, bounded histogram, and final range summary. The targeted
sample path must not depend on the general histogram's 256-word budget or on
the generic writer-PC table; it needs an explicit per-requested-PC seen bit
and one `[post-target] pc=... value=...` row per target PC. Do not change the
port, task fields, output routing, canary, guest gate, waits, guards, or guest
behavior.

ORIGIN: s2068 independently attributes E50 writes to named MusyX/audio
functions, while s2071's generated oracle sampler reaches the exact span and
the same named PCs in its ordinary histogram but does not attach post-store
values to them. The port's generated `L_1E48` path still emits zero-only E50
payloads and returns `Broke`; this unit repairs observation linkage only.

## Competing hypotheses and discriminator

- **H-E50-RetailFinal** — the named retail audio PCs write nonzero,
  PCM-shaped words into the exact E50 envelope. The port's zero-only E50 rows
  are then a live image-task destination/ABI mismatch.
- **H-E50-RetailIntermediate** — the named PCs write zero, metadata, pointers,
  sentinels, or otherwise non-PCM values. E50 ownership is real but does not
  identify final PCM output.
- **H-E50-PortPayloadMatch** — the named retail post-store values match the
  port's exact E50 class, including the zero-only FNV `0x25E26BC5` table.

The discriminator is one phase-qualified table containing the whole-RDRAM
positive control, title/hangar VI anchors, one post-store value per named
writer PC, the exact-E50 snapshot FNV/nonzero summary, and the port crosswalk.
H-E50-RetailFinal requires nonzero PCM-shaped named-PC values plus a port
mismatch; H-E50-RetailIntermediate requires zero/metadata/non-PCM named-PC
values; H-E50-PortPayloadMatch requires named-PC values matching the port
class. A hit count or unjoined PC histogram selects nothing.

## Exact commands

1. Re-run the corrected Rice witness before editing the oracle; require the
   whole-RDRAM control, exact-E50 writes, title VI `1024 @ 0x00790400`, and
   hangar VI `512 @ 0x006AB400`:

   ```sh
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --watch-write 0x0:0x800000 --watch-write 0x1931F0:0x194E70 --hit-cap 10000 --vi-trace
   ```

2. Add the explicit requested-PC seen-bit path to `tools/oracle/rs64_oracle.c`
   and rebuild:

   ```sh
   tools/oracle/build.sh
   ```

3. Run one corrected route with the same watches and the named-PC list. Save
   it to a named path; require `[post-target]` rows for all five PCs:

   ```sh
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --watch-write 0x0:0x800000 --watch-write 0x1931F0:0x194E70 --hit-cap 10000 --vi-trace --pc-hist-watch 1 --post-value-watch 1 --post-value-pc 8008f7d4,80091374,8008fb64,8008fb68,8008fb78 > scratch/agent/oracle_s2072_e50_targeted.log 2>&1
   ```

4. Crosswalk the five named-PC values and the exact-range FNV/nonzero table
   against s2070's port E50 rows (`0x25E26BC5`, zero nonzero bytes). Run
   `git diff --check`; no runtime behavior change is authorized by the result.
