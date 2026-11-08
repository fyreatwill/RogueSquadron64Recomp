# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: see git show HEAD~1:scratch/agent/NEXT.md, and CURRENT-TRUTH).

# NEXT: fold the s6948_skyz_sel2_confirm soak, then take the next G5/G1e item
HYPOTHESIS-ID: g5h-skyz-sel-miss
s6948: SEL's extra 1.8% misses were H-interleave (mode 0F0A4004, no z read, between sky depth and sky mode). SEL2 (default inside DD_SKYZ, =0 gives SEL) gives 1.78% unrewritten vs value 1.84%, leak 0/230. Single run.
1. Read SOAK-RESULTS for s6948_skyz_sel2_confirm (log scratch/agent/soak_results/, audit scratch/s6948/aud_c1.txt; python3 tools/g5h_skyz_audit.py). Pass: live sel2 miss% within 0.3 of val, selMode/selDrawPz/selEnd 0, sel2 oth_rw 0 with oth_ring > 0, crash 0. Pass -> label SEL2 two-source in CURRENT-TRUTH and close g5h-skyz-sel-miss. Fail -> read the "# why" lines (mode that decided) and fix skyish2.
2. If the soak has not run yet, do not wait: take the paused g1e-present-drain unit (git show HEAD~1:scratch/agent/NEXT.md, second half) or an owner report if one arrived.
Defaults: SKYZ opt-in, owner decides.
Rules learned (s6948): a consumer test must decide at the first draw that reads prim z, not at the first mode word.
Scripts: scratch/s6948/leak_nocap.zsh <tag> <dd> "<env>" (368 s, no capture). Older notes and the full owner question list: git show HEAD~1:scratch/agent/NEXT.md.
