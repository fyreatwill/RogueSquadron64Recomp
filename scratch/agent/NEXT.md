# Next: phase-gated RDRAM witness run (keyW/keyD/keyZ vs same-origin controls)
HYPOTHESIS-ID: m6-mission-input
H1: some words change only with stick/button input (real input state). H2: all keyW diffs are buffer-phase/animation artifacts.
Discriminator: edit s5069_mission_snap.sh so every snapshot (ctl and key) is triggered only when the latest origin= in run.log is 0x620400. Drop ctl3 and shorten sleeps so the whole run is under 540 s (harness caps background at 600 s; use run_in_background). Take ctlA, ctlB (same phase), keyW, ctlC, keyD, keyZ.
Analyze: python3 -I tools/snap_witness.py DIR keyW keyD keyZ (adapt the ctl names to ctlA/B/C). Input-state words = stable across ctls, changed in W hold, and D hold changes a different word set.
Outcomes: witnesses surviving phase-gating and differing between keyW and keyD => input-state words found (H1); none => H2.
