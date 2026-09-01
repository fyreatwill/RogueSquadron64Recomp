# M5 session 3577 — retail remaining zero-fill edge

The retail oracle ran the remaining `0x800C825C` predecessor watch with the
whole-RDRAM and source-span positive controls. The run reached the target
hangar bucket `0x006AB400:512` and recorded:

- whole-RDRAM writes: 10,674;
- source-span writes in `0x1797B0..0x179930`: 674;
- `0x800078E0` executions: 3,166;
- `0x800C825C` executions: 2,260;
- entry predecessor joins from `0x800C825C`: 2,259.

The retained `0x800C825C` rows show `a2=0x80` and a changing structure pointer
in `a0`; the immediately joined `0x800078E0` rows preserve that `a2=0x80`.
This differs from the port tuple `dst=0x801797B0`, `fill=0`, `len=0x298`.
The target entry was therefore live and the predecessor was positively
observed, but this edge does not reproduce the port's zero-fill input.

This selects `H-RemainingEdgeInput` and leaves source-DMA ordering and the
legitimate retail writer context open. The result is independent retail
evidence for the edge/input divergence; exact retail-to-port source-DMA
ordering was not measured in this run. No game state, output, PCM, task, DMA,
or source contents were changed.

ORIGIN: diagnostic-only retail predecessor/entry qualification. No mitigation
was added.
