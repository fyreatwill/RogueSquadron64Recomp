# Next work unit (s4358): repair M5 selector/decode consumer join

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4357 passed the retail whole-RDRAM control and reached title/hangar, but
the selected retail task/field join at `0x80033FCC` was empty. The port side
was live: 2,817 ABI rows and 2,812 DMA joins, with title 1024 at 13.7 s and
hangar 512 at 34.0 s and no crash/abort. Therefore the result is an
instrument-boundary failure, not a stream-origin result.

Competing hypotheses:

- H-selector-consumer: the repaired C904/C950 join matches the port's later
  consumer layout while the selected source remains equivalent.
- H-pre-filter-origin: the repaired retail source already differs before the
  selector/decode consumer, independently of the port aftermath.
- H-instrument-boundary: C904/C950 still cannot produce a phase-keyed row even
  though whole-RDRAM, VI, and execution controls fire.

Discriminating measurement: build one bounded phase-keyed table around the
existing retail C904/C950 execution witnesses, selected words, and the port
descriptor/consumer rows. Matching post-filter layout selects
H-selector-consumer; mismatch already in the pre-filter source selects
H-pre-filter-origin; absent C904/C950 rows despite the positive controls selects
H-instrument-boundary.

Exact pre-build ground-truth check: run the existing oracle whole-RDRAM
positive control plus C904/C950 execution watches first; do not add another
oracle field until those witnesses fire in the same title/hangar capture.
