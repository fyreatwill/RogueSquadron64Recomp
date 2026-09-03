# M3 s3598 — MusyX voice `+0x66..+0x74` publication-family audit

## Work unit

Static census of every generated access to offsets `0x66` through `0x74`
in `../N64Recomp/RecompiledFuncs/funcs_24.c`. No build or runtime run was
performed.

The discriminator was a complete writer → consumer → base/layout →
lifetime/bound chain: a concrete invalid edge selects `H-NextClassGap`;
complete structural coverage of one object selects `H-NextClassComplete`;
mixed or missing layouts select `H-NextClassUnevaluable`.

## Census size

15 offset-first stores and 12 offset-second loads matched `MEM_[BHW]` at
those offsets. Three additional `MEM_BU` loads read voice-table `+0x6D`.
One further `MEM_BU` is `musyxRenderVoiceSamples`' incoming stack byte at
`r29+0x73` and is not a voice field.

`musyxStoreVoiceAdsrParams`, `musyxMixActiveVoices`,
`musyxBuildVoiceCommandList`, and `musyxSynthFrame` have no direct access
in this window. Mix and the builder only pass the command-list pointer
into render and key-on.

## Distinct layouts

The remaining accesses are not one record.

### 1. Command-list ping-pong (`D_80149708` / `D_8014970C`, stride `0x88`)

`musyxMixActiveVoices` walks the live slot-count halfword at
`0x8015:-0x6900`, forms voice `a0 = D_801496F8 + i*0x88`, and passes
`a3 = pingpong[byte][old_count]*0x88` into `musyxRenderVoiceSamples`.
That `a3` becomes render `s0`.

Render copies voice-table volume halfwords into that command-list record:

- `s1+0x18..+0x1E` → `s0+0x66,+0x68,+0x6A,+0x6C` (`0x80090974..0x8009098C`)
- if `s1[0]==1`, it first mirrors those four halfwords onto `s1+0x20..+0x26`
- then `s1+0x20..+0x26` → `s0+0x6E,+0x70,+0x72,+0x74` (`0x800909C4..0x800909DC`)

It also copies voice `s1+0x6D` (byte) to command-list `s0+0x21`.

`musyxBuildVoiceCommandList` walks `a0 + i*0x88` while `i < a1` and, when
byte `+0x22` is zero, calls `musyxKeyOnVoice` with that command-list
record as `a0`/`s0`. Key-on then:

- publishes `s0+0x6E..+0x74` left-shifted 16 into dest words `+0x0..+0xC`
- divides `(+0x66 - +0x6E)`, `(+0x68 - +0x70)`, `(+0x6A - +0x72)`, and
  `(+0x6C - +0x74)` by halfword `s0+0x60` into dest words `+0x10..+0x1C`

The dest is `D_80149750 + count*0xA10 + inner*0x50 + 0x10`. Both transfer
blocks share this tail; it is skipped when command-list `+0x21` is neither
0 nor 3. Existing divide traps return early. Mix bounds `i` by the live
slot-count halfword; that is a count bound, not a static 64-slot or
allocation-size proof. The inner key-on count is incremented with no local
check that it stays inside one `0xA10` block.

### 2. Global voice table (`D_801496F8`, stride `0x88`)

`musyxInitVoiceFromSample` computes `base + (a3 * 0x88)` from
`0x8015:-0x6908` and stores descriptor `a1+0x18` as a byte at `+0x6D`
(`0x80092238`). The first init block masks the index to 16 bits; this
`+0x6D` path reuses the original unmasked argument. The base has the
existing KSEG0 entry guard; the generated body does not prove the index
is below the live slot-count halfword at `0x8015:-0x6900`.

`musyxRenderVoiceSamples` reads that same voice-table byte three times
(`0x800901C8`, `0x8009046C`, `0x80090774`) as a 0-versus-3 decode-mode
switch, then publishes it to command-list `+0x21`.

`musyxTriggerVoiceAttack` writes byte `0` at `+0x6C` and word `0` at
`+0x68` after a 16-bit index mask and KSEG0 guard (`0x80092348`,
`0x80092350`). `musyxStartVoiceRelease` and `beginVoiceFadeRelease` write
byte `3` at `+0x6C` and copy the float at `+0x5C` into word `+0x68`.
Release uses the original unmasked `a0` and has no KSEG0 guard; fade uses
unmasked `a0` with a KSEG0 guard.

Those voice-table word/byte fields overlap the command-list halfword
offsets numerically but are a different object. No load of voice-table
`+0x68` or `+0x6C` exists in this file. The envelope tick that reads them
is `advanceVolumeFadeEnvelope` in `funcs_23.c`, outside this census.

## Result

`H-NextClassGap` is not selected: every non-stack store is an identified
truncated volume copy, a descriptor-byte copy, a `0`/`3` envelope phase,
a zero word, or a float copy from `+0x5C`. No wild constant or
demonstrably invalid writer was found.

`H-NextClassComplete` is not selected: the same spelling covers the
command-list volume halfwords and the voice-table envelope/mode bytes and
word; widths disagree; voice-table and inner key-on indices lack
caller-proven capacity checks; and the envelope word/byte consumers are
not in this file.

`H-NextClassUnevaluable` is selected. The independent evidence lines are
(1) the complete offset/type/base census in `funcs_24.c` and (2) the
control-flow derivation of the two bases (`D_801496F8` versus ping-pong
`D_80149708/0C`) plus the key-on dest at `D_80149750`. Runtime slot-count
contents, allocator size, envelope-tick legitimacy, and DMA timing remain
open. No guard or mitigation was added.

ORIGIN: command-list halfword writers are `musyxRenderVoiceSamples`
(copies of voice-table `+0x18..+0x26`). Voice-table `+0x6D` is written by
`musyxInitVoiceFromSample` from descriptor `+0x18`. Voice-table `+0x6C`/
`+0x68` writers are `musyxTriggerVoiceAttack` (zero),
`musyxStartVoiceRelease`, and `beginVoiceFadeRelease` (`3` and the `+0x5C`
float). Those values are legitimate state or copies from identified
sources; capacity and lifetime remain unproven.
