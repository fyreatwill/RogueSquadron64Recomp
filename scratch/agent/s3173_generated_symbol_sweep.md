# Session 3173 generated-symbol sweep

- Range: `0x80100000..0x80110000`
- Helper change: `static_4_801096D8` -> `data_gap_801096D8`
- Classification: invalid-data tail; the body is discarded shift/divide
  material with no callable prologue or independent companion symbol.
- Generated result: two `data_gap_801096D8` references; zero
  `static_4_801096D8` references in `funcs.h`, `funcs_49.c`, and
  `recomp_overlays.inl`.
- Companion census: no stale semantic function match in the range; all
  other selected records were synchronized or ambiguous/fake.
- Validation: source-only rename; no build or runtime run.
