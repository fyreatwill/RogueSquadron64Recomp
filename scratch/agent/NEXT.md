# NEXT (s7331): item 23 — scene-reset dangling-writer audit (idiom class: blocks the retail bulk free releases that something still writes)
HYPOTHESIS-ID: reset-dangling-writer
Context: s7330 closed item 22. The boot bulk free (coalesceFreeHeapBlocks after menuOverlayInit) released the mixer's command-list
buffers while the synth kept writing them for 4-7 tasks (CPU writes the command list, RSP writes voice state back). That is one
instance of a class: untagged (a1&0x80==0) blocks freed by the retail scene reset that a still-running subsystem (audio thread, RSP,
PI DMA, VI callbacks) keeps using. Enumerate the whole class once, instead of meeting members one crash at a time.
Hypotheses:
- H-audio-only: the mixer buffers are the only blocks written after a reset (class closes with 1 member, retail-shaped, harmless).
- H-more: other subsystems (sfx voices, streamed tiles, PI DMA targets, cutscene actors: cf. G5a junk pointer) write freed blocks too.
- H-reuse: some post-reset writer hits a block that has ALREADY been reallocated (real corruption, the dangerous form).
Discriminating measurement (ONE build, ONE run per route): at each rs64_s7325_heapsync, snapshot (hash per 64 B line) every block it
drops (ptr, req, owner); every VI for the next 2 s re-hash those not yet reallocated (host map) and record changed lines (block, offset,
first change ms); when a block is reallocated, stop tracking it but also record the first post-realloc write if the new owner differs.
Writers attributed coarsely by also hooking the s7324 audio DMA wr path (RSP) and PI DMA completion (pi) into the same block lookup; a
change with neither = CPU. Positive control: the boot class-1 buffers 0x80169F10/0x8016BD50/0x80171EB0 must show changed lines with
the RSP + CPU attribution (s7330 known writer). Negative control: a block dropped and never touched (most of the 17-176 per sync) shows 0.
Routes: forced L4 (scratch/agent/g1_level_coverage_common.zsh, LEVEL=4 HOLD_S=200, env ROGUESQ_S7317_ALLOCMAP=1 ROGUESQ_S7324_RCPREF=ctl)
and the hangar route with aborts (scratch/s7326/run.zsh) for mission resets. Watchdog: kill the game by pid, never `pkill -f` a string
that is in your own command line (s7330).
Outcome map: only the mixer buffers change -> H-audio-only, close; other blocks change before reuse -> H-more, name each writer;
any change after reallocation to a different owner -> H-reuse, root-cause that writer (fix candidate).
