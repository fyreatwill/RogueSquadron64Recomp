# NEXT: what fills the game thread's 133-150 ms OS-silent stretch inside each scene-transition stall?
HYPOTHESIS-ID: transition-stall-silent-stretch
Context (s7064): L6 dd1 4:3 FPS60 transition gaps 201-335 ms (15 per 362 s run). The audio-slot drain wait inside is only
25-66 ms (2-4 synth frames, ROGUESQ_S7064 ring); other guest threads keep 17 ms cadence; the game thread (TL slot 8) makes no
OS mesg call for 133-150 ms per gap, quantized at 8 or 9 VIs. Recipe: scratch/s7064/run.zsh <name> 6 (ROGUESQ_S7064 + G1E_TL).
Hypotheses:
 H-vispin: the game busy-polls a VI-updated variable (frame counter / fade timer written by the retrace thread) for N frames
   outside OS calls -> retail-identical timed wait (feel only). Fingerprint: stretch length = integer VIs exactly; one hot loop PC.
 H-compute: text glyph / menu / mission-end build (rasterizeFormatMessageGlyphs, buildDebrisMeshFromCells, menuOverlayInit)
   that happens to take ~140 ms host time -> ours to speed up (host cost, retail would be faster/slower?).
 H-tokenwait: the game host thread is blocked on the ultramodern run token / a host lock (not a guest OS call), e.g. RT64
   or a host-side load -> ours.
Discriminator, ONE run: host `sample <pid> 1 1` triggered by a watcher at each slot-wait episode start (tail sw_*.txt for 'B '),
or an ultramodern-side per-gap guest PC census of the game thread; split samples in the stretch into on-CPU compute (which
function), spin (one loop), and blocked (psynch/mutex). Positive control: a known compute burst (title glyph build, s6808)
must show as rasterizeFormatMessageGlyphs.
Outcome map: one VI-polling loop -> H-vispin (close as retail feel, owner note); named heavy compute -> H-compute (profile/fix);
blocked in a host lock -> H-tokenwait (fix the holder).
Hard rules: diagnostics in generated code go through tools/fixup_*.py / apply scripts; one game run at a time; SIGKILL.
