# NEXT: G1c phase 2 - name what drains the 0x801163B0 node cache at dd3
HYPOTHESIS-ID: g1c-phase2-drawdist
s6087: both arms (arena/no-arena) SIGBUS at beginFrameDLChunk (guest NULL+4): cache head *(0x801163B0)==0 and findAndUnlinkSmallestEntry(0x8002221C) returned 0. Heap NULLs and arena are exonerated.
Hypotheses: H-drain (dd3 consumes cache nodes faster than reclaim returns them, e.g. per-frame DL chunks not reclaimed because of the s6070 ucode cap/truncation path), H-bucket (0x80128F00 bucket lists legitimately empty because heap blocks are exhausted in the guest's own sizing, not host heap), H-leak (a path at dd3 skips reclaimDisplayListChunk).
One build, one run (fixup script, not hand-edit): at 0x8002221C return log count of 0-returns plus per-VI counts of pops from 0x801163B0, calls to reclaimDisplayListChunk (0x80007CDC) and countDisplayListChunks result; run L1 px4 dd3 and dd1 in the SAME recipe family (phase-gated on VI), positive control = dd1 must show nonzero pops/reclaims.
Discriminator: pops-minus-reclaims grows monotonically at dd3 only -> H-leak/H-drain (find the missing reclaim); balanced but 0-returns still occur -> H-bucket.
Fallback fix if the drain is per-frame DL volume: guard the NULL (skip chunk) is a MITIGATION - needs ORIGIN line; prefer raising the guest pool supply.
