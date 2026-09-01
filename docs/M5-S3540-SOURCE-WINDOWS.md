# M5 session 3540 — exact image-task source-window ordering

## Work unit

Phase-qualified RSP DMEM stores and post-copy RDRAM-to-DMEM DMAs now emit
exact post-event FNV/nonzero summaries for window 2 (`0x6F0..0x9F0`) and
window 3 (`0xCB0..0xE48`), with a shared bounded event ordinal. The run used
the real-audio LLE/spin-yield/autopilot route and existing task, stage, and PCM
controls.

## Result

The build succeeded. Source-window, stage, stage-byte, and PCM controls all
fired. The run reached title VI 1024 at phase 4 but did not reach 512 hangar
before the 50-second capture ended, so this is title-phase evidence only.

Window 2 became nonzero at event 26 (`post_nz=332`), later returned to the
all-zero hash `F59C39C5` at event 113, became nonzero again at event 492, and
returned to zero at event 581. A post-copy DMA from RDRAM `0x178C80` into
`dmem=0x6F0`, `len=0x100` also produced the zero state (event 842); a later
DMA from `0x1E2FC0` refilled it (`post_nz=396`, event 843). Window 3 stayed
zero with hash `762B22A5` throughout the target phase.

Stage 2 consumed the zero `0x6F0..0x9F0` source and produced zero destination
and PCM payloads while stage and completion joins remained live.

## Selection

`H-SourceWindowOverwritten` is selected for the title-phase port path: a
window was nonzero and a later DMA/store sequence restored zero before stage
consumption. The exact RDRAM writer that made source `0x178C80` zero remains
open. This is single-source port evidence for the ordering, paired with the
independent retail result from session 3539 that the corresponding source/state
ranges contain legitimate nonzero data. No audio or output state was changed.

