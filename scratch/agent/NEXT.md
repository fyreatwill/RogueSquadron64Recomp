# NEXT (s7924)
HYPOTHESIS-ID: soak-verdict-freeze-field
s7923 made ring_stalls.py `max_vihold_ms` mean frozen holds only (title animation -> `max_animhold_ms`; owner rings 391-392 ms).
The loop's verdict line (tools/agent/soak_verdict_fields.sh) still only scores `vi_stalls30s` (>= 30 s), so a G5c-class freeze
(1-5 s, the owner's "buffering") in any future soak is invisible in SOAK-RESULTS.md.
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks this.
1. Read tools/agent/soak_verdict_fields.sh + test (tools/s7453_harness_death_test.zsh V/VN helpers). Add `freeze_arms=<n>`:
   arms whose tag line has max_vihold_ms >= 1000 (exact-key parse via tools/agent/summary_field.sh semantics; missing key ->
   counted in a `freeze_na=<n>` like stall_na). Do not change rc semantics.
2. Controls in the same harness test: fake ring with a 1.5 s frozen hold (gen frozen) -> freeze_arms=1; a 17 s animating hold
   (gen=$i advancing) -> freeze_arms=0; steady -> 0. Mutation: scorer without the animating rule -> the 17 s fake reads 1.
3. Re-score the s7919/s7921 rings through the verdict path: freeze_arms=0 expected (H-clean) vs 1 (H-hidden freeze).
