# NEXT (s7336): idiom-class audit - host-owned arenas vs the guest memory layout
HYPOTHESIS-ID: host-arena-layout-audit
Context: s7335 closed the guest side (fb-layout bound consumers, H-clean) and found one host overlap: the DLPOOLX DL-chunk arena could
start below the guest top 0x80000000|osMemSize (fixed: rs64_s7335_dlpool_cap). The same class may hold other members: every host
allocator that hands out guest addresses picks its range from its own env (SPILL_HI/SPILL_MB, DLPOOLX_MB, BIGARENA, s6127 fl, RT64
writeback/aux buffers, RAMTOP guards) with no shared layout table.
Hypotheses: H-clean (no other pair overlaps under any accepted env value), H-pair (two host arenas overlap each other at some combo,
e.g. spill 0x81000000+SPILL_MB 16 past RAMTOP 24, or BIGARENA vs spill), H-guest (another arena can start below the guest top).
Method (static first): grep src/main + src/rsp + tools/apply_*.py for every host-chosen guest address base (0x808/0x80C/0x810/0x818
literals, rs64_*_base functions); tabulate [base, end) as a function of each env and its clamp range; check pairwise and vs the guest
top over the accepted env range (script: tools/s7336_host_arena_table.py, exit 1 on any overlap). Then ONE build adding a startup
`[s7336] layout` line printing every arena actually chosen; positive control = an env combo the table says overlaps must print OVERLAP.
Outcomes: no overlap -> H-clean, close; overlap -> clamp at the source like s7335 and verify with def / clamped / clamp-off arms
(scratch/s7335/run.zsh pattern, L1 dd8 21:9, 90 s hold).
