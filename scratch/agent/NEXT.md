# NEXT (s7421)
HYPOTHESIS-ID: regen-verify-drift

Class CD (CURRENT-TRUTH Next steps item 1). s7420 got tools/regen_verify.sh to complete; compare is 2664 same / 114 differ /
18 live-only / 3 regen-only vs the s6881 baseline 2684/82/17/1 (scratch/s7420/regen_compare.json; baseline in
docs/REGEN-VERIFY.md / scratch/s6864/cmp2.json).
1. Diff the differing-name set against the baseline: list the NEW differing/one-sided functions (~32+).
2. For each, diff the live vs regen C of that function (both trees are left by regen_verify; see the script header) and
   classify: EXPECTED-ENVDIAG (env-gated diag/obs chain not in RS64_REPLAY), EXPECTED-SIZE (func_sizes.txt / data_gap),
   EXPECTED-CODEGEN (same statements, different layout), or LOST (a live hand edit absent from every fixup/apply script).
3. Each LOST: move it into a fixup (regen order), re-run regen_verify, show it now matches.
Hypotheses: H-mirrored (0 LOST) vs H-lost (>=1). Control: plant a one-line hand edit in a live funcs copy of one function and
show the classifier calls it LOST.
