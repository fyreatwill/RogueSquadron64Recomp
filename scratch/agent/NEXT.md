# NEXT (s7958)
HYPOTHESIS-ID: post-preset-class-ladder
s7957 fixed RT64 PresetLibrary::load (gate S7957_PL, registered in EXTRA_GATES). Register any new non-*_census.py gate in EXTRA_GATES in the same commit.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Ladder 3c: first non-closed rung not needing the owner's look, or a NEW host idiom-class audit that commits a guard/proof.
   Candidate: host file WRITERS in the game (ofstream/fopen "w" sites in src/ and lib/rt64/src: RT64 PresetLibrary::save, user
   config write, rs64 logs/dumps) - hypotheses H-safe (write failure reported, no partial file replaces a good one) vs H-clobber
   (truncate-then-write leaves an empty/partial file on a full disk or killed process, e.g. a settings or controls.json written in
   place). Discriminator: enumerate every write site, classify in-place vs temp+rename; plant a read-only dir / SIGKILL mid-write
   on any owner-data writer (controls.json, settings) and check the old file survives. Never touch build/saves.
