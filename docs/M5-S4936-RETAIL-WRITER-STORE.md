# M5 s4936 — retail writer store attribution

The retail oracle was run with a whole-RDRAM positive-control watch, three
targeted physical watches, the writer execution range, the exact writer
execution watch, and the independent type-2 task decoder. The first sampler
attempt retained the whole-RDRAM watch and slowed the emulator before mission
qualification; the corrected run used the three destination watches below and
allowed the positive-control watch to retire at 10,000 callbacks.

whole-RDRAM control: 67,289 writes; threshold reached and watch 0 removed
VI/emulation: 14,384 VI, 239.7 s emulated in 240.4 s wall
writer 0x80091784: 12,076 executions
store sampler: 19,773 phase hits, 17,199 unique rows, 0 overflow
type-2 decoder 0x80033FCC: 0/8192 rows, phase_hits=0

The range census identified four stores in the 0x80091600:0x80091840
neighborhood that were relevant to the writer. In all three 512-wide buckets,
their effective destinations were stable:

| store PC | instruction | effective destination | observed rows (hangar / mission 1 / mission 2) |
|---|---|---|---:|
| 0x800917C4 | sb | 0x80149702 | 516 / 979 / 873 |
| 0x80091698 | sh | 0x80149988 | 656 / 2231 / 2055 |
| 0x800916A4 | sh | 0x8014998A | 656 / 2231 / 2055 |
| 0x800917F4 | sw | 0x800A1778 | 657 / 2231 / 2055 |

The stores target auxiliary state/table locations, not an OSTask-shaped
publication. Together with the same-run type-2 decoder null and positive
controls, this selects H-auxiliary-store over H-task-store for the captured
route. This remains single-source retail evidence; no mitigation, filter, or
value rewrite is authorized.

Evidence: /tmp/rs64_s4936_retail_store_capture_exact.log.
