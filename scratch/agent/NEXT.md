# NEXT (s7959)
HYPOTHESIS-ID: post-preset-class-ladder
s7958 closed class FW (owner-state file writers; audio_device.txt now temp+fsync+rename, gate S7958_FW in ARGS + EXTRA_GATES).
Default-on file growth is ALREADY covered by tools/s7430_file_growth.py (s7430) and config precedence by s7428: do not redo them.
Register any new non-*_census.py gate in EXTRA_GATES in the same commit; an src/ edit needs the FULL sweep (s7958 caught 3 REDs
that `--only` missed: s7384 static-state, s7428 precedence, s7430 growth all pin exact source text).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Ladder 3c: first non-closed rung not needing the owner's look, or a NEW host idiom-class audit that commits a guard/proof.
   Candidate class RD (host file READERS of owner-state on a partial/empty file): audio_device.txt empty -> "default" route
   (system output) rather than the built-in default; controls.json empty/truncated -> defaults kept? save .bak fallback only when
   the main file fails to OPEN (an existing short file is read as-is?). Hypotheses H-fallback (each reader treats empty/short as
   absent and falls back to the backup/built-in default) vs H-trust (a short file is read as real data). Discriminator: plant
   empty, 1-byte-short and zero-filled copies through each real reader in a unit harness (pi.cpp save load with a .bak beside it;
   audio_route_load_pref; rs64_bindings_json) and log what value each yields. Never touch build/saves (copy into a temp dir).
