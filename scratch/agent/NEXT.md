# NEXT (s7960)
HYPOTHESIS-ID: post-preset-class-ladder
s7959 closed class RD (owner-state file readers): audio_device.txt empty/NUL/junk now = absent -> built-in default
(src/main/rs64_owner_text.h, gate S7959_RD in ARGS + EXTRA_GATES); controls.json already rejects every partial file; save
loader already falls back to a whole .bak on a short file (s7429). Do not redo FW (s7958), RD (s7959), growth (s7430),
precedence (s7428). An src/ edit needs the FULL sweep (`python3 tools/s7651_gate_sweep.py --jobs 2`), not only `--only`.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Ladder 3c: first non-closed rung not needing the owner's look, or a NEW host idiom-class audit that commits a guard/proof.
   Candidate class EV (host env-var numeric parsing): every getenv(...) fed to atoi/atof/strtol in src/main + librecomp.
   H-clamp (each parse rejects junk / out-of-range and falls back to the documented default) vs H-raw (atoi("abc")=0 or a
   huge/negative value reaches a size, divisor or array index). Discriminator: grep-enumerate every site, then a harness
   feeding "", "abc", "-1", "1e9", "nan" through each parse helper; any site where a junk value changes behaviour away from
   the default (or divides by it / indexes with it) is a defect. Check first whether a prior class already covers this
   (`grep -n 'env' docs/CURRENT-TRUTH.md`, s7427 env_policy_order, s7425 build options) before starting.
