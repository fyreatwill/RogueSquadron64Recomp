# Re-check ledger claims built on the 45 fixed swizzle-bug probe readers
HYPOTHESIS-ID: raw-rdram-swizzle-audit
s5231 fixed 26 more unswizzled byte reads (main.cpp 20 lines, upstream_compat 6). Next: grep PORTING-STATE for
m5-dma-source / m5-descriptor-layout / route-state / entry_2c claims; pick the cheapest soak that emits them, run once,
compare logged FNV/nonzero to the ledger. Outcome: values change => list refuted claims in CURRENT-TRUTH superseded;
values same (word-aligned ranges) => close the thread. Then M5 audio de-stubbing (docs/M5-AUDIO-PLAN.md) or M3 idiom audit.
