# Session 3220 — M3 musyxKeyOnVoice divisor/descriptor census (A8)

## Discriminator

The joined static table was every generated load at the eight trap PCs,
the backing record and field offsets, every generated store of those
fields, companion names, and caller fan-in. Competing outcomes:

- `H-NamedDescriptor`: every divisor loaded at the eight trap PCs is
  written by a named voice/channel descriptor path with a finite range.
- `H-InvalidDivisorProducer`: at least one generated store writes a zero,
  overflow, or non-voice value into a divisor field the traps are papering
  over.
- `H-NoLiveDivisorWriter`: the generated tree has no remaining store into
  those fields beyond already-named sites.

No port run. No trap removal without a named legitimate writer.

Positive control for this static census: companion `main_overlay.txt`
independently names `musyxKeyOnVoice` at `0x80090A3C` as computing four
envelope ramp deltas `/+0x60`, names `musyxBuildVoiceCommandList` as the
per-voice key-on walker, names `musyxRenderVoiceSamples` as the per-voice
resample/mix kernel, and names `allocateSongChannelArray` as the installer
of the `0x88`-stride arrays. Those addresses and the `* 0x88` index
arithmetic in the generated snapshot match.

## Trap-site load table

All eight sites are inside `musyxKeyOnVoice` (`0x80090A3C`), reached only
when cmd-list record `+0x21 == 3`. `$s0` is the first argument: a
`0x88`-stride record in the ping-pong cmd-list pair at `D_80149708` /
`D_8014970C` (`lui 0x8015` / `-0x68F8` indexed by the inverted byte at
`0x80149702`). Sole caller is `musyxBuildVoiceCommandList` at
`0x800910A8` (`jal 0x80090A3C`), itself called from `musyxSynthFrame` at
`0x80091330` with `$a0 = MEM_W[D_80149708 + (pingpong^1)*4]`.

Every divide uses the same unsigned-halfword divisor:

```
lhu $a0, 0x60($s0)
div $zero, $v0, $a0
bne $a0, $zero, skip   ; else break 7
addiu $at, $zero, -1
bne $a0, $at, skip     ; else if $v0 == 0x80000000: break 6
```

| Trap PC | MIPS | Divisor load | Numerator |
|---|---|---|---|
| `0x80090CEC` | `break 7` | `lhu 0x60($s0)` | `(lh 0x66 − lh 0x6E) << 16` → store `0x10($s1)` |
| `0x80090D04` | `break 6` | same `$a0` | same `$v0` |
| `0x80090D30` | `break 7` | `lhu 0x60($s0)` | `(lh 0x68 − lh 0x70) << 16` → store `0x14($s1)` |
| `0x80090D48` | `break 6` | same `$a0` | same `$v0` |
| `0x80090D74` | `break 7` | `lhu 0x60($s0)` | `(lh 0x6A − lh 0x72) << 16` → store `0x18($s1)` |
| `0x80090D8C` | `break 6` | same `$a0` | same `$v0` |
| `0x80090DB8` | `break 7` | `lhu 0x60($s0)` | `(lh 0x6C − lh 0x74) << 16` → store `0x1C($s1)` |
| `0x80090DD0` | `break 6` | same `$a0` | same `$v0` |

`lhu` zero-extends, so `$a0 ∈ [0, 65535]` and is never `-1`. The
numerators are `(s16 − s16) << 16`; the 32-bit shift cannot produce
`0x80000000`. All four `break 6` sites are unreachable at generated-source
scope.

The type-0 path at `L_80090BA0` (`+0x21 == 0`) does not divide. Any other
`+0x21` returns at `0x80090AA0` without dividing.

## Cmd-list `+0x60` publication (the actual divisor)

| Guest PC | Generated function | Operation | Value | Classification |
|---|---|---|---|---|
| `0x80090768` | `musyxRenderVoiceSamples` | `sh $s5, 0x60($s0)` | `$s5 = $a2` of the render call. All three `musyxSynthFrame` mix sites (`0x800914C0`, `0x80091580`, `0x80091634`) pass `addiu $a2, $zero, 0xC0`. Mix then `andi $a2, $s5, 0xFFFF` into render. | Sole live cmd-list divisor publisher. In-range (`0xC0`, never 0, never `-1`) |

`$s0` in render is `$a3 = pingpong_base + idx*0x88` with
`pingpong_base = MEM_W[D_80149708 + pingpong*4]` — the same record
family key-on reads, one ping-pong index later (`xori` of `0x80149702`
in the synth-frame build call).

Same-function companion stores on that record (not the divisor, but the
four envelope pairs key-on subtracts):

