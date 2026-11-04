# NEXT: retail mission null for the N64Recomp self-branch block 8009264C..800934A4
HYPOTHESIS-ID: selfbranch-mission-null

Why: g3-optin-frame-diff closed s6877 (pitch = retail asin dead zone, no fix). CURRENT-TRUTH lists the silent miscompile as NOT fixed: 16 backward branches out of a function land on its own entry, in voice resampler helpers. Retail attract gave 0 hits, but the retail mission arm never reached flight, so there is no mission null. The g3_mission oracle route has since reached flight on every mission (s6753-s6778).
Hypotheses: H-dead (block never runs in flight, stays parked) / H-live (retail executes it during mission voice playback, so the port runs miscompiled code and it needs a real fix, design in PORTING-STATE s6871).
Measure, one run: retail oracle in lvl1 flight with in-mission dialogue, PC watch on 8009264C..800934A4. Same-run positive control: a PC watch on a voice path function known to run in flight must fire, or a null says nothing. Read tools/oracle/README.md and tools/g3_mission/run.sh first; use --save-dir, never swap the user .eep.
Outcomes: 0 hits with control firing -> H-dead for that mission, record it, repeat on one more dialogue heavy level at most. Any hit -> H-live, name the caller, fix per s6871.
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these. lvl10 cloud clock only on an owner report.
