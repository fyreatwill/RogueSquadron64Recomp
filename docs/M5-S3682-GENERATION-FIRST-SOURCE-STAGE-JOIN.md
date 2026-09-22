# M5 s3682 — generation-first source/stage join

The prescribed s3682 runner was missing, so this iteration restored a
self-contained copy of the qualified s3681 oracle/port recipe, added the
generation-first matcher, rebuilt once, and ran one concurrent capture with
SIGKILL cleanup.

The retail arm registered the whole-RDRAM watch and all five descriptor/source
watches, emitted 909 type-2 task rows, and reached the target phases. The port
reached both target phases, passed its source-hook control, and emitted 1,024
source rows, 1,879 stage rows, 1,565 ABI rows, and 1,570 DMA rows. No crash or
abort marker appeared.

The matcher retained exact route/ordinal matches and then selected the newest
source record with the same nonzero task generation before the existing task
pointer and broad history fallbacks. It produced 442 generation-first stage
matches: 182 in title (1024/0x790400) and 260 in hangar (512/0x6AB400).
The remaining stage classifications were 2,046 pointer-history matches, 5
broad-history matches, and 10 unmatched rows. Generation-first rows logged
equal stage/source generations and source event before stage event.

This selects `H-SourceSameGeneration` for the class that can be joined by
generation and refutes treating all 240 s3681 source rows without same-generation
stage records as proven wrong-task input. It does not classify those source
rows source-centrically: a stage-first matcher can only report stages that
arrive, so the unmatched-source population and exact input-DMA ownership remain
open. The generation/order result is single-source port evidence; the retail
arm independently validates phase reachability and activity.

No guest value was skipped, rewritten, or guarded.
