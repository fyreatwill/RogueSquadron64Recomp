# NEXT: G1c per-cell cost — which branch of getGridCellValueAt (0x80048508) costs its 96-120 ns/call at dd6
HYPOTHESIS-ID: g1c-dd-headroom
Context (s7023, ROGUESQ_S7022_ST=1 + tools/apply_s7023_calleetime.py, L1 dd6 21:9 WIDEWIN tog3 8192/10240, owner path):
loop 1.52/1.83 ms; getGridCellValueAt 41-48% (96-120 ns/call, ~6000-7800 calls/frame), processGridCellByDistance 12-14%, self 40-45%
(call-path inline 74-81 ns/cell). 75-78% of cells take the call path; skipmix refuted. Ceiling of any fix here ~0.7 ms/frame.
G5i: fixed, owner look only — check CURRENT-TRUTH item 1 first.
getGridCellValueAt branches (read from funcs): (B1) out of range -> jal 0x80048948 (clampGridCellLookup? behind s6963 cellidx);
(B2) table 0x80136DC0+8 entry has 0x8000 flag and a2!=0 -> direct table 0x80136FCC lookup (cheap); (B3) else 0x80136DC0 table + node list
via 0x80137A5C (+0x22A) walk.
Hypotheses: H-walk (B3 node walk dominates: host-index it like s6963); H-clamp (B1 fallback dominates even with cellidx); H-flat
(cost is spread, ~100 ns = recomp ctx traffic of a ~60-instruction function: then inline/host-reimplement the whole function with a
same-run tog exactness check, the s6963 CHECK pattern).
Discriminator, ONE build, ONE run (scratch/s7023/run.zsh recipe, rename to s7024): patch getGridCellValueAt with per-branch counts and
mach time per branch (enter -> return), print [s7024-gv] per cap bucket. Outcome: one branch >60% of gv time -> H-walk or H-clamp;
else H-flat. Then build the fix with a ROGUESQ_*=tog same-run A/B and a CHECK arm (retail answer vs new answer, 0 mismatches + flipped
positive control) in the same iteration.
