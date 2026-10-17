# Session 5265 — `osWritebackDCacheAll`

The bounded helper was run over exactly `0x80035930..0x80035980` and made zero
edits, classifying `osWritebackDCacheAll` as already synchronized.

Independent checks found `osWritebackDCacheAll = 0x80035930` marked
`defined:true` in `rogue_squadron64/symbol_files/libultra.txt`. The generated
tree contains its ABI declaration in `funcs.h`, a zero-size overlay record in
`recomp_overlays.inl`, and two direct calls from `funcs_3.c` and `funcs_5.c`.
There is no generated function body or placeholder at the companion address;
the implementation is supplied by the host libultra wrapper. This is a
mechanically registered ABI entry, not a safe generated-symbol rename or a
data-fragment candidate. Preserve the ABI name; no build or soak was needed.

Next candidate: `_Putfld = 0x80035960`.
