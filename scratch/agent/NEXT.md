# NEXT work unit (s2088)

HYPOTHESIS-ID: m5-voice-output-base-provenance

## Work unit

Use the existing oracle post-store-PC facility to obtain the dynamic retail
voice-array addresses without arming the pointer-table stepping path. Keep a
whole-RDRAM positive-control watch first, remove it at the threshold, and
leave a second whole-RDRAM watch armed for phase-gated post-store samples at
the two static candidate writer PCs. Do not change the port, add a port
witness, or add another guest diagnostic field.

## Competing hypotheses and discriminator

- **H-ValidVoiceBase** — retail candidate writers `0x80090C80` and/or
  `0x800921E8` post-store into valid KSEG0/RDRAM addresses at the expected
  0x88-stride voice slots, with values consistent with the generated source
  fields.
- **H-InvalidWriter** — a candidate writer executes in a qualified title/
  hangar run but its post-store address or value is outside the RDRAM/voice
  domain.
- **H-WrongSlotBase** — candidate writers execute, but their post-store
  addresses do not form the expected `base + voiceIdx*0x88 + 0x34` pattern.
- **H-ScalarField** — neither candidate writer produces an address/value
  pattern consistent with a voice output-base field; the callee's pointer
  interpretation remains a mislabeled/scalar-field possibility.

The discriminator is the same-run `post-target-summary` address/value table
for both PCs, gated by the whole-RDRAM control plus title
`1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. Valid KSEG0 addresses with
the expected stride select H-ValidVoiceBase; an out-of-domain value selects
H-InvalidWriter; a stable non-voice address pattern selects H-WrongSlotBase;
and a fully qualified run with neither candidate pattern leaves H-ScalarField
as the unresolved alternative. A missing candidate hit is unevaluable unless
the control and both target phases fire.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 65 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x0:0x800000 \
  --post-value-watch 1 \
  --post-value-pc 0x80090C80,0x800921E8 \
  --watch-pc 0x8009024C:0x80090250 \
  --watch-pc 0x800902CC:0x800902D0 \
  --watch-pc 0x800903F0:0x800903F4 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2088_oracle/run.log 2>&1
```

Before interpreting a null, require `[oracle] positive-control threshold
reached`, both target VI transitions, and the `post-target-summary` rows.
