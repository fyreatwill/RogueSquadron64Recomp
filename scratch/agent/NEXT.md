# NEXT: fold s5693_htab_{a,b} (handle-table registration/fire census)
Hypotheses: H-reg lvf_initializeObjectTracking never runs / sayWhoaHim never registered (no [hreg] h=0x80108388); H-arm registered but condition never satisfied (hreg present, [hent] shows entry active, no [hfire] for it); H-disp checkObjectiveHandles not reached / dispatch never fires any handler (no [hchk] or no [hfire] at all); H-legit retail also never fires it.
Discriminator: grep -c '\[hreg\]\|\[hchk\]\|\[hent\]\|\[hfire\]' scratch/agent/soak_results/s5693_htab_*.log; look for h=0x80108388 in each tag. Controls: any [hreg] line; any [hfire] of another handler.
If H-arm: decode the entry's b4..b7/w8 (bool id, expected, count idx, threshold) and compare against bool array 0x80138xxx / count array in the same run; then oracle-compare. If H-reg: find who calls lvf_initializeObjectTracking (level table) and why not.
HYPOTHESIS-ID: g1-bool7-voice-path
