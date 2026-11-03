# NEXT: G1e FPS60 integer constant-step accumulators (|K|>1) - triage the 41-site census
HYPOTHESIS-ID: g1e-fps60-int-step-quanta

Context: s6830 closed the float/tick rate classes (spline-craft death ramp fixed). The one idiom never enumerated is integer
load/addiu K/store with |K|>1 (s6821's g3_tick_counter_audit.py only takes +-1 followed by a test).
`python3 tools/g1e_int_step_audit.py` -> 41 sites / 25 functions (scratch/s6830/int_step_audit.txt).
Step 1 OFFLINE (no build): drop the non-time sites by reading them (heap/pointer strides rs_free/coalesceFreeHeapBlocks +16,
instantiateNamedMeshInstance +88, JFIF parser, inflateInit2_, sampleRgbBoxFilter, cloneCellBufferWithAlloc, setupMenuData).
Read the rest: tickTextureAnimSlots 0x80054E70 (-256), advanceNpcOnCurvedPath 0x8006C124 (+32), setupWalkerSpriteTileQuad
0x8005BC80 (+2), runPauseMenuStateMachine 0x800C3094/3534/3584 (-2), spawnCutsceneObjectsFromList 0x800A7E38 (-65), audio
(tickAudioChannel, stepActiveSongTracks, advanceSongRegion, updateSongTempoTickRate, tickAllActiveSongs, serviceStreamingVoice:
audio-clock driven? which thread calls them?). For each: is it reached per mission tick (runInMissionFrame graph) or per
frame/handler, and what consumes the field (visible animation phase? a count?).
Hypotheses per site: H-quantum-visible (per tick, visible: fix k=dt*30 on the step, rounded/accumulated for ints),
H-benign (not per tick, or a stride/count), H-audio (audio-clock driven: rate-independent by construction).
Step 2 (only if a candidate survives): one build adding the surviving pcs to ROGUESQ_TICK_TRACE (fixup_fps60_float_trace.py
int rows), arms a30 / FPS60 on the level that exercises it (lvl14 420 s recipe scratch/s6830/lvl14L.sh, or the s6829
front-end recipe for menu sites); per game s rate must double at FPS60 to count as a defect, and the fix arm must equal a30.
Done = every site classified with a reason; any fix verified with a same-build FQUANTA=0 control.
If nothing survives: G1e is closed; the backlog's remaining items are owner-judgement (G1d, G3c sheets). Then take
G5 renaming only per ITERATION item 4 rules, or a new owner report.
