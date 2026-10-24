# NEXT: why do all LUT entries stay age 0 at dd3? (G1c phase 2)
HYPOTHESIS-ID: g1c-phase2-drawdist
Facts (s6092): full scan at finder call 59: 6815 entries / 8192 buckets, age0=6808, 7 odd. +8 = age (tick +1 up to 0x708 then frees; reset zeroes; finder picks largest nonzero age).
Hypotheses: H-notick tickTextureMaterialExpiry not running/starved at dd3; H-allreset every entry touched (reset) each frame since per-frame texture working set >= table; H-reader the 7 nonzero + 8192 base differ from game's view.
Discriminator, one build: counters (per VI) for tickTextureMaterialExpiry calls, resetMaterialExpiryById calls, finder calls/zero returns, and entry count; dd1 control vs dd3 in one recipe pair. Wrap in funcs_6.c via tools/apply_s6088_bucketlog.py style patch (idempotent, env gated).
Run: copy scratch/agent/soak_queue/done/s6091_lutx4_dd3.sh with new tag, dd1 and dd3.

STATUS s6093: counters built; soaks s6093_cnt_dd1/dd3 queued. Next: read SOAK-RESULTS + soak_results logs, grep '[bucketlog] s6093' (compare tickcalls/resetcalls growth between consecutive dumps, dd1 vs dd3), pick hypothesis per outcomes above.
