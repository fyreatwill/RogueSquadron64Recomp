# s2416 — M5 title-to-hangar handoff audit

Observation-only reduction of the two valid image captures. The title key-on
is the `kind=keyon-w40` event. PCM rows are the first five source records after
the first phase-12/hangar task; each source has an adjacent consumer row with
the same tuple.

| capture | title key-on | title task identity | first hangar task identity | first hangar DMA destinations | first five PCM guest addresses | result |
|---|---|---|---|---|---|---|
| s2412 | event 5288, phase 8, origin `0x790400`, ordinal/row `580/580`, dest `0x80173B30`, values `0x27/0x00276578` | `data_ptr=0x80173CB0`, ABI event 12917 | ordinal/row `822/241`, phase 12, origin `0x6AB400`; `data_ptr=0x80173CB0` | `0x167050..0x167350`, `0x1798B0..0x179A48` | `0x80169150`, `0x80166450`, `0x80166750`, `0x80166A50`, `0x80166D50` | no stable ordinal/row, event, or destination continuation |
| s2413 | event 5321, phase 8, origin `0x790400`, ordinal/row `585/585`, dest `0x80173B30`, values `0x27/0x00276578` | `data_ptr=0x80171E70`, ABI event 13129 | ordinal/row `783/197`, phase 12, origin `0x6AB400`; `data_ptr=0x80171E70` | `0x169150..0x169450`, `0x1798B0..0x179A48` | `0x80167350`, `0x80167650`, `0x80167950`, `0x80167C50`, `0x80167F50` | no stable ordinal/row, event, or destination continuation |

The title key-on shape is identical across captures at `site=0x80090C28`,
`dest=0x80173B30`, and values `0x27/0x00276578`, but its task ordinal differs.
The first hangar task and first 0x300-byte destination also differ. The shared
second 0x198-byte DMA role is insufficient to identify the PCM consumer. All
retained PCM tuples are zero-valued, so payload equality is excluded.

`H-PhaseTransitionKey` and `H-TaskOrdinalKey` are not selected: no existing
task/DMA field remains stable through the VI-origin transition in both
captures. `H-GlobalSequenceOnly` is not promoted to a legitimate identity;
only broad event ordering remains. The bounded table therefore selects
`H-NoHandoffKey` at the current marker scope. This does not prove PCM absence,
image-DMA corruption, or authorize an output remap.

Sources: `scratch/agent/s2412_identity_join/image_retained/run.log` and
`scratch/agent/s2413_identity_join/image/run.log`.
