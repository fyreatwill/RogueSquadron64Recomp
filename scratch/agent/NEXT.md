# NEXT (s7365): idiom-class audit - class AP, references / pointers / iterators / indices held across a container mutation
HYPOTHESIS-ID: host-container-invalidation
Context: s7364 (class AO) closed subscripts on runtime-sized buffers and found a DEFAULT-PATH RT64 defect of a different shape: an
index (drawCall.tileIndex) saved against one container state and used after Workload::begin() cleared it (4773/8192 frames in the
WLRESET=0 arm). The AO census sees only the subscript, not the stale lifetime. Class AP is that lifetime idiom:
  auto &x = v[i]; / T* p = v.data(); / auto it = v.begin(); / size_t idx = v.size()  ...  v.push_back / emplace_back / resize /
  insert / erase / clear / assign / reserve / swap / = (or a call that does one)  ...  use of x / p / it / idx.
Also members holding an index into ANOTHER object's container that is reset elsewhere (the FULLSYNC shape): RT64 State/RSP/RDP
members named *Index / *Cursor / *Start / *Count vs the Workload/DrawData vectors cleared in Workload::begin()/reset().
Hypotheses: H-safe (no mutation between capture and use, or the capture is refreshed), H-trust (mutation cannot reallocate: reserve
dominates / capacity proven), H-hole (use after an invalidating mutation - fix).
Method: tools/s7365_invalidation_census.py: per function, capture sites (& of a subscript/front/back/data(), iterator from begin/find/
end, index = size()) for every container s7364 collects (import tools/s7364_heapbuf_census.py collect()); then any mutation of the
same container (direct, or via a call to a same-file function that mutates it - one level) between capture and a later use of the
captured name. Rows: NOMUT / REFRESHED / RESERVED / B. Separately list every member index field whose container is cleared in a
reset/begin function and not reset with it (the s7364 shape), for lib/rt64/src/hle + src/rsp + librecomp.
Planted selftest rows (ref then push_back then use = B; ref, reserve(n) dominating, push within n = RESERVED; iterator across erase).
Independent reviewers per file group (given code + rows, not conclusions), verdict TSV like s7364_heapbuf_reviewed.tsv, ASan two-arm
(tools/s7364_ao_ctl.sh pattern) per real hole, regen gate entry, smoke `env SECS=260 zsh scratch/s7326/run.zsh s7365_dd8 ''`.
Side question from s7364 (one experiment, same session if cheap): what did the stale tile DRAW? The first draw after FULLSYNC used a
4-workload-old tile. Same dd8 recipe, presented-frame captures WLRESET=0 vs default, phase-gated on the same VI ordinals; if frames
differ, compare against angrylion (tools/oracle) to see which matches retail.
Leftovers (HOLE-OPEN, s7364): RT64 RSP vertex-cache indices[] across workloads (HLE only, LLE_FORCE=0): guard drawIndexedTri/
modifyVertex `globalIndex < vertexCount()`; mods duplicate dependency names; rt64_filesystem_zip source range; preset_light [-1].
Exit: PORTING-STATE s7365, CURRENT-TRUTH 27zd -> closed, commit; any lib/ edit -> ./submodule-patches/export.sh first.
