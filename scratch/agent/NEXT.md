# NEXT work unit (s2490) — explain MEM_W versus explicit descriptor reads

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Add one phase-gated diagnostic to `rs64_m5_descriptor_yield` that prints, for
fields 0, 2, 4, 6, 10, 11, 12, and 14 in the same row: `MEM_W`, explicit
`memcpy` from `rdram + (guest - 0x80000000)`, the corresponding `TO_PTR` field
read, exact host offsets, and the guest address. Retain the raw-byte table and
scheduler-id positive control. Do not change task dispatch, audio behavior, or
any guard.

Before building, run the oracle whole-RDRAM positive control and verify the
byte-address formulas against `MEM_W`, `TO_PTR`, and the RDRAM-copy convention
in `librecomp/src/sp.cpp`. Build one Debug binary and run one qualified hangar
capture with the same boot-relative recipe as s2489.

## Competing hypotheses and discriminator

- H-MEMW-aliases-explicit: `MEM_W`, `memcpy`, and `TO_PTR` read the same host
  bytes. This predicts identical values for every selected field.
- H-MEMW-expands-differently: `MEM_W` resolves a different base or expression
  than the explicit read in this translation unit. This predicts `MEM_W` alone
  differs while explicit and `TO_PTR` agree.
- H-TO_PTR-layout-differs: the struct view uses a distinct layout/aliasing path.
  This predicts `MEM_W` and explicit reads agree while `TO_PTR` differs.

The discriminator is one same-run equality table with the scheduler-id control
and layout rows firing in the 512 / `0x6AB400` phase. Exact equality selects
the alias hypothesis; MEM_W-only disagreement selects the macro-expression
hypothesis; TO_PTR-only disagreement selects the struct-layout hypothesis.
The oracle remains a phase-independent positive control, not descriptor evidence.
