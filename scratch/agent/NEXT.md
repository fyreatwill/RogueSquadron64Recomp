# NEXT (s7364): idiom-class audit - class AO, heap/container buffers indexed by guest-derived values
HYPOTHESIS-ID: host-heapbuf-guest-index
Context: s7363 (class AN) closed host arrays of STATIC extent (tools/s7363_hostarr_census.py, gated in regen_replay.sh). It cannot see
buffers whose extent is a runtime value: std::vector<T> v; v[idx] / &v[idx] / v.data() + idx; new T[n]; calloc/malloc tables
(e.g. main.cpp g_s5229_val = calloc(0x800000) indexed by a guest address, g_s5229_pc/g_s5229_w); std::string s[idx]; memcpy(dst, &vec[off], len)
with a guest off/len. s7363 found one live instance by hand review: s7097 word_snap g_cur[(a & ~3) - g_glo] underflowed (FIXED).
Idiom (class AO): a subscript / pointer offset / memcpy range on a runtime-sized host buffer where the index or length is not provably
< size(): from guest RAM, ctx->rN, an RDP/RSP command word, a DMA length, an env var or a file.
Hypotheses: H-safe (every index checked against size()/the allocation constant or masked below it), H-trust (unchecked, but the producer
is range-limited, e.g. phys & 0x7FFFFF into an 8 MB table), H-hole (a guest value can exceed size(): heap overflow / OOB read - fix).
Method: tools/s7364_heapbuf_census.py: collect runtime-sized buffers (std::vector/std::string/std::deque members and locals, pointers
assigned from new[]/malloc/calloc/aligned_alloc/std::make_unique<T[]> with their allocation expression) in src/**, librecomp,
ultramodern, lib/rt64/src, and the --gen tree; per use classify SIZE-CHECKED (dominating idx < v.size() / < alloc const), MASK
(& M with M < alloc const), LOOP (i < v.size()), AT (.at()), B (rest). Reuse s7363's scoped-decl / guard_dominates / ubound helpers
(import the module). Planted control rows per class in --selftest (incl. a negative after-loop row and an unaligned-window row
modelled on word_snap). Verdict table like tools/s7363_hostarr_reviewed.tsv; reviews split by file across independent reviewers
given the code, not the conclusion. Second line: ASan two-arm harness for each real hole (tools/s7363_an_ctl.sh pattern).
Then the regression smoke: `env SECS=260 zsh scratch/s7326/run.zsh s7364_dd8 ''` + regen gate entry.
Leftovers noted by s7363 reviewers (fold into AO or fix in passing): funcs_13.c rs5834_who sentinel 2 indexes rs5834_n[2] if post runs
without pre (add `if (w > 1) return;` in its apply script); dpc_bridge.cpp:4116 (int)std::floor(xa) UB on huge xa; upstream_compat
s7318 bcmp ex[s.nex++] check-then-increment is unsynchronised (single guest thread today).
Exit: PORTING-STATE s7364, CURRENT-TRUTH 27zc -> closed, commit; any lib/ edit -> ./submodule-patches/export.sh first.
