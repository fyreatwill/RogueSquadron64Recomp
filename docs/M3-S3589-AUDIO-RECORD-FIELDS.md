# M3 s3589 — audio record field/table-address audit

This audit covers the generated audio path that reads record bytes `0x4E` and
`0x4F`, the `0x801483D0` table idiom (`0x80150000 - 0x7C30`), and all direct
writers of those offsets in the generated tree. The work unit was static; no
runtime instrument or guard was added.

## Competing hypotheses and discriminator

- **H-AudioRecordFieldsBounded:** every writer keeps the two selector bytes
  within the table dimensions, or publishes `0xFF` for the fallback table.
- **H-AudioRecordFieldsUnsafe:** a concrete writer publishes an invalid value
  that reaches a computed table address.
- **H-AudioRecordFieldsMisread:** the apparent fields or table layout are not
  the audio record/table described by the generated control flow.

The discriminator is exhaustive site enumeration: every distinct writer PC,
every `-0x7C30` consumer, and each writer's source/bounds or sentinel path.
Unsafe is selected only by a concrete writer and value.

## Results

The generated tree contains 29 distinct instruction PCs writing offset
`0x4E` or `0x4F`. Most are false matches for this audio record: 17 write
stack locals, and the remaining non-audio object sites are in DMA/manifest,
NPC/effect, menu, and vehicle structures. The audio-record candidates are:

| Writer PCs | Generated function | Source / classification |
|---|---|---|
| `0x80090B70`, `0x80090C50` | `musyxKeyOnVoice` | Stores a halfword loaded from source record `+0x64` into destination `+0x4E`. The destination is the selected MusyX voice slot; selection follows the table lookup and the `-1` allocation failure check. The low-byte range of source `+0x64` is not proven by this static pass. |
| `0x8008BD50`, `0x8008BD5C` | `tickAudioChannel` | Copies source bytes `+0x59` and `+0x58` back into the same channel record's `+0x4F` and `+0x4E`. The copies are structurally legitimate, but the upstream writers/ranges for `+0x58/+0x59` are not established here. |

The other direct object writers are not this record: `0x800ECCBC` and
`0x800ECD10` operate on a vehicle/NPC object, `0x800BA508` and `0x800BA684`
operate on menu data, and the earlier sites in `funcs_1.c`, `funcs_10.c`,
`funcs_13.c`, `funcs_17.c`, `funcs_18.c`, `funcs_19.c`, `funcs_20.c`,
`funcs_21.c`, `funcs_37.c`, `funcs_38.c`, and `funcs_39.c` are manifest,
effect, NPC, or stack-local fields. Conditional duplicate C arms were
collapsed by guest instruction PC.

There are 13 distinct `-0x7C30` consumer PCs:

- `0x80083EC4`, `0x80083F20`, `0x800844E0` in channel byte get/set and reset;
- `0x80086F68`, `0x80087510`, `0x800879D8`, `0x80087C0C` in voice lookup and
  sequencer dispatch;
- `0x8008BA28` in `refreshVoicePlaybackRate`;
- `0x8008BB50`, `0x8008BBCC` in `soundMacroSetPitchTarget`; and
- `0x8008CD84`, `0x8008CE10` in `tickAllAudioChannels`.

Each consumer first checks its row/column selector against `0xFF` and uses a
separate per-channel fallback table when the selector is `0xFF`. The ordinary
address is `base + (row << 4) + column`; the code masks selector arguments to
8 bits where they originate as call arguments. No consumer adds an explicit
upper bound below `0xFF`, so the table's true dimensions and the two audio
record source ranges remain a runtime/data-flow boundary, not a proved bound.

## Verdict

`H-AudioRecordFieldsUnsafe` is **not selected**: no concrete invalid writer
and value was found. `H-AudioRecordFieldsMisread` is also not selected: the
shared get/set/reset helpers, sentinel fallback branches, and the target
function all use the same consistent row/column table idiom. The boundary is
**unclassified**, because `musyxKeyOnVoice` depends on source `+0x64` and
`tickAudioChannel` depends on `+0x58/+0x59`, whose runtime value provenance is
not established by this census.

No mitigation is authorized. There is no ORIGIN-backed guard to add: the
identified writers are legitimate game-side writes, and their values were not
observed to be invalid.
