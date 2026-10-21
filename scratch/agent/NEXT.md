# NEXT: fold s5763_slotwatch_kill (forced death via ROGUESQ_FORCEKILL_MS=60000)
Read SOAK-RESULTS.md s5763 line + scratch/agent/m6/s5763_slotwatch_lvsel/run.log: need `[forcekill]` lines, and lldb_att*.log wp4 (0x130B10) hit with lives decrement = positive control. If control absent -> void, check death path (cur at 0x137E7C vs the game's actual health word).
Then bt of wp2 (0x137F24) writes setting 0x8/0x10 after the kill.
Outcomes: slot writer is the death handler = slot state is death-driven (H1); only init writes = objective/stale (H2/H3).
HYPOTHESIS-ID: g1-nonhealth-fail
