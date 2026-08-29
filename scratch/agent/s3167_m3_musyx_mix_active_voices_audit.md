# Session 3167 — `musyxMixActiveVoices` voice-record index audit

## Scope

Complete static audit of `musyxMixActiveVoices` (`0x80090E04`) and the
producer of its voice-array count. No build, run, generated-source edit, guard,
or audio behavior change was performed.

## Evidence table

| Guest PC | Access | Index/data-flow proof |
|---|---|---|
| `0x80090E8C` | `lbu voice[index*0x88+0x85]` | `s0` starts at zero and the loop continues only while `s0+1 < count` |
| `0x80090EC4` | `lbu voice[index*0x88+0]` | same `s0`, same dominating loop bound |
| `0x80090EA8` | `lbu voice[index*0x88+0x84]` | same derived record pointer as `0x80090E8C` |
| `0x80090F3C` | `sb 0, voice[index*0x88+0x22]` | uses the current record's `0x88`-stride address |
| `0x80090F8C` | `sb 1, voice[index*0x88+0x22]` | uses the post-loop current record for the same bounded voice |
| `0x80090FC0` | `sw frame_ptr, voice[index*0x88+0x7C]` | same bounded record index after the loop |

The base pointer is loaded from `0x801496F8` and the function's loop count is
loaded from `0x80149700`. `initN64RspMixer` (`0x8009189C`) receives the count,
uses `andi 0xFFFF`, and replaces any value not below `0x21` with `0x20` before
`allocateSongChannelArray` stores the count at `0x80149700` (`0x8008F0CC`).
The mixer increments `s0` after each record and branches only while the
incremented value is below that stored count. Therefore every accessed index
is `0..31`, matching the 32-entry `0x88`-stride voice array.

All three reachable callers are the `musyxSynthFrame` blocks at
`0x800914C8`, `0x80091588`, and `0x8009163C`; each passes the current output
block and the same voice-array state. No alternate caller or indirect entry
was found in the generated snapshot.

The companion symbol file names `musyxMixActiveVoices` at `0x80090E04` and
documents the `0x801496F8` base and `0x88` stride. The companion ELF independently
exports `musyxMixActiveVoices` at `0x80090E04` and `initN64RspMixer` at
`0x8009189C`.

## Result

`H-M3-Proven` is selected. `H-M3-Unclassified` is rejected for this complete
class because the count clamp and loop bound dominate all indexed accesses;
`H-M3-Dead` is rejected because the function has three reachable generated
callers. No guard or mitigation is authorized by this audit.
