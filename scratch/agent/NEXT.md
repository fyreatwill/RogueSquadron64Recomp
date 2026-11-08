# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: G1e commit term: provenance-keyed TMEM hash, feasibility census first
HYPOTHESIS-ID: g1e-dd4-rt64-texload
s6958: 99.8% of TMEM loads are descriptor+content repeats (sources static), but only 6.5% are noops: TMEM thrashes, so the s6942 generation
memo hits 0.34%. The hash (~30% of commit) and uploadTMEM XXH3 (inside uploadTexture ~32%) still read TMEM bytes every upload.
Idea: keep per TMEM 8-byte word (512 words) the provenance of its contents: (load descriptor key, word index within that load). Because
descriptor+content repeat is ~100%, the same provenance over a hashed span means the same bytes. Key the TMEMHasher result (and uploadTMEM's hash)
by (tile params, provenance of the span and TLUT span). A cheap key: store spans as run-length (one entry per load run), not per word.
Unit (ONE build): ROGUESQ_G1E_PROV=stat. Per hash call: compute the provenance key, look it up in a 4096 table, count hits, and on a hit compare
the cached hash with the real one (mismatch count must be 0; positive control: a mutant key without the word offset must mismatch). Also time
the key cost (mach_absolute_time sampled 1/64) against the hash cost. Also count source-changed loads (desc same, cont differs; s6958 0.2%).
These need RDRAM write tracking, or the provenance key must also take the source hash (too costly).
Hypotheses: H-prov (hit >80%, key <30% of hash cost: build the cache next, expect com -0.6..-1 ms) vs H-prov-cost (key costs as much as the hash:
drop the hash lever, profile uploadTexture's non-hash part instead) vs H-src (source changes under the same descriptor matter: a cache needs
page-dirty tracking first).
Run: env OUT=scratch/s6959 zsh tools/g1e_xt_flight.zsh r 240 "ROGUESQ_G1E_PROV=stat ROGUESQ_G1E_LOADREP=0"
If the XG49V (21:9, 144 Hz) is attached, its unit (git show c4755af1e:scratch/agent/NEXT.md) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
