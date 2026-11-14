# NEXT (s7333): item 24 remainder — close the two carve-registration gaps so the FIFO reads host-live in every transition
HYPOTHESIS-ID: hostmap-carve-blind
Context: s7332 named the carve header writer (coalesceFreeHeapBlocks, H-carve) and landed carve registration at heapsync. FIFO-in-carve
transitions read host-live 14-15/18-20 per abort-route run (scratch/s7332/r3..r5_lines.txt). Two gaps:
(a) the carve-start host entry vanishes between heapsyncs while the guest header still says fl=6 + full size (80989000 after sync 1,
    8081E800 after sync 7). r5 kept the side map alive across an owner overwrite and the count did not move, so the erase path leads.
(b) 5-6 FIFO transitions/run sit at guest 0:0: the FIFO is above the arena top (80986800 = arena end 809867F0 + 0x10; 80904000).
Hypotheses for (a): H-free (a guest rs_free of the carve start: upstream_compat.cpp:3401 erase; guest then re-takes it without the
hook), H-malloc (the flags&4 rs_malloc returns the carve start with req << guest size and the s7317 insert replaces the entry; the side
map should cover that, but check the fallback runs: s7318_blk vs rs64_s7325_gap's live test), H-rebuild (rs64_s7325_heaprebuild /
s7326 spill release erase it; check line 4460).
Discriminating measurement (ONE build, ONE run, scratch/s7332/run_abort5.zsh recipe): log every s_s7317_live erase/replace of a
carve-tagged key or a s_s7332_carve key, with the call path (free / malloc / rebuild / sync) and guest header at that moment; plus, for
(b), log the arena top and the FIFO's distance to it at each `[s7332] fifo` line. Outcome map: erase path names the gap -> keep the
carve entry when the guest header is still fl&6 at that address (re-check in the erase path) and rerun: target 100% host-live for
in-heap FIFO transitions; (b) -> register [arena top, top of RDRAM used by the FIFO/fb] as an 'above-heap carve' at heapsync.
Report: python3 tools/s7331_reset_writer_report.py <log> --s7330 <log>; take ITS rc. Note the tmp+rename dump change (s7332) is
built but not yet run-validated: check rs64_s7331.log.tmp is gone and the log parses cleanly after the run.
