# NEXT: scene-transition stalls (200-320 ms) — retail audio wait or our slot-drain cadence?
HYPOTHESIS-ID: transition-stall-audio-wait
Context: 21:9 dd6 survey closed s7063 (19 levels ~60 fps). The remaining in-run gaps are 200-320 ms stalls at scene
transitions on L6/L7/L16/L17 (also dd1 4:3, s7059). One xctrace (single-source) put 209/298 game-thread samples in
isAudioSlotActive/anyAudioSlotActive polling under menuOverlayInit / endMissionCleanup / cinematicLoopBody.
s6809 already fixed one variant (preempt point in anyAudioSlotActive so the audio thread can reap). G5c bar excludes
loads, so this is a fidelity/feel question, not a G5c failure.
Hypotheses:
 H-retail: the slots are genuinely busy (a sound still playing out); retail waits the same time. Fingerprint: slot
   stays active for ~= the remaining sample count / 32 kHz of the voice it carries; reap happens on the first audio
   frame after the voice ends.
 H-cadence: the voice ended long before, but our audio thread reaps/clears the slot only on a coarse host cadence
   (AI buffer drain, host callback size) or is starved while the game spins. Fingerprint: slot-end-of-data timestamp
   to slot-idle timestamp >> one audio frame (~5 ms at 60 Hz task rate).
 H-preempt-residual: the s6809 preempt point is not reached on this path (a different spin site / isAudioSlotActive
   called directly), so the audio thread is blocked behind the run token. Fingerprint: zero audio-task runs during the
   stall window.
Discriminator, ONE build, ONE run (L6 dd1 4:3 FPS60, scratch/s7059/run_dd1.zsh recipe, ~15 stalls per run):
 per stall (game thread inside anyAudioSlotActive > 50 ms): which slot ids are active, per slot the voice's
 end-of-data time (sample cursor hits end), the time the slot goes idle, and audio-task count / AI pushes inside the
 window. Ring buffer dumped at exit, no per-frame stderr. Positive control: a forced long voice (or the title music
 slot) must show active-until-end with end->idle < 10 ms.
Outcome map: end->idle small and active time = real remaining audio -> H-retail (close as retail, owner note);
 end->idle large -> H-cadence (fix the reap cadence); no audio tasks in window -> H-preempt-residual (extend
 tools/fixup_preempt_point.py to the missing site).
Hard rules: diagnostics in generated code go through tools/fixup_*.py; one game run at a time; SIGKILL.
