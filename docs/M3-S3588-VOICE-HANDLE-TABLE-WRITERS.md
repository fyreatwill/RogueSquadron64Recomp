# M3 s3588 — voice-handle table writer audit

## Work unit

Audit the complete `-0x271C` per-voice field writer class used by the
unchecked low-byte-to-`0x17C` voice-table lookups. The competing hypotheses
were bounded producers, an unsafe concrete writer, or a misidentified field /
table layout. The discriminator was a whole-tree writer census followed by
classification of every low-byte consumer.

## Census

There are three generated stores in `funcs_21.c` and `funcs_23.c`:

| Writer | Address | Value contract |
|---|---:|---|
| `stopVoiceByKey` | `0x80086984` | `-1`, after `allocateSynthVoice` failure/success handling; cleanup sentinel |
| `startNoteOnVoice` | `0x80087294` | composite handle assembled after successful allocator selection; slot component is allocator-selected |
| `resetMusyXEngineState` | `0x8008E660` | `-1`, for each reset slot; loop covers the initialized 0x20 records |

The low-byte consumers are the voice-handle scans in
`queryVoicePlayPositionByHandle`, `flagVoiceChainForStop`,
`soundMacroOpKeyOffByNote`, and `stopVoicesByHandle`. Each obtains the field
from a live matching handle/record or rejects `-1`; direct record scans are
bounded by the configured slot-count byte.

## Result

No concrete invalid writer or value was found. The writer side of this idiom
class is structurally closed as bounded/sentinel-valued, but runtime allocator
state, record lifetime, and stale packed-handle legitimacy remain unproven.
No guard or runtime change is authorized.

