# Next work unit (s4357): M5 selector/decode consumer boundary

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4356 qualified both audio arms on the corrected AUTOPILOT/LLE route.
Both reached title 1024 at 15.0 s and hangar 512 at 24.2 s. The first hangar
audio-task sequence was 1064 for `factor5_ucode_b` and 1056 for `musyx_stub`;
enqueue/consume pairing makes that a four-task difference. The lifetime row
cap prevents an exact t=18–28 count, so rate divergence is not selected.

Competing hypotheses:

- H-selector-consumer: the qualified pre-filter selector/decode stream reaches
  a consumer whose later layout/value/order differs between arms.
- H-pre-filter-origin: the divergence is introduced before the selector/filter
  boundary and the selected consumer is only an aftermath.
- H-instrument-boundary: the existing retail/port join cannot produce a
  phase-keyed source-to-consumer row, so no new boundary is identified.

Discriminating measurement: use one bounded phase-keyed table joining the
existing retail C904/C950 witness fields to selected words and port
descriptor/consumer rows, with both source arms in the same build. Matching
post-filter layout selects H-selector-consumer; mismatch already in the
pre-filter source selects H-pre-filter-origin; absent phase, retail
whole-RDRAM, or port task controls selects H-instrument-boundary.

Exact pre-build ground-truth check: retain the oracle whole-RDRAM positive
control and existing retail task watch at `0x80033FCC`; do not add a new
oracle field until the existing source/consumer table is assembled.
