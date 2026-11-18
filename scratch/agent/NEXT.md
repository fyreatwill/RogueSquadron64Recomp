# NEXT (s7611)
HYPOTHESIS-ID: host-snapshot-of-guest-data

Class OV closed s7610 (tools/s7610_ov_census.py --controls --witness <logs>: 54 host rows 0 open, 14240 generated direct
calls 0 cross-overlay, controls 6/6, witness PASS, H-clean).
Next idiom class SN: host-side SNAPSHOTS of guest DATA keyed by a guest address (or read once) with no content hash /
generation check, reused after the guest rewrites the source bytes (level change, overlay data swap, heap reuse, PI DMA).
Candidates: src/ statics that copy guest bytes once (`static bool done` + MEM_ reads; level/config tables, hangar camera
tables in rs64_s6907_aim, terrain/far tables s6963, fog tables s6904, draw-distance spill state), any host map whose VALUE
is guest-derived bytes keyed by guest address (texture/TLUT/DL caches in src/rsp, RT64 texture cache keyed by address +
hash check?), and caches invalidated only on boot.
First boring check: grep `static .* = MEM_|static bool .*(done|init|seen)` near MEM_W/MEM_H/MEM_B reads in src/.
Classify: re-read-per-use, hashed (content checked), invalidated-on-event (name the event and prove it fires on every
rewrite path), immutable-source (ROM / main code / never-rewritten table), diag-gated, BAD.
Hypotheses: H-clean, H-bad-gated, H-bad-live.
Tool tools/s7611_sn_census.py --controls: (1) plant a once-read static snapshot of a guest table used on a default path ->
OPEN; (2) drop a row -> OPEN; (3) remove an invalidation call -> OPEN; (4) plant an address-keyed map of guest bytes with
no hash -> OPEN. Second source: runtime witness from existing logs (level-change lines proving a source address is rewritten)
or a compiled witness.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
