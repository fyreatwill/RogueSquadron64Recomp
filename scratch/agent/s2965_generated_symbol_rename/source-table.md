# Session 2965 source table — `0x800BCC38`

| Evidence | Result |
| --- | --- |
| Candidate after the parked `0x800B89F4` fragment | `0x800BCC38` |
| Project symbol map | `data_gap_800BCC38`, size `0x8`; `playerT16Init` begins at `0x800BCC40` |
| Companion mission-overlay map | `data_gap_800BCC38 = 0x800BCC38`; comment says the real function is `playerT16Init` |
| Predecessor boundary | `playerTieInterceptorUpdate` starts at `0x800BC810`, size `0x428`, ending at `0x800BCC38` |
| Generated body | Two instructions: `bc1f L_800BCC6C` at `0x800BCC38` and delay-slot `nop` at `0x800BCC3C`; unresolved cross-function branch lowers to a trap |
| Successor body | `playerT16Init` has its own stack-frame prologue at `0x800BCC40` (`addiu sp, sp, -0x50`) |
| Generated callers | No calls or independent references to `fake_func_800BCC38`, `func_800BCC38`, or `data_gap_800BCC38`; callers target `playerT16Init` at `0x800BCC40` |
| Companion semantic source | No callable companion source for `0x800BCC38`; only the explicit data-gap record and successor name |
| Regeneration tables before this iteration | `rename_generated_symbols.py` and project maps used `data_gap_800BCC38`; `build_redefs.py` alone still appended the stale `playerT16InitPreamble` override |

## Classification

`0x800BCC38` is a mechanically proven non-callable data/fixup gap, not a
standalone function or callable preamble. The project/generated name
`data_gap_800BCC38` is retained and the stale redefinition to
`playerT16InitPreamble` is removed.
