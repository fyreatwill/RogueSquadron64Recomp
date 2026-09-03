# M3 s3599 — MusyX voice-table envelope companion `+0x5C`/`+0x64`

## Work unit

Static census of every generated `MEM_[BHW]` access to offsets `0x5C` and
`0x64` in `../N64Recomp/RecompiledFuncs/funcs_23.c` and `funcs_24.c`.
No build or runtime run was performed.

The discriminator was a complete writer → consumer → base/layout →
lifetime/bound chain spanning both files, including the
`advanceVolumeFadeEnvelope` edges left outside s3598: a concrete invalid
edge selects `H-NextClassGap`; complete structural coverage of one object
selects `H-NextClassComplete`; mixed or missing layouts select
`H-NextClassUnevaluable`.

## Census size

36 offset matches: 17 in `funcs_23.c` and 19 in `funcs_24.c`. Delay-slot
duplicates are counted. Two of the `funcs_23.c` hits are `tickAudioChannel`
prologue/epilogue spills at `r29+0x5C` and are not voice fields.

`musyxInitVoiceFromSample` does not touch these offsets. Mix and the
command-list builder only pass pointers into render.

## Distinct layouts

The remaining accesses are not one record.

### 1. Global voice table (`D_801496F8`, stride `0x88`) — envelope floats

Base is `0x8015:-0x6908`. Index formula is `i*0x88`. Attack masks `a0` to
16 bits and has the existing KSEG0 entry guard. Release uses the original
unmasked `a0` and has no KSEG0 guard. Fade uses unmasked `a0` with a KSEG0
guard. The envelope tick takes a pointer, not an index.

`musyxTriggerVoiceAttack` (`0x80092354`, `0x80092358`) writes word `0` at
`+0x5C` and a rodata float at `+0x64` (`0x80040000-0x21A0`), zeros
`+0x60`/`+0x68`, sets phase byte `+0x6C` to `0`, sets `+0x0` to `1`, and
stores attack duration `+0x28` into `+0x58`.

`musyxStartVoiceRelease` and `beginVoiceFadeRelease` copy float `+0x5C`
into `+0x68`, write word `0` at `+0x64` and `+0x60`, set `+0x6C` to `3`,
and copy halfword `+0x30` into `+0x58`. Release also forces `+0x30` to
`0x14` first. Fade skips that envelope block when `+0x0==0` or `+0x1!=0`.

`advanceVolumeFadeEnvelope` is the only tick. Render calls it once per
active voice with `a0 = s1` (the mix-computed `D_801496F8 + i*0x88` slot)
and `a1` the 16-bit sample-count argument. Mix skips `+0x0==0` before that
call, so init's inactive zero at `+0x0` gates the tick until attack.

The tick:

- when `+0x1==0` and `+0x6C!=3`, auto-releases: `+0x6C=3`, `+0x64=0`,
  `+0x60=0`, copies `+0x5C` to `+0x68`, copies `+0x30` to `+0x58`
- when progress `+0x60` has reached duration `+0x58`:
  - phase `0` → `1`, `+0x68` = rodata float `0x80040000-0x2270`,
    `+0x64` = sustain float `+0x2C`, `+0x58` = `+0x2A`
  - phase `1` → `2`, copies `+0x2C` onto `+0x68`, `+0x64`, and `+0x5C`
  - phase `3` zeros `+0x5C` and stores `0` at `a2+0`
- otherwise interpolates `+0x5C = +0x68 + (+0x64 - +0x68) * t` and adds
  the scaled sample-count into `+0x60`. Zero duration uses rodata
  `0x80040000-0x2260` instead of dividing.

Render then loads voice-table `+0x5C` four times (`0x800908F4`..
`0x80090930`) as the volume multiplier for halfwords `+0x44..+0x4A`,
truncating into `+0x18..+0x1E`.

Init never writes `+0x5C`/`+0x64`/`+0x68`/`+0x6C`. Lifetime order is
init (`+0x0=0`) → attack (active + envelope reset) → tick/render →
release/fade. Mix's live slot-count halfword at `0x8015:-0x6900` bounds
the render loop; that is a count bound, not a static 64-slot or
allocation-size proof. Release/fade indices are not checked against that
count.

### 2. Command-list ping-pong (`D_80149708` / `D_8014970C`, stride `0x88`)

Render `s0` is the command-list record mix built as
`pingpong[byte][old_count]*0x88`. It stores halfword `s3` at `s0+0x64`
on four sample-stream arms (`0x800902D4`, `0x80090400`, `0x80090520`,
`0x80090668`). `s3` is `0` or `pos - loop_start` from voice `+0x3C`.
It stores a derived sample-end word at `s0+0x5C` (`0x80090718`) from
`+0x48`/`+0x4A` plus the stream cursor.

`musyxKeyOnVoice` consumes those as unsigned halfword `s0+0x64` copied
to dest `+0x4E` and word `s0+0x5C` copied to dest `+0x4A`. The dest is
`D_80149750 + count*0xA10 + inner*0x50 + 0x10`. Widths are halfword/word,
not the voice-table envelope floats. s3589/s3590 already classified the
`+0x4E` publication; this census only identifies the command-list side.

### 3. Synth-voice packed handle (`0x17C` stride)

`tickAudioChannel`, `releaseSynthVoice`, `stopVoicesByHandle`, and
`stopAllSynthVoices` store a word at record `+0x64`. Those are the
packed-handle / `-1` sentinel writers already enumerated in s3586/s3588.
They are not envelope floats.

## Result

`H-NextClassGap` is not selected: every non-stack store is an identified
envelope reset (zero, sustain copy, or rodata float), an interpolated
current volume, a command-list sample cursor/offset, or a packed-handle
sentinel/composite. No wild constant or demonstrably invalid writer was
found.

`H-NextClassComplete` is not selected: the same spelling covers envelope
floats, command-list sample halfword/word fields, and the `0x17C` packed
handle; widths disagree; voice-table release/fade indices and the mix
slot-count lack caller-proven capacity checks.

`H-NextClassUnevaluable` is selected. The independent evidence lines are
(1) the complete offset/type/base census in both files and (2) the
control-flow derivation of the three bases (`D_801496F8`, ping-pong
`D_80149708/0C`, and the `0x17C` synth-voice record) plus mix's `+0x0`
gate into the envelope tick. That closes s3598's hole that the envelope
consumers lived only in `funcs_23.c`. Runtime slot-count contents,
allocator size, release-index legitimacy, float values, and DMA timing
remain open. No guard or mitigation was added.

ORIGIN: voice-table `+0x5C`/`+0x64` writers are `musyxTriggerVoiceAttack`
(zero current, rodata target), `musyxStartVoiceRelease` /
`beginVoiceFadeRelease` (zero target, copy current to `+0x68`), and
`advanceVolumeFadeEnvelope` (interpolation, sustain copy, or zero).
Command-list writers are `musyxRenderVoiceSamples` (`s3` and the derived
sample-end word). Packed-handle writers are the s3586 cleanup/publish
set. Those values are legitimate state or copies from identified
sources; capacity and lifetime remain unproven.
