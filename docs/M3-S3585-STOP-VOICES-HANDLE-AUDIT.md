# M3 s3585 — `stopVoicesByHandle` handle-provenance audit

## Question and discriminator

This complete static idiom audit tests three alternatives:

- `H-HandleBounded`: every consumer handle and copied slot index is produced
  by a bounded voice-record contract.
- `H-HandleUnsafe`: a caller reaches the consumer with an unchecked,
  concrete invalid handle or slot index.
- `H-HandleMisread`: the node fields or voice-record layout were identified
  incorrectly.

The discriminator is an enumeration of every direct consumer edge and the
full visible constructor/validator chain. The class closes only if each edge
is bounded or has a concrete invalid writer; an unresolved writer remains
unclassified.

## Enumeration

`stopVoicesByHandle` is at `0x8008DA98` in `funcs_23.c`. The generated tree
has four direct call sites, all in the same generated function at
`0x800958E4`/`0x8009590C` and `0x80095B90`/`0x80095BBC`:

| Site | Input construction | Traversal |
|---|---|---|
| `0x8009590C` | `lw a0, 0x8(s0)` | `s0 = list_head+0xE78`, then `s0 = s0->next` |
| `0x80095930` | `lw a0, 0x8(s0)` | same `+0xE78` list |
| `0x80095BBC` | `lw a0, 0x8(s0)` | `s0 = list_head+0xE7C`, then `s0 = s0->next` |
| `0x80095BE0` | `lw a0, 0x8(s0)` | same `+0xE7C` list |

No register-indirect call to `0x8008DA98` was found in the generated tree.

The visible node constructor is `allocVoiceHandleNode` at `0x80086450`.
It maintains the sorted handle list rooted at `0x8013AF00` (`0x8014-0x5100`),
links nodes through offsets `+0` and `+4`, stores the generated handle at
`node+0x8`, and stores `voice_record+0x64` at `node+0xC`. The companion map
describes the same structure and names `D_8013D880` as a 32-record table with
`0x17C` stride and `0x80141AD0` as the active count.

The consumer walks the sorted list by `node+0x8`, rejects a missing handle,
loads `node+0xC`, masks the handle to eight bits, and indexes the voice table
with that masked value. It checks the table entry's stored handle before
releasing the record. There is no local comparison of `node+0xC` against the
active count or the fixed 32-record capacity.

## Result

`H-HandleMisread` is refuted at static scope: generated offsets, list links,
companion symbols, and the 32-record/`0x17C` layout agree.

`H-HandleUnsafe` is not selected as a concrete defect. The consumer has an
unchecked slot-index boundary, but this audit did not find a writer that
actually produces an invalid `voice_record+0x64` value. The visible producer
copies that field from the voice record; `allocateSynthVoice` uses a bounded
voice-slot search, but the complete writer/lifecycle provenance of the field
is not established by these generated call edges.

`H-HandleBounded` is also not proven. The four callers are structurally
consistent linked-list consumers, and the node constructor is internally
consistent, but runtime legitimacy of the copied slot field remains open.
This is a single-source static result. No guard, runtime instrument, build,
or behavior change is authorized.

ORIGIN: no mitigation was added. The unresolved value originates at the
`voice_record+0x64` writer/lifecycle boundary; its legitimacy is unknown.
