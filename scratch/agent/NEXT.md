# Map the surrounding voice/name span that produces `late`
HYPOTHESIS-ID: m5-audio-destub

The s4600 run passed the generated-store controls and found three phase-3
stores at physical `0x1724F4`, all from `rs_strncpy` (`0x80007670`) with
byte values `0x6C,0,0`. The later `0x6C617465` read at the bad caller was
not observed at that exact byte. Do not rerun the exact-byte census.

Competing hypotheses and the discriminator:

- H-span-rsstrncpy: the surrounding record/name span is populated by
  `rs_strncpy`; rows at offsets `0x34..0x37` show the `late` bytes and name
  the writer.
- H-span-other-guest: a different generated writer stores the `late` bytes
  elsewhere in the span before the bad caller; its PC/phase/value row names
  that writer.
- H-span-host: no generated store touches the `late` bytes in the span while
  the adjacent generated-store control fires; this leaves host/translation or
  an uninstrumented write as the boundary.

Discriminating measurement: one build and one qualified run with the
regeneration-preserved generated-store hook widened from exact physical
`0x1724F4` to `0x1724C0..0x17250B`. Emit a bounded first-row-per-phase/PC
table with offset, width, value, and phase; retain the entry and adjacent
positive controls. Any row containing `late` selects its PC-bearing guest
writer; lifetime absence with controls live selects the host/uninstrumented
boundary.

Before building, extend `tools/apply_s4598_complete_store_census.py` and the
host logger in `src/main/upstream_compat.cpp`; then run:

```sh
python3 tools/apply_s4598_complete_store_census.py
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run from `build/` with the qualified environment used in s4600:
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1
ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_S4299=1 ROGUESQ_LOG_S4597=1`, repeated Start
input, a SIGKILL watchdog, and capture under
`scratch/agent/s4601_port_run/`.
