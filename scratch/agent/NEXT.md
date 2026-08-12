# NEXT work unit (consume overlay-12 splice soak)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s739 landed the resident-0C splice and queued `s739_ovl12_splice.sh`.
This iteration only consumes that soak. Do not rebuild or resplice.

## Competing hypotheses

- **H-splice-correct:** live `[ovl-route] res=0x0C` plus the CLIP positive
  control (`res=0x04`) and zero active reset/reuse rows in the section-2
  latch.
- **H-ovl12-return-incomplete:** OVL12 `0x1DB0` is entered, then
  `[clip-stray]`, a route-specific `UnhandledJumpTarget`, or `ovl12_ret=0`
  after a live `tgt=0x1DB0`.
- **H-reset-independent:** live OVL12 markers with retained active
  reset/reuse rows (main-image `L_1DB0` still fires, or a new predecessor
  such as resident `0x24` from `OVL12_1FCC → L_1268`).

## Discriminating measurement

Same-run CLIP `[ovl-route] res=0x04` must fire or the zero-reset result is
an unqualified null. Then:

- CLIP live + OVL12 live + sec2 `active=0` and `unpaired_reuse=0` →
  H-splice-correct.
- CLIP live + OVL12 `tgt=0x1DB0` then stray/UJ/`ovl12_ret=0` →
  H-ovl12-return-incomplete.
- CLIP live + OVL12 live + retained sec2 reset/reuse → H-reset-independent.

## Commands

    # After the loop moves the recipe to soak_queue/done/:
    LOG=$(ls -1t scratch/agent/soak_results/s739_ovl12_splice_*/run.log | head -1)
    grep -c '\[ovl-route\].*res=0x04' "$LOG"
    grep -c '\[ovl-route\].*res=0x0C' "$LOG"
    grep -c '\[e9-prov-reset\].*scope=sec2' "$LOG"
    grep '\[e9-prov-reset\].*scope=sec2' "$LOG" | awk '
      {reset+=($0 ~ /reset=[1-9]/); act+=($0 ~ /active=[1-9]/); ur+=($0 ~ /unpaired_reuse=[1-9]/); n++}
      END {print "sec2_rows",n,"reset_nonzero",reset,"active_nonzero",act,"unpaired_nonzero",ur}'
    grep -c '\[clip-stray\]' "$LOG"
    grep -c '\[CRASH\]' "$LOG"