| Guest PC | Field | Source |
|---|---|---|
| `0x80090974` | `sh 0x66($s0)` | mixer-voice `lhu 0x18($s1)` |
| `0x8009097C` | `sh 0x68($s0)` | mixer-voice `lhu 0x1A($s1)` |
| `0x80090984` | `sh 0x6A($s0)` | mixer-voice `lhu 0x1C($s1)` |
| `0x8009098C` | `sh 0x6C($s0)` | mixer-voice `lhu 0x1E($s1)` |
| `0x800909C4` | `sh 0x6E($s0)` | mixer-voice `lhu 0x20($s1)` |
| `0x800909CC` | `sh 0x70($s0)` | mixer-voice `lhu 0x22($s1)` |
| `0x800909D4` | `sh 0x72($s0)` | mixer-voice `lhu 0x24($s1)` |
| `0x800909DC` | `sh 0x74($s0)` | mixer-voice `lhu 0x26($s1)` |
| `0x80090780` | `sb 0x21($s0)` | mixer-voice `lbu 0x6D($s1)` (type flag; divide path requires `3`) |
| `0x80090F3C` | `sb $zero, 0x22` | mix, after each render: arms next-frame key-on |
| `0x80090F8C` | `sb $1, 0x22` | mix, post-loop: marks the unused next slot so key-on skips it |

`allocateSongChannelArray` at `0x8008F294` / `0x8008F2B0` publishes the
two ping-pong mallocs into `D_80149708` / `D_8014970C`. Those mallocs are
not followed by `rs_memset` (the only memset in that function is the
separate `0x298`-byte block at `D_80149664`). First-frame inverted-buffer
`+0x60` is therefore uninitialized heap, which hardware also leaves
uninitialized. That is the game's own `break 7` case, not a generated
store of zero.

## Mixer-voice `+0x60` stores (different malloc; not the divisor)

These write `D_801496F8 + idx*0x88 + 0x60` (A9 mixer-voice array), which
is a distinct `rs_malloc` from the cmd-list pair. They overlay ADSR
runtime words (`+0x60`/`+0x64`/`+0x68` plus stage byte `+0x6C`) and are
not loaded by the eight trap sites.

| Guest PC | Function | Operation |
|---|---|---|
| `0x800922B0` | `musyxStartVoiceRelease` | `sw $zero, 0x60($a0)` |
| `0x8009234C` | `musyxTriggerVoiceAttack` | `sw $zero, 0x60($v1)` |
| `0x800924DC` | `beginVoiceFadeRelease` | `sw $zero, 0x60($a0)` |
| `0x8008F538`, `0x8008F5A4`, `0x8008F64C` | `advanceVolumeFadeEnvelope` | `sw $zero, 0x60($a0)` (same ADSR overlay; reads stage byte `+0x6C`) |

## Excluded same-offset stores (wrong record type)

`tickAudioChannel` `sw 0x60` is the `0x17C`-stride sequencer channel at
`0x8013D880` (companion size). `soundMacroOpPlaySampleKeymap` `sw 0x60`
is that same channel (`$s5+0x9C`/`+0xBD`/`+0x24`). NPC, menu, HUD, and
effect `MEM_H/W(0x60)` stores are unrelated objects. None index
`D_80149708`.

## Caller fan-in

| Guest PC | Function | Edge |
|---|---|---|
| `0x800910A8` | `musyxBuildVoiceCommandList` | sole `jal musyxKeyOnVoice`; `$a0 = base + idx*0x88` when `+0x22 == 0` |
| `0x80091330` | `musyxSynthFrame` | sole `jal musyxBuildVoiceCommandList`; `$a0` is inverted ping-pong cmd-list base |
| `0x80090F00` | `musyxMixActiveVoices` | sole `jal musyxRenderVoiceSamples`; `$a2` is the mix third argument |
| `0x800914C8`, `0x80091588`, `0x8009163C` | `musyxSynthFrame` | the three mix calls; each sets `$a2 = 0xC0` |

Synth-frame order is build (key-on last frame's rendered records) then
mix (write `+0x60 = 0xC0` and clear `+0x22`). That is why the live
divisor key-on observes is the previous mix's constant `0xC0`.

## Decision

`H-NoLiveDivisorWriter` is refuted: `musyxRenderVoiceSamples` at
`0x80090768` publishes the mix block length into cmd-list `+0x60`.
`H-InvalidDivisorProducer` is not selected at generated-source scope:
that store is constantly `0xC0`, and every other `+0x60` store is a
different record type. `H-NamedDescriptor` is selected for the live
divisor and the four envelope halfword pairs.

The four `break 6` traps are dead (unsigned-halfword divisor never
`-1`; shifted s16 difference never `INT_MIN`). The four `break 7` traps
are the game's own divide-by-zero handler; the only generated-source way
`+0x60` is zero is uninitialized ping-pong heap before the first render
of that buffer, which hardware also has. Existing early-return traps
stay safety machinery. No trap is removed or replaced.

This is static evidence only. A8's remaining retail/port in-range and
normal-tail key-on plus slot `0x02` then `0x00` requirement is still
blocked on a target-phase M5 route.

ORIGIN: generated guest-PC store/load census plus independent companion
symbol metadata; no mitigation or runtime behavior change was made.
