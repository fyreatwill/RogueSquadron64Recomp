# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

OPEN DEPENDENCY (human, NOT to be retried by iterations): RSPRecomp is not in the headless
allowlist (denied s4741, s4742, s4744, s4745). Do NOT run it. The 0x2C splice (fixup 6r draft at
scratch/agent/fixup6r_draft.py, toml factor5_rsp_ovl2c.toml) resumes only when a human adds
the allow rules (see scratch/agent/UNBLOCK.md) and removes this paragraph.

Work unit that does not need it (s4746 follow-up): always-on per-task counter of arrivals at
DMEM 0x153==0x2C (do_indirect_jump into 0x1DB0 with d153==0x2C), plus per-task fetches, printed
per phase-7 task in one `[dlwalk-2c]` line (not ring-limited, not capped by the 80k ovl-route budget).
Run: `zsh scratch/agent/s4746_run.sh` after one build (cmake with DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer).
Hypotheses: H-2C-with-objects (normal 3.0-3.5k-fetch phase-7 tasks show 0 arrivals, runaway >0 and
count grows with mission time); H-2C-always (normal tasks also arrive, so 0x2C is not the
object-spawn marker); H-2C-phase3-only-alias (phase 3 runaways differ in shape from phase 7).
Positive control: phase-3 runaway tasks (14) must show >0; phase 4/5 normal tasks must show 0.
