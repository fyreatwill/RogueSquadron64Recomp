# Session 3119 — remaining `requestViFeatureChange` callers

The audit target was the complete remaining caller set named in `NEXT.md`.
The callee at `0x8001B7B8` stores `$a0` directly to pending VI word
`0x80128E90` (`0x8013-0x7170`); each row below is a real request-mask edge,
but not necessarily the publication edge that changes the VI descriptor.

| guest PC | generated function | argument provenance | static phase classification | can explain 640→1024? |
|---|---|---|---|---|
| `0x80044BAC` | `cutsceneActorNpcHandler` | `MEM_W(0x80138898)` loaded immediately before the call; dynamic global value | mission/cutscene actor maintenance; the same function dispatches actor slots and then begins a scene-render frame | no evidence of the title transition; caller is not a title-mode handoff |
| `0x800AFA70` | `tickCraftSelectScreen` (duplicate overlay record `static_5_800AF6AC`) | immediate constant `1` | menu/craft-select tick; follows asset release and clears menu state | no; menu tick is pre-title/menu lifecycle |
| `0x800AF644` | `cinematicDeactivator` | immediate constant `8`, reached only when cinematic state exists and feature bit `0x80` is absent | cinematic teardown | no; it is an end-of-cinematic cleanup request |
| `0x800B42BC` | `destroyPlayerShipRecord` | immediate constant `8`, reached only when the global player-ship record exists and its counter is decremented | player-ship record cleanup | no target-phase publication path is present |
| `0x800ADB34` | `updateHangarBayScene` | function input `$a0`, copied to `$s4` at `0x800AB660` and forwarded unchanged | hangar scene update; call follows `beginSceneRenderFrame($s3 & 0xffff)` | post-transition hangar path, not the 640→1024 title transition |

The dynamic argument in the first row is not enough to promote that caller:
its surrounding code is actor-slot processing, and there is no static edge to
the title VI publication. The hangar row is the only caller with an explicit
target-phase scene identity, but its phase is after the missing transition and
cannot account for it.

## Result

This selects `H-AlreadyEnumerated` for the current 640→1024 boundary: the five
remaining request callers are pre-title cleanup/maintenance, or post-transition
hangar work. The missing writer is outside this caller family. This is a static
classification only; no retail attribution was performed in this work unit.

## Next retail probe

Do not repeat the closed direct-callsite/helper watches or `0x800C2984`.
Enumerate the next handoff family around the VI descriptor/publication state,
starting with retail PC attribution for the first store or call immediately
after `requestViFeatureChange`'s pending-word write and before the descriptor
becomes `1024`. The probe must include the whole-RDRAM write positive control,
title/hangar VI phase controls, and a complete PC histogram for the interval.
