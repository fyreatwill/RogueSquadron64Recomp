# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e commit term: build the provenance-keyed upload hash cache (s6959 arm S), same-run timing
HYPOTHESIS-ID: g1e-dd4-rt64-texload
s6959: key = tile params + run-length tag walk; tagS = mix(load descriptor key, source-rows XXH3). Flight: 99.97% hit, 0 wrong, key 60 ns vs
hash 257 ns. Without the source hash 802 wrong in 105 s, so the source must be in the tag.
Unit (ONE build): ROGUESQ_G1E_PROVCACHE (=1 on, =tog 10 s blocks, =v verify: always hash, count wrong hits, mutant params-only arm must be wrong).
- Load side: reuse rs64ProvLoad's mask cache and tagS only (drop tagA, the srcchg table, and the scratch runs stay only on mask miss, 0.37%).
  Time the load-side cost per load (sampled 1/64) so the budget is measured, not assumed (~10 ms/s source hash expected).
- Hash side: in rs64MemoHash, on a PROVCACHE hit return the cached hash and skip TMEMHasher::hash. Table 4096 direct-mapped (maybe 2-way).
- Per-second [g1e-pcache]: mode, calls, hits, wrong (v), load-side ns, key ns.
Hypotheses: H-win (tog blocks: commit -0.15..-0.3 ms/task, >=8/11 pairs lower, wrong=0 in =v) vs H-load (source hash + tag stores eat the gain:
flat; then try RDRAM dirty-page tracking in place of the source hash) vs H-cachemiss (the table/tag arrays thrash L1 and the gain is smaller
than counted).
Runs: env OUT=scratch/s6960 zsh tools/g1e_xt_flight.zsh v 240 "ROGUESQ_G1E_PROVCACHE=v"; then ... t 240 "ROGUESQ_G1E_PROVCACHE=tog"
(pair the tog blocks with the existing [g1b] sd_wall / AQ commit fields as in s6957). Default only if wrong=0 and the gain holds.
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
