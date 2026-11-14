# NEXT (s7342): idiom-class audit - class S, host tables indexed by an address-derived value vs spill addresses
HYPOTHESIS-ID: host-addr-indexed-tables
Context: s7341 closed class P (top-byte tests; tools/s7341_topbyte_census.py, 0 default-on). The KSEG-literal classes are done
(R/M/N/O/P host, A-F game). A different failure shape remains: a host array/bitmap/vector indexed by `(addr & mask) >> k` or
`(addr - 0x80000000) >> k` and SIZED for 8 or 16 MB (e.g. per-4 KB page tags, per-word coverage bitsets, `[0x800000 >> 3]`). A spill
address (0x81000000-0x81800000, phys 0x01000000-0x017FFFFF) indexes past such a table: silent OOB read/write, not a reject.
Hypotheses: H-diag (every such table belongs to a gated probe), H-oob (a default-on table indexed by a live guest address can be
reached with a spill address: a real defect, fix by sizing to rs64_ram_top or bounds-checking), H-masked (indices pass through an
8/16 MB mask first, which class M/N already classified).
Method: new tools/s7342_addr_index_census.py on the s7338 HOST scope + gates. Enumerate (1) declarations of arrays / std::bitset /
std::vector / new[] whose size expression contains 0x800000, 0x1000000, 8 << 20, 16 << 20, RDRAM_SIZE-like names or `>> k` of
those; (2) subscripts `[ ... >> k ... ]` (k 2..23) and `.set(`/`.test(` with a shifted address. Join each subscript to its array's
declared size; class D/G/P/C as s7338, B = default-on and the index is a guest address with no bound <= size. Controls: plant a
default-on `static uint8_t tag[0x800000 >> 12]; tag[(a - 0x80000000u) >> 12] = 1;` ('?') and the same behind a log gate ('G').
Pre-grep (s7341): only fixed 0x1000/0x2000 DMEM/IMEM buffers matched a literal-size grep; subscripts go through locals, so the
join must follow `const uint32_t idx = ...;` locals (8-line window like s7341's VAR pass).
Runtime only if a B site exists: `env SECS=260 zsh scratch/s7326/run.zsh s7342_dd8 ''` with a selftest control at 0x81000100.
