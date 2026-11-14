# NEXT (s7345): idiom-class audit - class V, 32-bit multiply overflow in guest-derived sizes
HYPOTHESIS-ID: host-mul-overflow-sizes
Context: s7344 closed class U (tools/s7344_wrap_census.py: 343 `a + n <cmp> Z` sites, 0 open; rsp.hpp DMA length clamp made
subtractive, pi.cpp save_write_ptr/save_clear guarded). The sibling idiom: a size computed as a uint32 product of guest values
(`width * height * bpp`, `page_num * page_size`, `count * sizeof(T)`, `rows * stride`, `n << k`) wraps before the bound check or
allocation sees it, so a 64-bit or subtractive check downstream compares the wrapped (small) product while the loop uses the factors.
Hypotheses: H-safe (every product is computed in 64 bits, or its factors are masked/bounded so the product < 2^32),
H-diag (overflowing products only in gated probes), H-ovf (a default-on product of guest factors can wrap before a check or a
resize/new: real defect, fix with uint64_t math + reject log).
Method: new tools/s7345_mul_census.py on the s7344 scope; reuse s7344 classify()/CORE/HAND machinery and s7343 body_gated().
Sites: `X * Y` and `X << k` (k variable or >= 8) whose result feeds a comparison, a memcpy/loop bound, a resize/new/malloc, or an
index, within the same statement or via one local. Classes: K constant factors; W64 64-bit factor/cast/size_t; MSK factors masked
(<= 16 bits each, or bitfields); BND factors bounded earlier in the function (`w > N return`); G/D/P/C (CORE demotion as s7344);
B default-on guest factors, product can exceed 2^32 before use. Controls: plant `uint32_t n = task->w * task->h * 4; if (n > cap)
return; memcpy(..)` ('?'), the uint64 twin ('W64'), the masked twin (`w &= 0x3FF; h &= 0x3FF`, 'MSK'), a gated twin ('G').
Priority files: rt64 hle (framebuffer sizes, texture sizes, TMEM loads), librecomp pi.cpp/flash.cpp/eep.cpp, src/main capture paths.
Runtime only if a B site exists: build the fix + selftest, then `env SECS=260 zsh scratch/s7326/run.zsh s7345_dd8 ''`.
Exit: PORTING-STATE s7345, CURRENT-TRUTH item 27j -> closed/fixed, commit.
