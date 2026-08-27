# s2503 M5 AI-buffer writer provenance audit

## Scope

Static census only; no build or runtime change. The active root is
`D_801496B0` (`0x80150000 - 0x6950`). The superseded `0x801096B0` address was
not used as a candidate.

## Producer-to-consumer table

| Guest PC | Operation | Destination / value | Consumer relation |
|---|---|---|---|
| `0x8008EDA4` | `sw $v0, 0($v1)` after `rs_malloc(0x3000)` | `D_801496B0 = heap_base` | Root table read at `0x8008EDD0` |
| `0x8008EDB8` (loop, 16 iterations) | `sw $v0, 0($a0)` after adding `0x300` | `D_801496B0[1..15] = heap_base + 0x300..0x2D00` | Entries are the table used by the second AI path |
| `0x8008EDE0` | `rs_memset(heap_base, 0, 0x3000)` | Clears the complete allocation | Establishes the allocated region before AI submission; not a PCM payload writer |
| `0x8008EE00` | `osAiSetNextBuffer(rdram, ctx)` | `a0 = D_801496B0[0]`, `a1 = 0x300` | Direct first AI consumer |
| `0x8008EE84` | `osAiSetNextBuffer(rdram, ctx)` | `a0 = D_801496B0[index]`, `a1 = 0x300` | Direct indexed AI consumer |

The active generated tree has one root-table store site (`0x8008EDA4`), one
derived-entry store idiom (`0x8008EDB8`, repeated by the loop), and exactly two
`osAiSetNextBuffer_recomp` callsites, both in
`runAiAudioStreamPlaybackLoop`. No other active generated source matched the
root address or its fixed `-0x6908` alias as a store. Other `-0x6950` matches
are structure-field offsets using non-root bases and do not target
`D_801496B0`.

## Independent companion evidence

- `rogue_squadron64/undefined_syms_auto.txt` lists `D_801496B0 = 0x801496B0`.
- `rogue_squadron64/symbol_files/main_overlay.txt` names
  `runAiAudioStreamPlaybackLoop = 0x8008ED70`.
- The active generated function at that address contains the allocation,
  root store, sixteen-entry initialization, clear, and both AI calls.

## Result

`H-writer-generated` is selected for the requested allocation/table producer
boundary: an active generated game-side function produces the buffers consumed
by both AI submissions. This does **not** prove that the generated code writes
nonzero PCM samples into those buffers; the clear is the only content-wide
write established by this census. A follow-up must locate the producer of the
PCM payload inside the allocated 0x300-byte blocks, if one exists.
