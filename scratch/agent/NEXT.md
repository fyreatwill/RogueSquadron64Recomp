# NEXT: G1c - fold s6049_dd2t / s6049_dd3t (address-bounded span-table stores)
HYPOTHESIS-ID: g1c-draw-distance
Hypotheses: H-writers (7 unbounded span-table store sites; fix = address bound) vs H-other (another writer corrupts 0x80136DC4 / terrain table).
Discriminator: SOAK-RESULTS s6049_dd2t, dd3t + grep -a '[spanbound]' scratch/agent/m6/g1_lvl1g1cdd{2,3}t/run.log. rc=0 with skips => H-writers confirmed (two lines: lldb s6047 + soak). Still SIGBUS with tbl=0 and a spanbound skip count of 0 for the offending pc => H-other: lldb write-watch from rdram-derived host address (see s6047). Control: dd1b retail rc=0 0 skips (done).
Then: record distant-terrain fraction per step (gridlog) and bound the footprint upstream if skips are heavy.
