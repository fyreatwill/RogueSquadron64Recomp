# Next work unit (s4384): qualify actual hangar writer PCs

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-hangar-selector-writer: the actual hangar range-1 writer PCs carry the
  selector/decode payload and can be joined to task publication.
- H-hangar-maintenance: actual hangar range-1 traffic is maintenance unrelated
  to the task payload.
- H-hangar-value-watch-gap: the retained writer set is incomplete or its
  scalar/value watch cannot validate the relevant stores.

Discriminating measurement: from the qualified s4383 hangar
`ordinal-writer-join` rows, add the highest-volume actual hangar range-1 PCs to
`--post-value-pc` and rerun the same 75-second oracle. After-publication rows
from those PCs with live scalar validation select H-hangar-selector-writer;
live rows with no task-payload correspondence select H-hangar-maintenance;
missing/unsupported scalar rows select H-hangar-value-watch-gap. Require the
whole-RDRAM positive control, all three buckets, at least 1,000 valid type-2
rows, zero ordinal overflow, and `mismatch=0` for every retained scalar row.

Ground-truth preflight: use the independent retail oracle and preserve every
s4383 physical watch and phase schedule. Extract candidates with:

    rg 'ordinal-writer-join phase=0x006ab400:512 .*watch=1' scratch/agent/s4383_m5_writer_task_join_full/oracle.log | sort

Then create one self-contained runner from
`scratch/agent/run_s4383_m5_writer_task_join.sh`, changing only
`--post-value-pc` to include the selected hangar PCs, and run it after:

    bash tools/oracle/build.sh

Do not repeat the caller census, first-eight comparison, or C904 range.
