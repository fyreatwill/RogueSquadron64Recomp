# NEXT (s7363): idiom-class audit - class AN, host fixed-size arrays indexed by guest-derived values
HYPOTHESIS-ID: host-array-guest-index
Context: s7361 (class AL) and s7362 (class AM) closed every route from a guest value to a host pointer through rdram:
MEM_x sext bases stay in the 4 GB reservation, raw `rdram + X` sites are contained/checked (tools/s7362_rdramraw_census.py,
gated in regen_replay.sh). The remaining route is the host's OWN arrays: `static T buf[N]; buf[idx]` where idx comes from guest
RAM, a ctx->rN register, an RDP/RSP command word or a DMA length (e.g. upstream_compat `s_s6093_cnt[w & 7]`, funcs_24 `bkt[bi]`,
dpc_bridge per-tile/per-slot tables, rt64 tile/TMEM tables fed from RDP commands, rsp.cpp shadow buffers).
Idiom (class AN): `name[expr]` / `name + expr` on a host array of static extent N, where expr is not provably in [0, N).
Hypotheses: H-safe (every index masked `& (N-1)`, clamped, or a bounded loop counter), H-trust (unchecked but the producer is
range-limited by the ucode/RDP format: e.g. a 3-bit tile field into an 8-entry table), H-hole (a guest value can index past N:
host stack/BSS corruption - fix with a mask or bound).
Method: tools/s7363_hostarr_census.py: collect host arrays with constant extent (declarations `T name[N]` / std::array<T,N>) in
src/**, librecomp, ultramodern, the --gen tree, and lib/rt64/src (RDP-command-indexed tables); per subscript classify
MASK (& M, M < N), LOOP (for-counter bounded by N or a smaller constant), FIELD (bitfield extract (x >> s) & m with m < N),
CHECKED (dominating `< N` compare on the same name in the function), B (rest). Planted control rows per class (--selftest).
Second line: for each B, a fork/ASan two-arm harness like tools/s7362_rawneg_ctl.sh (pre overflows, post bounded).
Then the regression smoke: `env SECS=260 zsh scratch/s7326/run.zsh s7363_dd8 ''`.
Exit: PORTING-STATE s7363, CURRENT-TRUTH 27zb -> closed, commit; any lib/ edit -> ./submodule-patches/export.sh first.
