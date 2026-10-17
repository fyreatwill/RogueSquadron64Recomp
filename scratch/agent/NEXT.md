# Next: m6-mission-input is closed (s5081). Priority list otherwise exhausted per CURRENT-TRUTH line 14 (s5066).
HYPOTHESIS-ID: m6-mission-input-closed
Result s5081: 0x80138458 = player-vehicle effect object; +0x50 = Y of position vec3; stick-gated writer is updateEffectObjectOrientationQuat.
Unit: pick the next target from CURRENT-TRUTH Next steps; if none is actionable, go BLOCKED asking the owner for a target (see scratch/agent/BLOCKED.md).
Tools available: tools/s5081_wr_windows.py, tools/s5081_pc_to_func.py, scratch/agent/s5080_watch.sh (keyed mission run with census).
Note: after touching RecompiledFuncs, `touch src/main/register_overlays.cpp` before cmake.
