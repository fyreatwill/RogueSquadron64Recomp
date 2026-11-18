# NEXT (s7600)
HYPOTHESIS-ID: guest-indexed-host-array-census

Class GR closed s7599 (406 container receivers, 0 open, controls 3/3); AZ-1 folded (0 clamps on L1/L4 flight).

Class GX = fixed-size host arrays/tables (C arrays, std::array, vectors sized once) subscripted by a value derived from guest
data (RDP/RSP command fields, guest RAM words, DMA/VI registers, OSMesg ids, thread priorities, event ids) with no mask, clamp
or range check before the subscript -> an out-of-bounds host read/write (silent corruption, not a crash, so soaks miss it).
Scope: src/, librecomp/src, ultramodern/src, lib/rt64/src (skip gui/tests/tools). Enumerate `name[expr]` where name is a
fixed-size array/table and expr is not a literal/loop counter; per site: array size, index source, the mask/clamp/check that
bounds it (named), or gated diagnostic.
Hypotheses: H-masked (every guest-derived index is masked by its field width <= array size, e.g. tile & 7, segment >> 24 & 0xF),
H-oob (some index field is wider than the table, e.g. a 4-bit field into an 8-entry table, or a guest RAM word used raw),
H-gated (only diagnostics index raw).
Tool: tools/s7600_gx_census.py --controls (plant `tbl[rdram_word]` into a copy of rt64_rdp.cpp + drop a row; both must be OPEN).
Runtime witness for any H-oob row: an ASan/UBSan bounds arm (build_ub exists, s7584/LU) on L1/L4 dd4 for that site, old vs fixed.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
