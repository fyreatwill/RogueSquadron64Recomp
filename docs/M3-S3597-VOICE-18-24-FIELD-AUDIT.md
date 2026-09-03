# M3 s3597 — MusyX voice `+0x18..+0x24` field audit

## Work unit

Static census of every generated access to offsets `0x18`, `0x1A`, `0x1C`,
`0x1E`, `0x20`, `0x22`, and `0x24` in `../N64Recomp/RecompiledFuncs/funcs_24.c`.
No build or runtime run was performed.

The discriminator was a complete writer → consumer → base/layout →
lifetime/bound chain: a concrete invalid edge selects `H-NextClassGap`;
complete structural coverage of one object selects `H-NextClassComplete`;
mixed or missing layouts select `H-NextClassUnevaluable`.

## Census size

81 offset-first stores and 81 offset-second loads matched the family. 48 of
the stores and 48 of the loads are `r29` prologue/epilogue spills in
`musyxRenderVoiceSamples`, `musyxKeyOnVoice`, `musyxBuildVoiceCommandList`,
`musyxSynthFrame`, `initN64RspMixer`, `initAudioSubsystem`,
`reapplyAudioConfig`, `shutdownAudioEngine`, `setVoiceModulationParams`,
the resample/copy helpers, and `expandBytesToPcm16ViaTable`. Those are not
voice fields.

`musyxStartVoiceRelease`, `musyxStoreVoiceAdsrParams`, and
`musyxTriggerVoiceAttack` have no access in this offset window.

## Distinct layouts

The remaining accesses are not one record.

### 1. Global voice table (`D_801496F8`, stride `0x88`)

`musyxInitVoiceFromSample` computes `base + (index16 * 0x88)` from
`0x8015:-0x6908`, then writes zero halfwords at `+0x18`, `+0x1A`, `+0x1C`,
`+0x1E`, `+0x20`, `+0x22`, and `+0x24` (`0x80092164..0x8009217C`). The
index is reduced to 16 bits and the base has the existing KSEG0 entry
guard; the generated body does not prove the index is below the live
slot-count halfword at `0x8015:-0x6900`.

`musyxRenderVoiceSamples` takes `a0` as that same voice slot (mix passes
`D_801496F8 + i*0x88`). It writes computed truncated-float volumes as
halfwords at `s1+0x18..+0x1E` (`0x80090948..0x80090970`), copies them to
the command-list working record at `s0+0x66..+0x6C`, then — when
command-list `s1[0]==1` — mirrors `+0x18..+0x1E` onto `+0x20..+0x26` and
copies `+0x20..+0x26` to `s0+0x6E..+0x74`. The same halfwords are then
written again at `0x800909F8..0x80090A00`. Mix bounds `i` by the live
slot-count halfword; that is a count bound, not a static 64-slot proof.

`musyxKeyOnVoice` reads source `s0+0x24` as a halfword on both transfer
blocks (`0x80090AA8`, `0x80090BA0`) and copies it to the command dest
`s1+0x22`. That source is the voice-table volume/pitch halfword above.

### 2. Command-list ping-pong (`D_80149708` / `D_8014970C`, stride `0x88`)

`musyxMixActiveVoices` does not write these offsets on the voice table.
After each `musyxRenderVoiceSamples` call it stores byte `0` at
`pingpong[byte][old_count]+0x22` (`0x80090F3C`). After the voice loop it
stores byte `1` at `pingpong[byte][final_count]+0x22` (`0x80090F8C`).
Those are terminator/key-on flags on the command-list malloc, not on
`D_801496F8`.

`musyxSynthFrame` calls `musyxBuildVoiceCommandList` with `a0 =
D_80149708[pingpong^1]` and `a1` equal to the matching count halfword at
`0x8015:-0x68F0`. The builder walks `a0 + i*0x88` while `i < a1`, reads
byte `+0x22`, and calls `musyxKeyOnVoice` when the flag is zero. The loop
is count-bounded; the allocation size behind that count is not proven
here.

`musyxRenderVoiceSamples` copies voice `s1+0` (byte) to command-list
`s0+0x20` and voice `s1+4` (halfword) to command-list `s0+0x24`
(`0x80090720`, `0x80090728`). Adjacent to the mix flag at `+0x22`, not
overlapping it.

### 3. Key-on dest record (`D_80149750`, outer stride `0xA10`, inner `0x50`)

`musyxKeyOnVoice` builds `s2 = D_80149750 + count*0xA10` from
`0x8015:-0x68B0` / `-0x68A0`, then `s1 = s2 + s2[0]*0x50 + 0x10`. On each
live transfer block it writes:

- halfword `s1+0x22` from source `s0+0x24`
- halfword `s1+0x20` from a truncated pitch (optionally OR `$a0` with
  `0x80000000`)
- word `s1+0x24` from source `s0+0x28` (the already-audited `+0x28`
  copy)
- words `s1+0x18` and `s1+0x1C` from signed division of voice
  `+0x6A/+0x72` and `+0x6C/+0x74` by `+0x60` (`0x80090D94`,
  `0x80090DD8`), behind the existing divide traps

The inner count at `s2+0` is incremented on the normal tail. No local
check proves that count stays inside one `0xA10` block.

### 4. Sample descriptor and resample parameter block

`musyxInitVoiceFromSample` reads descriptor `a1+0x18` as a byte and
stores it at voice `+0x6D` (`0x80092234`). That is not the voice-table
halfword at `+0x18`.

The resample/copy helpers (`resampleVoicePointTableSamples`,
`resampleVoiceLutSamples`, `resampleVoiceConstantSamples`,
`resampleVoiceLutSamplesPacked`, `copyVoiceSamplesS16`,
`copyVoiceSamplesLut`) load words at `a0+0x18` and `a0+0x1C` from a
caller-supplied parameter block. They are reached through the function
pointer at `0x8015:-0x6620` with `a0` set from the caller's `a1`. That
block is a separate layout from the voice-table halfwords; joining it to
the key-on dest words is not proven in this file.

## Result

`H-NextClassGap` is not selected: every non-stack store is an identified
zero, a `0/1` command-list flag, a truncated computed volume/pitch, or a
copy from a named source field. No wild constant or demonstrably invalid
writer was found.

`H-NextClassComplete` is not selected: the same spelling covers at least
four objects (voice table, command-list ping-pong, key-on dest,
descriptor/param block), widths disagree across those objects, and the
voice-table and inner key-on indices lack caller-proven capacity checks.

`H-NextClassUnevaluable` is selected. The independent evidence lines are
(1) the complete offset/type/base census in `funcs_24.c` and (2) the
control-flow derivation of the four bases (`D_801496F8`, ping-pong
`D_80149708/0C`, `D_80149750`, and the descriptor/param pointers).
Runtime slot-count contents, allocator size, and value legitimacy remain
open. No guard or mitigation was added.

ORIGIN: voice-table halfword writers are `musyxInitVoiceFromSample`
(zero) and `musyxRenderVoiceSamples` (computed volumes). Command-list
byte `+0x22` writers are the two `musyxMixActiveVoices` stores (`0` after
render, `1` as terminator). Key-on dest writers are `musyxKeyOnVoice`.
Those values are legitimate state or copies from identified sources;
capacity and lifetime remain unproven.
