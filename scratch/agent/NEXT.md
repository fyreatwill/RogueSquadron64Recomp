# NEXT: remove the dead s4563 check through the now-working regen path, then fold the regen dd4 soak
HYPOTHESIS-ID: s4563-dead-code-removal

Why: s6862 found the s4563 stale-head skip dead (covered by s4786 PAUSE=4); s6863 deferred removal until regen worked. It closed s6864.
First: read SOAK-RESULTS for s6864_regen_fps60_dd4_lvl5. Fail on regen but not on live = a real difference the compare missed: reopen replay-patch-presence and stop.
Unit: drop apply_s4563_stale_head_skip.py from the replay list and remove its text from live funcs (default off, env-gated). Rebuild live. tools/regen_replay.sh + tools/regen_verify.sh must then show no new differing function (baseline 75, docs/REGEN-VERIFY.md).
Hypotheses: H-dead (s4563 never fires: removal changes no default-path function) / H-live (some default path reads g_s4563_blk_freed).
Discriminator: per-function compare before vs after removal; only functions holding s4563 text may differ, and only by the gated block. lvl1 120 s hold after.
Outcomes: H-dead -> commit. H-live -> keep it and record the reader.
Ask owner when a human is next on: add tools/regen_replay.sh + regen_verify.sh to the CLAUDE.md regen order (owner file, not edited).
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
