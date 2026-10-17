# Classify remaining raw single-byte rdram[] reads
HYPOTHESIS-ID: raw-rdram-swizzle-audit
s5230 fixed 19 word reads (rs64_rdram_peek.h). Next: grep `rdram\[[^]]*\]` in src/main/{main,upstream_compat,rt64_render_context}.cpp,
classify each (needs ^3 / linear copy / already via MEM_B), fix with rs64_rdram_u8. Outcomes: any fix
that changes a logged value => re-check ledger claims citing it. Also re-read claims from the 19 fixed probes
(grep PORTING-STATE for m5-producer-input / m5-object-successor). Then M3 idiom audit if clean.
