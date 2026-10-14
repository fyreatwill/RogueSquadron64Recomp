# M3 s4820 — unaligned / ll-sc / cache idiom census

Tool: `tools/census_unaligned.py` (static, single-source for reachability; runtime helpers read directly from `N64Recomp/include/recomp.h`).

| mnemonic | sites | where |
|---|---|---|
| lwl / lwr | 212 / 206 | 64 fns, real code; pairing audited s4705 (203 pairs, 12 orphans classified) |
| swl / swr | 208 / 206 | 65 fns, real code (struct-copy idiom) |
| ldl / ldr | 87 / 174 | only `__OSGlobalIntMask` (size 0x4E10, oversized data-decoded-as-code), `lvj_checkComplexObjectives` tail (dead, s4819), `audioCompandS16` (size 0x54, data) |
| sdl / sdr | 2 / 3 | `audioCompandS16`, `__OSGlobalIntMask` only; offsets like 0x5CFF/-0x6BBB = data |
| ll / lld / sc / scd | 191 / 4 / 8 / 10 | all lowered to `do_break`; every site is in `__OSGlobalIntMask`, `audioCompandS16`, `data_gap_*`, the `lvj_checkComplexObjectives` tail, the `filterVoiceSampleBlock` tail (s1970) or `static_3_*` data. No reachable ll/sc in real code. |
| cache | 212 | lowered to nothing. Real code uses op 0x0D (hit-writeback-invalidate-D) in resample*/copyVoice*/zeroAudioBufferWords/zmemcpy/convertMat3x4ToN64Mtx; the host has no cache model, so a no-op is exact. The rest are data symbols. |

Runtime helpers `do_lwl/lwr/swl/swr/ldl/ldr` reviewed: shift/mask arithmetic is correct for all misalignments (0-3, 0-7); shifts never reach the type width. Only deviation from hardware: lwl/lwr always sign-extend the merged 32-bit result, whereas MIPS64 keeps stale upper bits on partial merges. A completed pair gives the same value for any 32-bit consumer, and ldl/ldr (the 64-bit users) are live only in data.

Verdict: class closed, no guard needed. ORIGIN: no mitigation added; census tool + doc only.
