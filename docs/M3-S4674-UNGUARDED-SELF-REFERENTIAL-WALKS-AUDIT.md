# M3 s4674 — unguarded self-referential `MEM_W` walks

## Work unit and discriminator

This audit covers the complete generated-tree idiom in which a backward branch
re-enters a label followed within four generated statements by
`MEM_W(ctx->rN, 0X0)` using the same register as both address and result. It is
not a single crash-site audit. The candidate script found 30 sites in 14
functions and eight generated files.

The competing hypotheses were:

- H-safe-loop: every site is a legitimate sentinel/list or bounded table walk;
- H-unguarded-invalid: a reachable site has a named writer that can publish a
  non-KSEG0 or otherwise invalid pointer;
- H-incomplete-census: the generated tree or detector is stale/incomplete.

The discriminator was a same-tree complete census plus an independent exact
scan, followed by classification of every site. The independent scan also
returned 30 sites. The known heap-list control is present separately at
`heapFreeListInsert` / `0x800079B8`; its existing `alloc-tail-guard3` probe
and adjacent guard probes provide the positive control that the generated tree
contains the guarded free-list idiom. No runtime or oracle null was used, so
this result does not claim that any route is dynamically safe.

## Complete classification

| Generated function(s) | Sites | Classification | Writer / legitimacy result |
|---|---:|---|---|
| `model_animation_offset_convert` | 1 | bounded animation table/index walk | Base comes from the model-animation object and the loop advances through the decoded table; no non-KSEG0 writer identified. |
| `tickAudioChannel` | 1 | audio record pointer walk | The record link is written by the audio-channel setup path; this is covered by the existing M5 audio pointer/slot evidence, not a new M3 guard selection. |
| `stopSongByHandle` | 2 | two sentinel-terminated song-list walks | Head fields are song-list state owned by song setup/teardown; no alternate non-allocator writer found in this scan. |
| `tickSongSequence` | 2 | two sentinel-terminated song-list walks | Same song-list head/next contract; no invalid writer attribution. |
| `cutsceneDispatchSlotsByFlag` | 2 | bounded flag-slot table walks | The address is computed from the slot index and compared against the searched value; these are not allocator-linked-list walks. |
| `commitMeshDrawBatchRefs` | 3 | three render-reference list walks | Heads come from the mesh draw-batch object; the surrounding KSEG0 selection and null termination are existing game logic. No invalid writer proven. |
| `renderLitTexturedMeshFaces` | 5 | light/texture reference list walks | Heads are loaded from validated mesh/material records and each walk is null-terminated. No named writer can produce an invalid pointer from static evidence. |
| `playSpeechClipOncePerLevel`, `resetSpeechOncePerLevelFlag` | 2 | bounded cinematic/speech slot-table walks | Index arithmetic and searched sentinel bound the table; not a free-list class. No invalid writer identified. |
| `tickCinematicObjectStateMachine` | 8 | bounded cinematic dispatch-table walks | Each walk is an indexed table search with a sentinel comparison; no arbitrary pointer writer is involved. |
| `freeModelViewerMeshChain` | 1 | mesh-chain next-pointer walk | Initial head is object-owned and null-tested; append/destructor paths write the chain. The free target is separately null-tested. No invalid writer proven. |
| `appendNodeToListTail`, `appendNodeToListHead` | 2 | list insertion walks | These are writers of the list being traversed, with null termination and allocator-created nodes; they are not evidence of a bad value by themselves. |
| `renderUnlitMeshFaces` | 1 | render-reference list walk | Existing fixup contains the unguarded peek-load guard instrumentation at this site; no runtime fire was observed in the qualified M5 route, but that is not used as a global null. |

The 30 sites therefore split into 17 bounded/sentinel table or audio-list
walks, 12 render/mesh/list walks, and one already instrumented unlit-render
peek-load. None has a statically attributable writer that is shown to publish
an invalid pointer. The site count and per-function grouping are independently
reproduced by the two scans; the positive-control guard is present in source.

## Result and policy

H-safe-loop is selected provisionally for this static class. H-unguarded-invalid
is not selected because no writer/legitimacy pair demonstrates an invalid
value. H-incomplete-census is not selected because the exact independent scan
matches the 30-site result and the guarded heap-list control is present.

No guard, skip, or mitigation is authorized. A future runtime discriminator
must name one writer and prove the value is legitimate or illegitimate before
changing any of these walks. The next M3 unit should choose a different
complete idiom class rather than adding another field to this census.

ORIGIN: no mitigation or behavior change; the candidate pointers are written
by the named object/list/table setup paths described above, and no illegitimate
writer was established.
