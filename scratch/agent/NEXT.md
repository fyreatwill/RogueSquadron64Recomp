# NEXT work unit (s2062)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Attribute the opt-in image arm's DMA destination band against the retail ROM
before changing the audio runner. s2061 showed that `factor5_ucode_b` writes
DMEM through the reserved `0xF80..0xF8F` canary and returns `Broke`, yet emits
19 matched nonzero title PCM pairs. The next unit asks whether the image's
DMA destinations are legitimate retail-owned audio buffers or an ABI-shaped
runtime artifact.

Do not change the guest gate, C88 value, task descriptor, RSP runner, canary,
wait/slot guards, PCM bridge, or default dispatch in this unit. Do not enable
stock `aspMain`. The port recipe is not rerun: s2061 already supplied the
phase-valid image rows; this unit is the independent writer attribution.

## Competing hypotheses and discriminator

- **H-RetailAudioWriter** — the retail game writes the image arm's destination
  band (`0x166000..0x17A000`) during the qualified title/hangar route, with
  PCs in the MusyX/audio producer path. This makes the destination class
  legitimate and leaves the `Broke`/canary result as an unresolved task ABI or
  output-layout contract.
- **H-WrongDestination** — retail never writes the image arm's destination
  band under the same route, or writes it only from an unrelated boot path.
  This selects an image-side destination/ABI mismatch; the nonzero title PCM
  is not sufficient evidence of a valid current task output.
- **H-WorkBufferNotPCM** — retail writes the band from audio code, but the
  writes are work/state buffers rather than the PCM destination. This keeps
  the task/output contract open and requires a narrower next watch around the
  actual AI source ring.

The discriminator is the retail narrow-watch hit count plus PC attribution,
phase timeline, and PIF/menu controls in one oracle run. The positive-control
watch must cross its threshold before any narrow-watch null is used. A target
watch hit from the named audio PCs selects H-RetailAudioWriter; zero target
writes after the qualified title/hangar route selects H-WrongDestination; a
target hit only from unrelated PCs selects H-WorkBufferNotPCM. A missing
whole-RDRAM threshold, PIF rows, title VI 1024, hangar VI 512, or relevant
menu PC selects H-RouteUnevaluable and no port interpretation is allowed.

## Exact command

Run from the repository root, before any port command:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x166000:0x17A000 \
  --watch-write 0x0CE730:0x0CE828 \
  --watch-pc 0x800B47C4,0x800B8014,0x800B8050 \
  --vi-trace --pif-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start \
  > scratch/agent/s2062_oracle.log 2>&1
```

Require the positive-control threshold, at least one target-band write and
its PC (or a qualified zero), PIF Start rows, title VI 1024, hangar VI 512 at
`0x006AB400/0x006AB800`, and at least one relevant menu PC before selecting a
hypothesis. Preserve the oracle log and report the target watch's PCs, not
just its count.

ORIGIN: no guest writer, C88 value, wait, guard, skip, audio task, callback,
or default behavior change is authorized; this is an independent retail
writer attribution for the already-observed image-arm destination class.
